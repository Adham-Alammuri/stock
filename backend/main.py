from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import analysis, prediction, sentiment, visualization

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",               
        "http://localhost:5173",               
        "https://stock.adhamalammuri.com",     
        "https://adhamalammuri.com",           
        "https://www.adhamalammuri.com"        
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Stock Analysis API is running"}

app.include_router(analysis.router)
app.include_router(prediction.router)
app.include_router(sentiment.router)
app.include_router(visualization.router)