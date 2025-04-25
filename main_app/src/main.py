from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from main_app.src.controllers.routes.auth_routes import router as auth_router
from main_app.src.controllers.routes.users_routes import router as users_router
from main_app.src.controllers.routes.secrets_routes import router as secrets_router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
app.include_router(secrets_router, prefix="/secrets")
