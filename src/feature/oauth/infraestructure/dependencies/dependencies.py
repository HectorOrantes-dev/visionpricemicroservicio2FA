"""Inyección de dependencias de la feature oauth (composition root local)."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.feature.oauth.application.verify_code_use_case import VerifyCodeUseCase
from src.feature.oauth.domain.repositories.code_repository import CodeRepository
from src.feature.oauth.infraestructure.adapters.sql_code_repository import (
    SqlCodeRepository,
)
from src.feature.oauth.infraestructure.controllers.oauth_controller import (
    OAuthController,
)


def get_code_repository(
    session: AsyncSession = Depends(get_session),
) -> CodeRepository:
    return SqlCodeRepository(session)


def get_oauth_controller(
    repository: CodeRepository = Depends(get_code_repository),
) -> OAuthController:
    return OAuthController(VerifyCodeUseCase(repository))
