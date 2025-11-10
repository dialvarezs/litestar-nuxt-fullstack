from litestar import Router

from .auth.controllers import AuthController
from .permissions.controllers import PermissionController
from .roles.controllers import RoleController
from .users.controllers import UserController

accounts_router = Router(
    path="/accounts",
    route_handlers=[UserController, RoleController, PermissionController, AuthController],
)
