from fastapi import FastAPI
from routes import auth_router, project_router, document_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(document_router)


