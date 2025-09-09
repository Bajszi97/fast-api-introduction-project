from .auth_routes import auth_router
from .project_routes import project_router
from .document_routes import document_router

__all__ = ["auth_router", "project_router", "document_router"]