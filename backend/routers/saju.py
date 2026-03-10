"""사주팔자 계산 API 라우터."""

from __future__ import annotations
from fastapi import APIRouter
from schemas.saju import SajuCalcRequest, SajuCalcResponse
from core.errors import SWAGGER_ERRORS
from core.exceptions import CalcFailedException, InvalidDateFormatException
from engine.handlers.calculate_saju import handle_calculate_saju

router = APIRouter(prefix="/api/saju", tags=["사주 계산"])


@router.post(
    "/calc",
    response_model=SajuCalcResponse,
    summary="사주팔자 계산",
    description="""
생년월일시와 성별을 입력하면 사주팔자 전체를 계산합니다.

**계산 내용**:
- 4기둥 (연·월·일·시주) — 천간·지지·십성·12운성
- 오행·음양 분포 비율
- 일간 강약 (very_strong / strong / medium / weak / very_weak)
- 격국 (편재격·칠살격·정관격·식신격 등 13종)
- 용신·희신·기신 선정 (억부/조후/통관)
- 신살 (역마살·도화살·귀문관살·양인살 등, RAG 우선순위 포함)
- 지장간·지지 관계 (충·합·형·해·파)
- 대운 10구간 + 현재 대운
- 구조 패턴·동역학·시너지 (Writer Agent용)
- 행동 프로파일·생활 도메인 (RAG 쿼리 seed)

**시각 보정**:
동경 127° 기준으로 표준시를 보정합니다 (통상 -30~-32분).
역사적 표준시 변경(일제강점기·해방 후)도 자동 적용됩니다.

**음력 입력**:
`calendar: "lunar"` 설정 시 음력 날짜로 처리합니다.
윤달은 `is_leap_month: true`로 구분합니다.
""",
    responses={
        200: {
            "description": "사주팔자 계산 성공",
            "content": {
                "application/json": {
                    "example": SajuCalcResponse.model_config["json_schema_extra"]["example"]
                }
            },
        },
        **{k: v for k, v in SWAGGER_ERRORS.items() if k in (400, 422, 500)},
    },
)
async def calculate_saju(req: SajuCalcRequest) -> SajuCalcResponse:
    try:
        result = handle_calculate_saju(
            birth_date=req.birth_date,
            birth_time=req.birth_time,
            gender=req.gender,
            calendar=req.calendar,
            is_leap_month=req.is_leap_month,
        )
        return result
    except ValueError as e:
        msg = str(e)
        if "날짜" in msg or "date" in msg.lower():
            raise InvalidDateFormatException(req.birth_date)
        raise CalcFailedException(msg)
    except Exception as e:
        raise CalcFailedException(str(e))
