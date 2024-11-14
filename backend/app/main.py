from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stock Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import analysis, prediction, visualization

app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])  
