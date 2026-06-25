"""Adaptador SQL del puerto CodeRepository (SQLAlchemy async)."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base
from src.feature.oauth.domain.entities.two_factor_code import TwoFactorCode
from src.feature.oauth.domain.repositories.code_repository import CodeRepository


class TwoFactorCodeModel(Base):
    """Modelo ORM. Vive en infraestructura, separado de la entidad de dominio."""

    __tablename__ = "two_factor_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(12), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _to_entity(model: TwoFactorCodeModel) -> TwoFactorCode:
    return TwoFactorCode(
        id=model.id,
        email=model.email,
        code=model.code,
        expires_at=model.expires_at,
        used=model.used,
        created_at=model.created_at,
    )


class SqlCodeRepository(CodeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, code: TwoFactorCode) -> TwoFactorCode:
        model = TwoFactorCodeModel(
            email=code.email,
            code=code.code,
            expires_at=code.expires_at,
            used=code.used,
            created_at=code.created_at,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def find_active_by_email(self, email: str) -> TwoFactorCode | None:
        stmt = (
            select(TwoFactorCodeModel)
            .where(
                TwoFactorCodeModel.email == email,
                TwoFactorCodeModel.used.is_(False),
            )
            .order_by(TwoFactorCodeModel.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def mark_used(self, code_id: int) -> None:
        await self._session.execute(
            update(TwoFactorCodeModel)
            .where(TwoFactorCodeModel.id == code_id)
            .values(used=True)
        )
        await self._session.commit()

    async def invalidate_previous(self, email: str) -> None:
        await self._session.execute(
            update(TwoFactorCodeModel)
            .where(
                TwoFactorCodeModel.email == email,
                TwoFactorCodeModel.used.is_(False),
            )
            .values(used=True)
        )
        await self._session.commit()
