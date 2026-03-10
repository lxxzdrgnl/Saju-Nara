"""SajuBon FastAPI 진입점."""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import saju

app = FastAPI(
    title="SajuBon API",
    version="0.1.0",
    description="AI 사주 상담 서비스 — 사주팔자 계산·궁합·오늘의 운세·한줄 상담",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(saju.router)
# app.include_router(compatibility.router)   # 구현 예정
# app.include_router(daily.router)           # 구현 예정
# app.include_router(question.router)        # 구현 예정


@app.get("/health", tags=["상태 확인"])
async def health():
    return {"status": "ok"}
