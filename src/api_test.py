from fastapi import FastAPI

app = FastAPI()

@app.get("/items/age")
async def read_age(age: int):
    return {"age": age}