from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.signup import signup_router
from routes.verify_email import email_router
from routes.login import login_router
from routes.forgot_password import forgot_password_router
from routes.tasks import task_router
from routes.taskupdate import task_update_router
from routes.profile import profile_router
from routes.export import export_router
from routes.user_stats import user_stats_router
from routes.manage_users import admin_router
from routes.get_user import users_router
from routes.search import search_router
from routes.cron_reminder import cron_router
import os
ENV = os.getenv("ENV", "production")
if ENV == "local":
    from utils.scheduler import start_scheduler
app = FastAPI(
    title="ToDo List API",
    description="A backend for an advanced ToDo List app",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://app-todopro.netlify.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(signup_router)
app.include_router(email_router)
app.include_router(login_router)
app.include_router(forgot_password_router)
app.include_router(users_router)
app.include_router(user_stats_router)
app.include_router(task_router)
app.include_router(task_update_router)
app.include_router(profile_router)
app.include_router(export_router)
app.include_router(admin_router)
app.include_router(search_router)
app.include_router(cron_router)

if ENV == "local":
    @app.on_event("startup")
    async def startup_event():
        start_scheduler()
   
@app.get("/")
def read_root():
    return {"message": "Welcome to the ToDo List API"}



