from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os, json

from agents import prompts

# Load env
load_dotenv(dotenv_path=".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ OPENAI_API_KEY missing in .env")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Load schema once
with open("agents/normalized_schema.json", "r") as f:
    SCHEMA_JSON = f.read()

# Define shared state
class AgentState(BaseModel):
    raw_data: dict
    normalized_data: dict | None = None
    amenities_findings: str | None = None
    reviews_findings: str | None = None
    descriptions_findings: str | None = None
    house_rules_findings: str | None = None
    images_findings: str | None = None
    final_report: str | None = None

# ---------------- Nodes ---------------- #

# Normalizer Agent
def normalizer_agent(state: AgentState):
    prompt = prompts.NORMALIZER_PROMPT + f"""
Here is the schema you must strictly follow:
{SCHEMA_JSON}

Now normalize this raw data into that schema:
{json.dumps(state.raw_data, indent=2)}
"""
    response = llm.invoke(prompt)
    try:
        normalized = json.loads(response.content)
    except Exception:
        normalized = {
            "error": "Failed to parse normalized JSON",
            "raw_response": response.content
        }
    return {"normalized_data": normalized}

# Specialist Agents
def amenities_agent(state: AgentState):
    prompt = prompts.AMENITIES_PROMPT + f"\n\nData:\n{json.dumps(state.normalized_data, indent=2)}"
    return {"amenities_findings": llm.invoke(prompt).content}

def reviews_agent(state: AgentState):
    prompt = prompts.REVIEWS_PROMPT + f"\n\nData:\n{json.dumps(state.normalized_data, indent=2)}"
    return {"reviews_findings": llm.invoke(prompt).content}

def descriptions_agent(state: AgentState):
    prompt = prompts.DESCRIPTIONS_PROMPT + f"\n\nData:\n{json.dumps(state.normalized_data, indent=2)}"
    return {"descriptions_findings": llm.invoke(prompt).content}

def house_rules_agent(state: AgentState):
    prompt = prompts.HOUSE_RULES_PROMPT + f"\n\nData:\n{json.dumps(state.normalized_data, indent=2)}"
    return {"house_rules_findings": llm.invoke(prompt).content}

def images_agent(state: AgentState):
    prompt = prompts.IMAGES_PROMPT + f"\n\nData:\n{json.dumps(state.normalized_data, indent=2)}"
    return {"images_findings": llm.invoke(prompt).content}

# Optimizer Agent
def optimizer_agent(state: AgentState):
    prompt = prompts.OPTIMIZER_PROMPT + f"""
Specialist findings:
- Amenities: {state.amenities_findings}
- Reviews: {state.reviews_findings}
- Descriptions: {state.descriptions_findings}
- House Rules: {state.house_rules_findings}
- Images: {state.images_findings}
"""
    return {"final_report": llm.invoke(prompt).content}

# ---------------- Graph ---------------- #

workflow = StateGraph(AgentState)

workflow.add_node("normalizer", normalizer_agent)
workflow.add_node("amenities", amenities_agent)
workflow.add_node("reviews", reviews_agent)
workflow.add_node("descriptions", descriptions_agent)
workflow.add_node("house_rules", house_rules_agent)
workflow.add_node("images", images_agent)
workflow.add_node("optimizer", optimizer_agent)

workflow.set_entry_point("normalizer")

# Fan out after normalizer
workflow.add_edge("normalizer", "amenities")
workflow.add_edge("normalizer", "reviews")
workflow.add_edge("normalizer", "descriptions")
workflow.add_edge("normalizer", "house_rules")
workflow.add_edge("normalizer", "images")

# All specialists converge to optimizer
workflow.add_edge("amenities", "optimizer")
workflow.add_edge("reviews", "optimizer")
workflow.add_edge("descriptions", "optimizer")
workflow.add_edge("house_rules", "optimizer")
workflow.add_edge("images", "optimizer")

workflow.add_edge("optimizer", END)

graph = workflow.compile()


