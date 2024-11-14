from fastapi import APIRouter
from app.routes.prediction import router as prediction_router

router = APIRouter()
router.include_router(prediction_router, prefix="/prediction", tags=["prediction"])