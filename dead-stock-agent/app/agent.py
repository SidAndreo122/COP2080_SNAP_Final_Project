from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

# Grabs the detect_dead_stock_batch function from the other file
from app.tool import detect_dead_stock_batch

load_dotenv()

# The basic prompt the AI works off of
template = """
You are a assistant foreman at a warehouse, providing advice to your foreman on how to handle dead inventory.
You know the following about the current inventory:
{inventory}
Given what you know about the inventory, answer the following question:
{prompt}
"""

# Creates the PromptTemplate object
prompt = PromptTemplate(
    input_variables=["inventory", "prompt"],
    template = template
)

#Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature = 0.3
    )

# Makes a simple chain to format the prompt
chain = prompt | llm | StrOutputParser()

def run_agent(query: str, inventory_df):
    """
    description placeholder
    """

    inventory_text = inventory_df.to_string(index=False)
    return chain.invoke({
        "inventory": inventory_text,
        "prompt": query
    })  