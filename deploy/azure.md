# Deploy to Azure

## Azure Container Apps (recommended)

1. Build and push the image to Azure Container Registry:
   ```bash
   az acr build --registry MYREGISTRY --image customer-ai-healthcare-agent .
   ```

2. Deploy to Container Apps:
   ```bash
   az containerapp create \
     --name customer-ai-healthcare-agent \
     --resource-group MYRG \
     --environment MYENV \
     --image MYREGISTRY.azurecr.io/customer-ai-healthcare-agent \
     --target-port 8000 \
     --ingress external
   ```

3. Store secrets in Azure Key Vault and reference them via Container Apps secrets:
   ```bash
   az containerapp secret set --name customer-ai-healthcare-agent --resource-group MYRG --secrets OPENAI_API_KEY=...
   ```

4. Use Azure Database for PostgreSQL for production persistence. SQLite is ephemeral in Container Apps and should not be used in production.

## Compliance note

For healthcare workloads, ensure Microsoft BAA is in place and enable diagnostic logging before enabling PHI integrations.
