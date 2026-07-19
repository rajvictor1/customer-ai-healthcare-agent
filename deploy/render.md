# Deploy to Render

1. Fork or connect repo https://github.com/rajvictor1/customer-ai-healthcare-agent on Render.
2. Create a new **Web Service**.
3. Set start command:
   ```
   uvicorn run:app --host 0.0.0.0 --port 10000
   ```
4. Add environment variables from `.env.example` in the Render dashboard.
5. Add a **Persistent Disk** mounted at `/app/data` for the SQLite database, or switch `DATABASE_URL` to a managed PostgreSQL instance.
6. Deploy.

> **Note:** SQLite is ephemeral on Render unless you attach a persistent disk. For production use, replace SQLite with PostgreSQL.
