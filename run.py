from fastapi import FastAPI

app = FastAPI(title="Customer-Facing AI Agent MVP")

from app.main import app as main_app

app = main_app
