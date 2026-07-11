"""
Phase 2: The Autonomous Content Engine (LangGraph)
Builds a 3-node state machine: Decide Search → Web Search → Draft Post
Uses Google Gemini as the LLM and structured JSON output.
"""

import os
import json
import re
from typing import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

load_dotenv()

# ── LLM Setup ─────────────────────────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.environ.get("GOOGLE_API_KEY"),
    temperature=0.8,
)

# ── Bot Personas ───────────────────────────────────────────────────────────────
BOT_PERSONAS = {
    "bot_a": (
        "You are Bot A — a Tech Maximalist. You fervently believe AI and crypto will "
        "solve all human problems. You are highly optimistic about technology, Elon Musk, "
        "and space exploration. You dismiss regulatory concerns as fear-mongering."
    ),
    "bot_b": (
        "You are Bot B — a Doomer/Skeptic. You believe late-stage capitalism and tech "
        "monopolies are destroying society. You are highly critical of AI, social media, "
        "and billionaires. You value privacy and nature above profit."
    ),
    "bot_c": (
        "You are Bot C — a Finance Bro. You strictly care about markets, interest rates, "
        "trading algorithms, and making money. You speak in finance jargon and view "
        "every topic purely through the lens of ROI and alpha generation."
    ),
}

# ── Mock Search Tool ───────────────────────────────────────────────────────────
MOCK_NEWS_DB = {
    "crypto":    "Bitcoin hits new all-time high amid regulatory ETF approvals.",
    "bitcoin":   "Bitcoin hits new all-time high amid regulatory ETF approvals.",
    "ai":        "OpenAI releases GPT-5, sparking mass debate on white-collar job displacement.",
    "openai":    "OpenAI releases GPT-5, sparking mass debate on white-collar job displacement.",
    "elon":      "Elon Musk's xAI raises $6B as Grok becomes default AI on X platform.",
    "tesla":     "Tesla autopilot cleared of fault in landmark EU court ruling.",
    "market":    "S&P 500 surges 3% as Fed signals two rate cuts before year end.",
    "fed":       "Federal Reserve holds rates steady; hints at September pivot.",
    "interest":  "10-year Treasury yield drops below 4% for first time since 2022.",
    "privacy":   "Meta fined €1.2B for GDPR violations; EU demands data deletion.",
    "tech":      "Big Tech lobbying record $500M to water down EU AI Act provisions.",
    "climate":   "Scientists warn 2024 is hottest year on record by largest margin ever.",
    "space":     "SpaceX Starship completes first orbital flight; Mars mission on track for 2030.",
}


@tool
def mock_searxng_search(query: str) -> str:
    """
    Simulates a SearXNG web search.
    Returns hardcoded recent headlines based on keywords found in the query.
    """
    query_lower = query.lower()
    results = []
    for keyword, headline in MOCK_NEWS_DB.items():
        if keyword in query_lower and headline not in results:
            results.append(headline)
    if not results:
        results.append(
            "General tech news: AI adoption accelerating across all industries in 2025."
        )
    return " | ".join(results[:3])  # return up to 3 headlines


# ── LangGraph State ────────────────────────────────────────────────────────────
class PostState(TypedDict):
    bot_id: str
    persona: str
    search_query: str
    search_results: str
    final_post: dict  # {"bot_id": ..., "topic": ..., "post_content": ...}


# ── Node 1: Decide Search ──────────────────────────────────────────────────────
def decide_search_node(state: PostState) -> PostState:
    """LLM decides what topic to post about and creates a search query."""
    print("  [Node 1] Deciding search query...")

    messages = [
        SystemMessage(content=state["persona"]),
        HumanMessage(
            content=(
                "You are about to make a social media post. "
                "Based on your personality, decide ONE topic you want to post about today. "
                "Respond with ONLY a short search query (3-7 words) to find recent news on that topic. "
                "No explanation, just the query."
            )
        ),
    ]

    response = llm.invoke(messages)
    query = response.content.strip().strip('"')
    print(f"  [Node 1] Search query: \"{query}\"")
    return {**state, "search_query": query}


# ── Node 2: Web Search ─────────────────────────────────────────────────────────
def web_search_node(state: PostState) -> PostState:
    """Executes the mock search tool to retrieve context."""
    print("  [Node 2] Running mock web search...")
    results = mock_searxng_search.invoke({"query": state["search_query"]})
    print(f"  [Node 2] Results: {results}")
    return {**state, "search_results": results}


# ── Node 3: Draft Post ─────────────────────────────────────────────────────────
def draft_post_node(state: PostState) -> PostState:
    """LLM drafts a 280-char opinionated post and returns strict JSON."""
    print("  [Node 3] Drafting post...")

    messages = [
        SystemMessage(content=state["persona"]),
        HumanMessage(
            content=(
                f"Recent news context: {state['search_results']}\n\n"
                "Using the above news as inspiration, write a highly opinionated social media post "
                "IN YOUR PERSONA. The post must be under 280 characters.\n\n"
                "Respond ONLY with a valid JSON object — no markdown, no backticks, no explanation:\n"
                '{"bot_id": "<bot_id>", "topic": "<topic>", "post_content": "<post under 280 chars>"}\n\n'
                f"Use bot_id = \"{state['bot_id']}\"."
            )
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content.strip()

    # Strip markdown fences if model wraps in ```json ... ```
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        post_json = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: wrap raw text so pipeline doesn't crash
        post_json = {
            "bot_id": state["bot_id"],
            "topic": state["search_query"],
            "post_content": raw[:280],
        }

    print(f"  [Node 3] Post JSON: {json.dumps(post_json, indent=2)}")
    return {**state, "final_post": post_json}


# ── Build LangGraph ────────────────────────────────────────────────────────────
def build_content_graph() -> StateGraph:
    graph = StateGraph(PostState)
    graph.add_node("decide_search", decide_search_node)
    graph.add_node("web_search", web_search_node)
    graph.add_node("draft_post", draft_post_node)

    graph.set_entry_point("decide_search")
    graph.add_edge("decide_search", "web_search")
    graph.add_edge("web_search", "draft_post")
    graph.add_edge("draft_post", END)

    return graph.compile()


def run_content_engine(bot_id: str) -> dict:
    """Run the full LangGraph pipeline for a given bot."""
    persona = BOT_PERSONAS.get(bot_id)
    if not persona:
        raise ValueError(f"Unknown bot_id: {bot_id}")

    initial_state: PostState = {
        "bot_id": bot_id,
        "persona": persona,
        "search_query": "",
        "search_results": "",
        "final_post": {},
    }

    app = build_content_graph()
    final_state = app.invoke(initial_state)
    return final_state["final_post"]


# ── Demo ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🤖  PHASE 2 — AUTONOMOUS CONTENT ENGINE")
    print("=" * 60)

    for bot_id in ["bot_a", "bot_b", "bot_c"]:
        print(f"\n▶  Running pipeline for {bot_id}...")
        result = run_content_engine(bot_id)
        print(f"\n✅ Final Output:\n{json.dumps(result, indent=2)}")
        print("-" * 60)
