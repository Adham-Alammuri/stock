from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import sentiment

app = FastAPI(title="Stock Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://adhamalammuri.com", "https://www.adhamalammuri.com"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes import analysis, prediction, visualization

app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])  
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
