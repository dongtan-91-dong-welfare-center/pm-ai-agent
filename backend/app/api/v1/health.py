# 2026-04-08 [API_DESIGN.md] 헬스 체크 엔드포인트
# Ref: .claude/projects_management/pm-ai-agent/API_DESIGN.md#4-라우터-파일-구조

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    API 헬스 체크 (Ping 테스트)

    응답:
        {
            "status": "healthy",
            "version": "0.1.0"
        }
    """
    return {
        "status": "healthy",
        "version": "0.1.0 (Month 1 MVP)"
    }
