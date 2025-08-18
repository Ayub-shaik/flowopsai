from fastapi import FastAPI
from server import routes  # absolute import within package

app = FastAPI(title="FlowOpsAI Backend")

# include API routes
app.include_router(routes.router)


@app.get("/")
def root():
    return {"message": "Welcome to FlowOpsAI backend!"}
