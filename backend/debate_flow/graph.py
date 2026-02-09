"""LangGraph state graph for the debate workflow."""
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from backend.debate_flow.nodes import (
    closing_affirmative,
    closing_negative,
    cross_examination_round_1,
    cross_examination_round_2,
    final_judgment,
    free_debate_round,
    initialize_debate,
    opening_affirmative,
    opening_negative,
    score_opening,
    should_continue_free_debate,
)
from backend.debate_flow.state import DebateState, create_initial_state


def build_debate_graph(max_free_debate_rounds: int = 3) -> StateGraph:
    """Build the debate state graph.

    Args:
        max_free_debate_rounds: Maximum number of free debate rounds.

    Returns:
        A compiled StateGraph for running debates.
    """
    # Create the state graph
    graph = StateGraph(DebateState)

    # Add nodes
    graph.add_node("initialize", initialize_debate)
    graph.add_node("opening_affirmative", opening_affirmative)
    graph.add_node("opening_negative", opening_negative)
    graph.add_node("score_opening", score_opening)
    graph.add_node("cross_examination_1", cross_examination_round_1)
    graph.add_node("cross_examination_2", cross_examination_round_2)
    graph.add_node("free_debate", free_debate_round)
    graph.add_node("closing_affirmative", closing_affirmative)
    graph.add_node("closing_negative", closing_negative)
    graph.add_node("final_judgment", final_judgment)

    # Set entry point
    graph.set_entry_point("initialize")

    # Define edges (linear flow)
    graph.add_edge("initialize", "opening_affirmative")
    graph.add_edge("opening_affirmative", "opening_negative")
    graph.add_edge("opening_negative", "score_opening")
    graph.add_edge("score_opening", "cross_examination_1")
    graph.add_edge("cross_examination_1", "cross_examination_2")
    graph.add_edge("cross_examination_2", "free_debate")

    # Conditional edge for free debate (can loop)
    graph.add_conditional_edges(
        "free_debate",
        should_continue_free_debate,
        {
            "continue": "free_debate",
            "end": "closing_affirmative",
        },
    )

    graph.add_edge("closing_affirmative", "closing_negative")
    graph.add_edge("closing_negative", "final_judgment")
    graph.add_edge("final_judgment", END)

    return graph.compile()


async def run_debate(
    topic: str,
    max_free_debate_rounds: int = 3,
) -> Dict[str, Any]:
    """Run a complete debate.

    Args:
        topic: The debate topic.
        max_free_debate_rounds: Maximum number of free debate rounds.

    Returns:
        A dictionary containing the debate results including:
        - messages: List of all debate messages
        - final_verdict: The final verdict
        - scores: List of all scores
    """
    # Build and compile the graph
    graph = build_debate_graph(max_free_debate_rounds=max_free_debate_rounds)

    # Create initial state
    initial_state = create_initial_state(
        topic=topic,
        max_free_debate_rounds=max_free_debate_rounds,
    )

    # Run the debate
    result = await graph.ainvoke(initial_state)

    return {
        "topic": topic,
        "messages": result["debate_messages"],
        "final_verdict": result["final_verdict"],
        "scores": result["scores"],
        "opening_statements": result["opening_statements"],
        "cross_examinations": result["cross_examinations"],
        "closing_statements": result["closing_statements"],
    }


# Type alias for the compiled graph
DebateGraph = StateGraph
