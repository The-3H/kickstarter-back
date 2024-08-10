from groq import Groq
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

import os
import pprint
import sys
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
GROQ_API_KEY = os.environ["GROQ_API_KEY"]


llm_api = ChatGroq(
    model_name="Llama-3.1-8b-Instant",
    temperature=0.1
)

prompt_api = PromptTemplate(
    input_variables=["food"],
    template="""
    What is the average price of {food} in USD dollar? The price should be realistic and specific, including tip. YOU MUST ONLY print the dollar sign and a number. (e.g. "$0.34")
    """
)


output_parser = StrOutputParser()

chain_api = prompt_api | llm_api | output_parser


# food input
foods = ["Sushi", "Pasta", "Instant Ramen", "Chinese spicy hot pot"] #! API

res = []
for food in foods:
    
    res.append(chain_api.invoke({"food": food}))

print(res)