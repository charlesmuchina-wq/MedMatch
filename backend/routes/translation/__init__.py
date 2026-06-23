"""Aggregated package for the translation routes (refactored from a single God file)."""
from fastapi import APIRouter
from ._common import *  # noqa: F401,F403  (re-export shared symbols e.g. SUPPORTED_LANGUAGES)
from . import core as _core
from . import analytics as _analytics
from . import memory as _memory
from . import quality as _quality

router = APIRouter(prefix='/translate', tags=['Translation'])
router.include_router(_core.router)
router.include_router(_analytics.router)
router.include_router(_memory.router)
router.include_router(_quality.router)
