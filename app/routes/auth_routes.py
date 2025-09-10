import logging
from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_user_service, get_auth_service
from schemas import CreateUserRequest, UserOut, LoginResponse, LoginRequest
from services import UserService, AuthService

auth_router = APIRouter(tags=["Auth"])
logger = logging.getLogger("app")

@auth_router.post("/auth", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest, service: UserService = Depends(get_user_service)):
    logger.info(f"User with username {user.username} requested to register.")
    try:
        user = service.register_user(user)
        logger.info(f"User with username {user.username} has been successfully registered with id {user.id}.")
        return user
    except ValueError as e:
        logger.warning(f"User with username {user.username} registration failed. Reason: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, service: AuthService = Depends(get_auth_service)):
    logger.info(f"User with username {credentials.username} requested to login.")
    try:
        token = service.login_user(credentials)
        logger.info(f"User with username {credentials.username} has been successfully logged in.")
        return LoginResponse(
            message="Login was succesful",
            token=token,
        )
    except ValueError as e:
        logger.warning(f"User with username {credentials.username} failed to log in. Reason {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )