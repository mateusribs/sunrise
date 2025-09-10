from fastapi import FastAPI

from src.interfaces.http.controllers import auth_controller, mood_controller, user_controller

app = FastAPI(title='Sunrise API')

app.include_router(user_controller.router)
app.include_router(auth_controller.router)
app.include_router(mood_controller.router)
