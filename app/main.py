from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from xml.sax.saxutils import escape as xml_escape

from app.chains import run_chain, set_llm
from app.providers import build_llm


# Load env variables from .env if present (development convenience)
load_dotenv()

PROVIDER = (os.getenv("PROVIDER") or "").strip().lower()
BRAND = os.getenv("BRAND", "MiMarca")


# Initialize LLM once at import/startup
try:
    _llm = build_llm()
    set_llm(_llm)
except Exception:
    _llm = None


app = FastAPI()


@app.get("/")
async def root():
    return {"ok": True, "provider": PROVIDER, "brand": BRAND}


@app.get("/ping")
async def ping():
    return "pong"


@app.post("/webhook/twilio")
async def webhook_twilio(request: Request):
    form = await request.form()
    body = form.get("Body") or ""
    # from_number = form.get("From")  # Not used at the moment

    reply = run_chain(body, BRAND)
    xml = (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{xml_escape(reply)}</Message></Response>"
    )
    return Response(content=xml, media_type="application/xml")


@app.get("/webhook/meta")
async def meta_verify(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
    if (
        hub_mode == "subscribe"
        and hub_verify_token
        and verify_token
        and hub_verify_token == verify_token
    ):
        return PlainTextResponse(hub_challenge or "")
    return Response(status_code=403, content="Forbidden")


@app.post("/webhook/meta")
async def meta_webhook(request: Request):
    data = await request.json()

    try:
        entry = (data.get("entry") or [])[0]
        change = (entry.get("changes") or [])[0]
        value = change.get("value") or {}
        messages = value.get("messages") or []
    except Exception:
        messages = []

    if not messages:
        return PlainTextResponse("")

    message = messages[0]
    from_number = message.get("from")
    text = (message.get("text") or {}).get("body") or ""

    reply = run_chain(text, BRAND)

    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

    if not token or not phone_number_id:
        return JSONResponse({"status": "acknowledged_without_send"})

    url = f"https://graph.facebook.com/v20.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": from_number,
        "text": {"body": reply},
    }

    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(url, headers=headers, json=payload)

    return JSONResponse({"status": "sent"})


