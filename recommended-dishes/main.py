from fastapi import FastAPI
from api.routes import router
from config import config
from data.database import db
from utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(title="餐饮智能推荐引擎 - AI Agent", version="1.0")

app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    try:
        db.create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.warning(f"Database initialization: {str(e)}")

@app.get("/")
async def root():
    return {"message": "餐饮智能推荐引擎 - AI Agent 服务已启动"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting server on {config.APP_HOST}:{config.APP_PORT}")
    uvicorn.run(app, host=config.APP_HOST, port=config.APP_PORT)