from dataclasses import asdict
from typing import Any
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import (
    APIRouter,
    Request,
    HTTPException
)

from main_app.src.application.dto import (
    LoginDto, 
    OkxWebSocketConfigDTO,
    UserSignupDTO
)
from main_app.src.application.interactors import (
    GetOkxListnerConfigsInteractor,
    GetUserInteractor,
    LoginInteractor,
    SaveOkxListnerConfigInteractor,
    SignupInteractor
)
from main_app.src.controllers.schemas import (
    OkxWebSocketConfigRequest, 
    UserLoginRequest,
    UserSignupRequest
)
from main_app.src.application.exceptions import (
    InvalidPasswordException,
    UserAlreadyExistsError, 
    UserGetManyConnections, 
    UserNotFoundException
) 



router = APIRouter()

class UserRoutes:
    @router.post("/login/")
    @inject
    async def login(
        self, 
        request_body: UserLoginRequest,
        request: FromDishka[Request],
        interactor: FromDishka[LoginInteractor]
    ) -> dict[str, str]:
        dto = LoginDto(**request_body.model_dump())
        try:
            user_id = await interactor(dto)
        except UserNotFoundException as e:
            raise HTTPException(status_code=404, detail="User not found") from e
        except InvalidPasswordException as e:
            raise HTTPException(status_code=401, detail="Invalid password") from e
        request.session["user_id"] = user_id
        return {"message": "Logged in successfully"}

    @router.get("/logout/")
    @inject
    async def logout(
        self, 
        request: FromDishka[Request],
    ) -> dict[str, str]:
        request.session.clear()
        return {"message": "Logged out successfully"}

    @router.post("/signup")
    @inject
    async def create_user(
        request_body: UserSignupRequest,
        interactor: FromDishka[SignupInteractor]
    ) -> dict[str, int|str]:
        dto = UserSignupDTO(**request_body.model_dump())
        try:
            user = await interactor(dto)
        except UserAlreadyExistsError as e:
            raise HTTPException(
                status_code=409, 
                detail="User with this username already exists."
            )
        return {"id": user.id, "username": user.username}


    @router.get("/me/")
    @inject
    async def get_current_user(
        self, 
        request: FromDishka[Request],
        interactor: FromDishka[GetUserInteractor]
    ) -> dict[str, int | str]:
        user_id: int | None = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        try:
            user = await interactor(user_id)
        except UserNotFoundException as e:
            raise HTTPException(status_code=404, detail="User not found") from e
        return {"id": user.id, "username": user.username}

    @router.post("/listners/okx/config")
    @inject
    async def save_okx_listner_config(
        self,  
        request_body: OkxWebSocketConfigRequest,
        request: FromDishka[Request],
        interactor: FromDishka[SaveOkxListnerConfigInteractor]
    ) -> dict[str, str]:
        user_id = request.session.get("user_id")
        if not user_id or type(user_id) is not int:
            raise HTTPException(
                status_code=401, 
                detail="Not authenticated"
            )
        try:
            config_dict = request_body.model_dump()
            config_dict["user_id"] = user_id
            dto = OkxWebSocketConfigDTO(**config_dict)
            await interactor(dto)
        except UserGetManyConnections as e:
            raise HTTPException(
                status_code=409, 
                detail="""
                    User can only have 2 WebSocket 
                    connections in this category.
                """
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail="Internal server error"
            ) from e
        return {"message": "Secrets stored securely"}

    @router.get("listners/okx/config")
    @inject
    async def get_user_okx_listner_config(
        self, 
        request: FromDishka[Request],
        interactor: FromDishka[GetOkxListnerConfigsInteractor]
    ) -> list[dict[str, Any]]:
        user_id = request.session.get("user_id")
        if not user_id or type(user_id) is not int:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated"
            )
        configs = await interactor(user_id)
        return [asdict(config) for config in configs]
