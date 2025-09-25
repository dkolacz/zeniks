import os
import json
from typing import TypedDict, Any, Dict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from .prompts import analyzer_prompt, improver_prompt  # if prompts.py is in same folder as graph.py

# -----------------------------
# Setup
# -----------------------------
load_dotenv()
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY"),
    # 👇 Force JSON output from the model
    model_kwargs={"response_format": {"type": "json_object"}}
)

# -----------------------------
# Helpers
# -----------------------------
def safe_json_parse(content: str) -> dict:
    """Try to parse JSON, return {} if fails."""
    try:
        return json.loads(content)
    except Exception as e:
        print("⚠️ JSON parse failed:", e)
        print("Raw content:", content)
        return {}

# -----------------------------
# Define Graph State
# -----------------------------
class AgentState(TypedDict):
    listing_json: Dict[str, Any]
    analysis: Dict[str, Any]
    improvements: Dict[str, Any]
    report: Dict[str, Any]

# -----------------------------
# Nodes
# -----------------------------
def analyze_listing(state: AgentState) -> AgentState:
    listing_context = json.dumps(state["listing_json"], indent=2)

    result = llm.invoke([
        {"role": "system", "content": "You are a helpful analyzer agent."},
        {"role": "user", "content": analyzer_prompt(listing_context)}
    ])

    analysis = safe_json_parse(result.content)
    state["analysis"] = analysis
    return state


def improve_listing(state: AgentState) -> AgentState:
    listing_context = json.dumps(state["listing_json"], indent=2)
    analysis_context = json.dumps(state.get("analysis", {}), indent=2)

    result = llm.invoke([
        {"role": "system", "content": "You are a helpful improver agent."},
        {"role": "user", "content": improver_prompt(listing_context, analysis_context)}
    ])

    improvements = safe_json_parse(result.content)
    state["improvements"] = improvements
    return state


def generate_report(state: AgentState) -> AgentState:
    state["report"] = {
        "analysis": state.get("analysis", {}),
        "improvements": state.get("improvements", {})
    }
    return state

# -----------------------------
# Build Graph
# -----------------------------
workflow = StateGraph(AgentState)

workflow.add_node("analyze", analyze_listing)
workflow.add_node("improve", improve_listing)
workflow.add_node("report", generate_report)

workflow.set_entry_point("analyze")
workflow.add_edge("analyze", "improve")
workflow.add_edge("improve", "report")
workflow.add_edge("report", END)

graph = workflow.compile()

# -----------------------------
# Run Example
# -----------------------------
if __name__ == "__main__":
    # 👇 Adjust path to your JSON file
    with open("scraper/responses/n_test_7_v3.json", "r") as f:
        listing = json.load(f)

    result = graph.invoke({"listing_json": listing})

    print("\n=== FINAL REPORT ===")
    print(json.dumps(result.get("report", {}), indent=2))
