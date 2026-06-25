"""Controller de oauth: orquesta la validación del código."""
from pydantic import BaseModel, EmailStr, Field

from src.feature.oauth.application.verify_code_use_case import VerifyCodeUseCase


class VerifyRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=4, max_length=12)


class VerifyResponse(BaseModel):
    email: EmailStr
    valid: bool
    reason: str


class OAuthController:
    def __init__(self, verify_use_case: VerifyCodeUseCase) -> None:
        self._verify_use_case = verify_use_case

    async def verify(self, payload: VerifyRequest) -> VerifyResponse:
        result = await self._verify_use_case.execute(payload.email, payload.code)
        return VerifyResponse(
            email=payload.email,
            valid=result.valid,
            reason=result.reason,
        )
