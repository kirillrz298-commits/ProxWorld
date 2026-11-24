from .common import router as common_router
from .categories import router as categories_router
from .ai_dialog import router as ai_dialog_router
from .tickets import router as tickets_router
from .admin import router as admin_router

all_routers = [
    common_router,
    categories_router,
    ai_dialog_router,
    tickets_router,
    admin_router
]

