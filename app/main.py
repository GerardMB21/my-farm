from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from app.modules.auth.router import router as auth_router

app = FastAPI(title="my-farm")
app.include_router(auth_router)


@app.get("/docs-scalar", include_in_schema=False)
async def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.get("/health")
async def health():
    return {"status": "ok"}
