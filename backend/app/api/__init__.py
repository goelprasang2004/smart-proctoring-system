from fastapi import APIRouter
from app.api.endpoints import auth, proctoring, exams, attempts, admin, blockchain

api_router = APIRouter()


api_router.include_router(auth.router, tags=["login"])
api_router.include_router(proctoring.router, prefix="/proctoring", tags=["proctoring"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
# Add results as an alias to attempts for my-results endpoint
api_router.include_router(attempts.router, prefix="/results", tags=["results"])
# Admin endpoints
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
# Blockchain endpoints
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
