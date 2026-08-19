"""Aggregated package for the lumi_messenger routes (refactored from a single God file)."""
from fastapi import APIRouter
from ._common import *  # noqa: F401,F403  (re-export shared symbols e.g. SUPPORTED_LANGUAGES)
from . import core as _core
from . import dm_domain as _dm_domain
from . import admin as _admin
from . import voice as _voice
from . import ws as _ws
from . import ai_agent as _ai_agent

router = APIRouter(prefix='/lumi', tags=['LUMI Messenger'])
router.include_router(_core.router)
router.include_router(_ai_agent.router)
router.include_router(_dm_domain.router)
router.include_router(_admin.router)
router.include_router(_voice.router)
router.include_router(_ws.router)
