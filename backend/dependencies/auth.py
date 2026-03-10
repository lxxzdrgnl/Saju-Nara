"""인증 의존성 — 추후 로그인 구현 시 확장."""

from fastapi import Header


async def get_current_user(authorization: str | None = Header(default=None)):
    """현재는 None 반환 (익명 허용). JWT 도입 시 이 함수만 수정."""
    return None
