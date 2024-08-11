from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import search_api
import chatbot_api
import average_price_api

app = FastAPI()

# CORS setting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_api.router, prefix="/search")
app.include_router(chatbot_api.router, prefix="/chat")
app.include_router(average_price_api.router, prefix="/avg_price")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=58000)