from fastapi import FastAPI
from . import routes

app = FastAPI(title="FlowOpsAI Backend")

# include API routes
app.include_router(routes.router)

@app.get("/")
def root():
    return {"message": "Welcome to FlowOpsAI backend!"}
