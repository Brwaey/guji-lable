# API路由包
from .files import router as files_router
from .similarity import router as similarity_router
from .annotations import router as annotations_router

__all__ = [
    "files_router",
    "similarity_router",
    "annotations_router",
]