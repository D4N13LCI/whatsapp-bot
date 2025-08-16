# whatsapp-bot

Webhook de FastAPI para WhatsApp usando LangChain. Permite elegir proveedor LLM entre Gemini y OpenAI mediante variables de entorno.

## Estructura

- app/
  - main.py
  - chains.py
  - providers.py
- requirements.txt
- Dockerfile
- .env.example
- README.md

## Requisitos

- Python 3.11+

## Pasos rápidos (local)

1. Crear y activar entorno virtual
   - Windows (PowerShell):
     ```powershell
     cd whatsapp-bot
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     cd whatsapp-bot
     python3 -m venv .venv
     source .venv/bin/activate
     ```
2. Instalar dependencias
   ```bash
   pip install -r requirements.txt
   ```
3. Copiar variables de entorno y completar claves
   ```bash
   cp .env.example .env
   # Edita .env y añade tus claves
   ```
4. Ejecutar servidor de desarrollo
   ```bash
   uvicorn app.main:app --reload
   ```
5. Probar endpoints
   - GET `/` → estado
   - GET `/ping` → `pong`

## Selección de proveedor LLM

- Establece `PROVIDER=gemini` o `PROVIDER=openai` en `.env`.
- Gemini: `GOOGLE_API_KEY` y opcional `GEMINI_MODEL` (default: `gemini-2.0-flash`).
- OpenAI: `OPENAI_API_KEY` y opcional `OPENAI_MODEL` (default: `gpt-4o-mini`).
- Temperatura por defecto: `0.4` (puedes sobrescribir con `TEMPERATURE`).

## Webhook Twilio (sandbox o número propio)

- Configura en Twilio el webhook de WhatsApp para `POST https://<tu-host>/webhook/twilio`.
- Twilio enviará `application/x-www-form-urlencoded` con campos como `Body` y `From`.
- La respuesta es TwiML con el mensaje generado por el LLM.

## Webhook Meta (WhatsApp Cloud API)

- Verificación (GET):
  - Configura en Meta la URL: `https://<tu-host>/webhook/meta`.
  - Durante la verificación, Meta llama con `hub.mode=subscribe`, `hub.verify_token`, `hub.challenge`.
  - Define `WHATSAPP_VERIFY_TOKEN` en `.env` y usa el mismo token en la app de Meta.
- Recepción (POST):
  - La app procesa `messages[0]` y obtiene `from` y `text.body`.
  - Responde al usuario vía `POST https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages` con `WHATSAPP_TOKEN`.

## Despliegue en Cloud Run (gcloud)

1. Construir e implementar
   ```bash
   gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/whatsapp-bot
   gcloud run deploy whatsapp-bot \
     --image gcr.io/$(gcloud config get-value project)/whatsapp-bot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8080
   ```
2. Configurar variables de entorno en Cloud Run
   - `PROVIDER`, `GOOGLE_API_KEY` o `OPENAI_API_KEY`
   - `GEMINI_MODEL` o `OPENAI_MODEL` (opcional)
   - `BRAND`
   - `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN`

## Notas

- En local, el archivo `.env` se carga automáticamente si existe.
- Para exponer el servidor local a Twilio/Meta usa `ngrok` o similar:
  ```bash
  ngrok http 8000
  ```
