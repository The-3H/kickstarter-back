from chatbot_bot import ChatQA
import re
import pandas as pd
import io
from typing import Union
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatInput(BaseModel):
    age: int
    pregnancy_week: int
    input: str

@router.post("/")
async def chat(chat_input: ChatInput):
    chat_qa = ChatQA()
    input = {
        'age': chat_input.age,
        'pregnancy_week': chat_input.pregnancy_week,
        'input': chat_input.input
    }

    response = chat_qa.get_result(input['age'], input['pregnancy_week'], input['input'])

    return {
        "age": input['age'],
        "pregnancy_week": input['pregnancy_week'],
        "input": input['input'],
        "response": response.raw
    }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=58000)