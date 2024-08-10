import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

GROQ_API_KEY = os.environ['GROQ_API_KEY']

from crewai import Agent, Task, Crew
from crewai_tools import tool, CSVSearchTool

from langchain_community.tools import DuckDuckGoSearchRun
# pip install --upgrade --quiet  duckduckgo-search

from groq import Groq
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic

#*-----------------LLM-----------------*#

llm = ChatGroq(temperature=0.2,
               #format="json",
               model_name="Llama-3.1-70b-Versatile",
               api_key=os.getenv('GROQ_API_KEY'))



#*-----------------Tools-----------------*#

'''
RxNorm_tool = CSVSearchTool(csv = "./RXNORM_cut.csv", 
    config=dict(
        llm=dict(
            provider="groq", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="llama3-70b-8192",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="huggingface", # or openai, ollama, ...
            config=dict(
                model="BAAI/bge-small-en-v1.5",
                #task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
#pip install sentence-transformers
'''


@tool('DuckDuckGoSearch')
def search_tool(search_query: str):
    """Search the web for information on a given topic"""
    return DuckDuckGoSearchRun().run(search_query)


#*-----------------Agents-----------------*#

food_searcher = Agent(
    role = "Food and Nutrient for Pregnant Women Specialist",
    goal = """Provide accurate, comprehensive, and tailored information about food and nutrition for pregnant women, considering their trimester, specific nutritional needs, and potential dietary restrictions.""",
    backstory = """You are an AI-powered nutritionist with extensive knowledge in prenatal nutrition. You have been programmed with the latest research and guidelines from reputable health organizations worldwide. Your primary focus is to assist pregnant women in making informed dietary choices to support their health and their baby's development throughout pregnancy.""",
    tools = [search_tool],
    llm=llm,
    max_iter = 5,
    allow_delegation = False,
    verbose = True,
)


#*-----------------Tasks-----------------*#

search_food = Task(
    description = """
        You are tasked with providing detailed nutritional information and recommendations for pregnant women based on their specific query. Analyze the user's input, consider any mentioned trimester or specific concerns, and provide a comprehensive response.
        
        <user_input>
        - User (Pregnant woman) age: {age}
        - {pregnancy_week} week pregnancy
        - Food search query: {input}
        </user_input> 
        
        Use the search tool to gather the most up-to-date and accurate information. Ensure your response is tailored to the needs of pregnant women and follows the expected output format.
        
        Assess the food safety level using these guidelines. You must consider the pregnancy trimester to assess the safety level into 1 to 5.
        <safety_level_guideline>

        Level 1: Optimal Foods
        High in essential nutrients
        Safe to consume
        Examples: leafy greens, salmon (low-mercury), lean meats, whole grains, fruits, pasteurized dairy

        Level 2: Generally Good Foods
        Nutritious but may need moderation
        Safe when properly prepared
        Examples: eggs (fully cooked), nuts, legumes, moderate caffeine (1-2 cups coffee/day)

        Level 3: Neutral Foods
        Neither particularly beneficial nor harmful
        Safe in moderation
        Examples: white bread, pasta, rice

        Level 4: Foods to Limit
        May pose minor risks or lack significant nutritional value
        Examples: processed foods, high-sugar snacks, artificial sweeteners

        Level 5: Foods to Avoid
        Pose significant risks to maternal or fetal health
        Examples: raw/undercooked meats, high-mercury fish, unpasteurized dairy, alcohol, raw sprouts

        </safety_level_guideline>

    """,
    agent = food_searcher,
    expected_output = """
        Provide a detailed response in the following format:

        1. Food Item Analysis:

           - Name: [Food name]
           - Safety level: [Safety level]
           - Nutritional Value: [List key nutrients]
           - Recommended Intake: [Amount per day/week]
           - Trimester-specific Recommendations: [1st/2nd/3rd trimester specifics]

        2. Key nutrients and calories calculation
        
            | Nutrient      | Amount per 100g | % Daily Value* |
            |---------------|-----------------|----------------|
            | Calories      | [number] kcal   | [number]%      |
            | Carbohydrates | [number] g      | [number]%      |
            | Protein       | [number] g      | [number]%      |
            | Fat           | [number] g      | [number]%      |
            | Sodium        | [number] mg     | [number]%      |
            | Sugar         | [number] g      | [number]%      |

        3. Benefits for Pregnancy:

           - [SINGLE SHORT SENTENCE with food benefits.]

        4. Potential Risks or Contraindications:

           - [SINGLE SHORT SENTENCE with any risks or contraindications.]

        5. Preparation Tips:

           - [SINGLE SHORT SENTENCE with Important tip for safe preparation or consumption.]

        6. Alternative Options:

           - [List 2-3 alternative foods with similar nutritional benefits]

        7. Additional Information:

           - [Any other relevant details or recommendations]

        8. Sources:

           - [List reliable sources used for this information]

        Ensure all information is evidence-based and tailored for pregnant women's needs.
    """,
    context = [],
    output_file = "output.md",
)



#*-----------------Crew-----------------*#

class SearchQA:
    def __init__(self):
        self.crew = Crew(
            tasks=[
                search_food
            ],
            agents=[
                food_searcher
            ],
            verbose=2,
        )

    def get_result(self, age, pregnancy_week, input):
        result = self.crew.kickoff(
            inputs={
                "age": age,
                "pregnancy_week": pregnancy_week,
                "input": input
            }
        )
        return result
