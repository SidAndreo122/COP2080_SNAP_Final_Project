from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
import pandas as pd
import os
import streamlit

# Grabs the detect_dead_stock_batch function and get_rag_tool from the other file
from app.tool import detect_dead_stock_batch
from app.rag import get_rag_tool

load_dotenv()


def get_secret(key: str) -> str:
    """Reads from st.secrets when deployed, falls back to .env locally."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ[key]

#Initialize the Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature = 0.3
)

# The basic prompt the AI works off of
system_prompt = """
You are an expert supply chain advisor at Meridian Supply Co.
Your job is to help warehouse managers understand and act on their inventory data.
 
You have access to two tools:
1. analyze_inventory   — runs financial dead stock calculations on the current inventory.
                         Always call this first when the user asks about stock health,
                         holding costs, or which products are at risk.
2. search_knowledge_base — searches internal policy and product catalog documents.
                           Use this when the user asks what to DO about dead stock,
                           supplier return options, markdown rules, or product details.
 
Always reason step by step. If a question requires both tools, use both.
Be concise, specific, and actionable in your responses.
"""


# Non-LLM tool usage
@tool
def analyze_inventory(query: str ) -> str:
    """Runs the Dead Stock Detector batch Non-LLM tool.
    Use this to identify which SKUs are dead, at-risk, slow-moving, or healthy,
    and to calculate their total holding costs.
    The query parameter describes what aspect of the inventory to focus on """
    df = get_inventory_df()
    if df is None:
        return "No inventory data loaded. Please upload a CSV file first"
    skus = df.to_dict(orient="records")
    results = detect_dead_stock_batch(skus)
    lines = []
    for r in results:
        if r["error"]:
            lines.append(f"{r['sku_id']} ({r['product_name']}): ERROR - {r['error']}")
        else:
            lines.append(
                f"{r['sku_id']} | {r['product_name']} | {r['severity'].value} | "
                f"{r['days_of_stock_remaining']:.1f} days | "
                f"${r['result']:,.2f} holding cost"
            )
            return "\n".join(lines)

# helper functions
inventory_df: pd.DataFrame | None = None

def set_inventory_df(df: pd.DataFrame):
    global inventory_df
    inventory_df = df

def get_inventory_df() -> pd.DataFrame | None:
    return inventory_df

# RAG tool usage
def create_agent():
    rag_tool = get_rag_tool()
    tools = [analyze_inventory, rag_tool]


    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,   
    )

def run_agent(query: str, agent) -> str:
    """
    Takes the user query and the inventory data as arguments, then returns the AI response.
    """

    result = agent.invoke({"messages": [("human", query)]})
    content = result["messages"][-1].content
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        return " ".join(
            block["text"] for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)