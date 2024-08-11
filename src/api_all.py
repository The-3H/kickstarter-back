from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import search_api
import chatbot_api
import average_price_api
import logging
from fastapi.middleware.gzip import GZipMiddleware


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS setting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip 압축 추가
app.add_middleware(GZipMiddleware, minimum_size=1000)


app.include_router(search_api.router, prefix="/search")
app.include_router(chatbot_api.router, prefix="/chat")
app.include_router(average_price_api.router, prefix="/avg_price")

@app.on_event("startup")
async def startup_event():
    logger.info("Application is starting up")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application is shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=58000, log_level = "info")