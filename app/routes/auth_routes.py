from fastapi import APIRouter, Depends, HTTPException, status
from dependencies import get_user_service, get_auth_service
from schemas import CreateUserRequest, UserOut, LoginResponse, LoginRequest
from services import UserService, AuthService

auth_router = APIRouter()

@auth_router.post("/auth", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: CreateUserRequest, service: UserService = Depends(get_user_service)):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, service: AuthService = Depends(get_auth_service)):
    try:
        token = service.login_user(credentials)
        return LoginResponse(
            message="Login was succesful",
            token=token,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )