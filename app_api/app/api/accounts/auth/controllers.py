"""Authentication controller module."""

from typing import Annotated, Any

from litestar import Controller, Request, Response, post
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK

from .dtos import Login, LoginDTO
from .services import AuthService, provide_auth_service


class AuthController(Controller):
    """
    Authentication controller handling login and logout operations.

    Provides endpoints for user authentication using username/password
    credentials and JWT token management.
    """

    path = "/auth"
    tags = ["accounts / auth"]

    @post(
        "/login",
        dto=LoginDTO,
        dependencies={"auth_service": Provide(provide_auth_service)},
    )
    async def login(
        self,
        request: Request,
        data: Annotated[Login, Body(media_type=RequestEncodingType.URL_ENCODED)],
        auth_service: AuthService,
    ) -> Response[Any]:
        """
        Authenticate user with username and password.

        Validates user credentials, updates last login timestamp, and returns
        a JWT token for authenticated access.
        """
        user = await auth_service.authenticate_user(data.username, data.password)
        if not user:
            raise HTTPException(detail="Invalid username or password", status_code=401)

        oauth2_auth = request.app.state.oauth2_auth
        return oauth2_auth.login(
            identifier=str(user.id),
            response_status_code=HTTP_200_OK,
            token_extras={"name": user.fullname, "email": user.email or ""},
        )

    @post("/logout")
    async def logout(self) -> Response[None]:
        """
        Log out the current user by clearing the authentication token.
        """
        response = Response(content=None, status_code=HTTP_200_OK)
        response.delete_cookie("token")

        return response
