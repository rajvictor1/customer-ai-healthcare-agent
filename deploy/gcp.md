# Deploy to GCP Cloud Run
# 1. Build image: gcloud builds submit --tag gcr.io/PROJECT/customer-ai-agent
# 2. Deploy: gcloud run deploy customer-ai-agent --image gcr.io/PROJECT/customer-ai-agent
# 3. Set env vars / secrets in Secret Manager
