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

@tool('DuckDuckGoSearch')
def search_tool(search_query: str):
    """Search the web for information on a given topic"""
    return DuckDuckGoSearchRun().run(search_query)


#*-----------------Agents-----------------*#

prenatal_health_educator = Agent(
    role="Prenatal Health Education Specialist",
    goal="""Provide clear, accurate, and supportive health information to pregnant women, 
    addressing their concerns and promoting maternal and fetal well-being.""",
    backstory="""With a background in obstetrics and gynecology and a specialization in maternal-fetal medicine, 
    you've dedicated your career to supporting expectant mothers. Your expertise in prenatal care, nutrition, 
    and common pregnancy discomforts allows you to offer comprehensive and empathetic guidance.""",
    tools=[search_tool],
    llm=llm,
    verbose=True,
    max_iter = 6,
    allow_delegation = False
)

#*-----------------Tasks-----------------*#

prenatal_advice = Task(
    description="""
    Provide tailored health advice for a pregnant woman based on her age, gestational week, and specific concern:
    
    <patient_info>
    Age: {age}
    Gestational Week: {pregnancy_week}
    Concern: {input}
    </patient_info>
    
    Your advice must:
    <advice_requirements>
    1. Address the specific concern raised by the pregnant woman
    2. Provide clear, evidence-based information relevant to her stage of pregnancy
    3. Offer safe, practical solutions or management strategies for her symptoms
    4. Explain when to seek immediate medical attention, if applicable
    5. Include general wellness tips appropriate for her trimester
    6. Acknowledge any age-related considerations for her pregnancy
    7. Recommend reliable resources for further information
    8. Emphasize the importance of regular prenatal check-ups
    </advice_requirements>

    Use the search_tool to find up-to-date, evidence-based information as needed.
    """,
    agent=prenatal_health_educator,
    expected_output="""
    Deliver a comprehensive, empathetic prenatal health advice report including:
    <prenatal_advice_report>
    1. A clear explanation of the concern and its relevance to pregnancy
    2. Safe, practical advice for managing the symptoms or addressing the concern
    3. Information on when to seek medical attention
    4. General wellness tips appropriate for the current trimester
    5. Any age-specific considerations for the pregnancy
    6. Recommendations for reliable resources or further reading
    7. A reminder about the importance of regular prenatal care
    </prenatal_advice_report>

    Format your response in a warm, reassuring tone that balances medical accuracy with compassion. 
    Use headings, bullet points, and possibly a FAQ section to enhance readability. Include a 
    brief "Key Points" summary at the beginning for quick reference.
    """,
    context=[],
    output_file = "./prenatal_advice_output.md"
)


#*-----------------Crew-----------------*#

class ChatQA:
    def __init__(self):
        self.crew = Crew(
            tasks=[
                prenatal_advice
            ],
            agents=[
                prenatal_health_educator
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
