from average_price_bot import AvgPriceQA
import re
import pandas as pd
import io
from typing import Union
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class FoodInput(BaseModel):
    food: str

@router.post("/")
async def avg_price_cal(food_input: FoodInput):
    avg_price_qa = AvgPriceQA()
    input = {
        'food': food_input.food
    }
    response = avg_price_qa.get_result(input['food'])

    return {
        "food": input['food'],
        "price": response
    }