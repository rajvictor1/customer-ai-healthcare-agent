# Deploy to Fly.io

1. Install flyctl:
   ```bash
   brew install flyctl   # macOS
   ```

2. Launch the app:
   ```bash
   fly launch --now
   ```

3. Set secrets:
   ```bash
   fly secrets set SECRET_KEY="$(openssl rand -hex 32)"
   fly secrets set OPENAI_API_KEY=sk-...
   fly secrets set TWILIO_ACCOUNT_SID=...
   fly secrets set TWILIO_AUTH_TOKEN=...
   fly secrets set TWILIO_WHATSAPP_NUMBER=...
   ```

4. Create a persistent volume for SQLite, or use a managed PostgreSQL database for production.

5. Deploy:
   ```bash
   fly deploy
   ```

> **Note:** SQLite is ephemeral on Fly.io unless you create a `fly volumes` mount at `/app/data`. For production, switch to PostgreSQL.
