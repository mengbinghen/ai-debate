"""Node functions for the debate LangGraph."""
from typing import Any, Dict, Literal

from backend.agents import DebaterAgent, JudgeAgent, ModeratorAgent
from backend.debate_flow.state import DebateState, get_llm_client_for_role
from backend.models import DebateMessage, Role, RoundType


async def initialize_debate(state: DebateState) -> Dict[str, Any]:
    """Initialize the debate with moderator introduction.

    Args:
        state: Current debate state.

    Returns:
        Updated state with moderator introduction.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("moderator", model_config)
    moderator = ModeratorAgent(llm_client=llm_client)
    intro = await moderator.introduce_debate(state["topic"])

    message = DebateMessage(
        role=Role.MODERATOR,
        content=intro,
        round_type=RoundType.OPENING,
    )

    messages = state["debate_messages"] + [message]

    return {
        "current_round": "opening",
        "round_number": 1,
        "debate_messages": messages,
    }


async def opening_affirmative(state: DebateState) -> Dict[str, Any]:
    """Generate affirmative opening statement.

    Args:
        state: Current debate state.

    Returns:
        Updated state with affirmative opening statement.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("affirmative", model_config)
    debater = DebaterAgent(position="affirmative", llm_client=llm_client)
    statement = await debater.make_opening_statement(state["topic"])

    message = DebateMessage(
        role=Role.AFFIRMATIVE,
        content=statement,
        round_type=RoundType.OPENING,
    )

    opening_statements = state["opening_statements"].copy()
    opening_statements["affirmative"] = statement
    messages = state["debate_messages"] + [message]

    return {
        "opening_statements": opening_statements,
        "debate_messages": messages,
    }


async def opening_negative(state: DebateState) -> Dict[str, Any]:
    """Generate negative opening statement.

    Args:
        state: Current debate state.

    Returns:
        Updated state with negative opening statement.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("negative", model_config)
    debater = DebaterAgent(position="negative", llm_client=llm_client)
    statement = await debater.make_opening_statement(state["topic"])

    message = DebateMessage(
        role=Role.NEGATIVE,
        content=statement,
        round_type=RoundType.OPENING,
    )

    opening_statements = state["opening_statements"].copy()
    opening_statements["negative"] = statement
    messages = state["debate_messages"] + [message]

    return {
        "opening_statements": opening_statements,
        "debate_messages": messages,
    }


async def score_opening(state: DebateState) -> Dict[str, Any]:
    """Score the opening statements.

    Args:
        state: Current debate state.

    Returns:
        Updated state with opening scores.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("judge", model_config)
    judge = JudgeAgent(llm_client=llm_client)

    scores = state["scores"].copy()

    # Score affirmative opening
    aff_score = await judge.score_round(
        topic=state["topic"],
        round_type=RoundType.OPENING,
        position="affirmative",
        content=state["opening_statements"]["affirmative"],
    )
    scores.append(aff_score)

    # Score negative opening
    neg_score = await judge.score_round(
        topic=state["topic"],
        round_type=RoundType.OPENING,
        position="negative",
        content=state["opening_statements"]["negative"],
    )
    scores.append(neg_score)

    return {
        "current_round": "cross_examination",
        "scores": scores,
    }


async def cross_examination_round_1(state: DebateState) -> Dict[str, Any]:
    """First cross-examination round (affirmative questions, negative answers).

    Args:
        state: Current debate state.

    Returns:
        Updated state with first cross-examination.
    """
    model_config = state.get("model_config", {})
    aff_llm_client = get_llm_client_for_role("affirmative", model_config)
    neg_llm_client = get_llm_client_for_role("negative", model_config)

    aff_debater = DebaterAgent(position="affirmative", llm_client=aff_llm_client)
    neg_debater = DebaterAgent(position="negative", llm_client=neg_llm_client)

    # Affirmative asks question based on negative's opening
    question = await aff_debater.ask_cross_question(
        topic=state["topic"],
        opponent_statement=state["opening_statements"]["negative"],
    )

    # Negative answers
    answer = await neg_debater.answer_cross_question(
        topic=state["topic"],
        question=question,
        history=state["debate_messages"],
    )

    question_msg = DebateMessage(
        role=Role.AFFIRMATIVE,
        content=question,
        round_type=RoundType.CROSS_EXAMINATION,
    )

    answer_msg = DebateMessage(
        role=Role.NEGATIVE,
        content=answer,
        round_type=RoundType.CROSS_EXAMINATION,
    )

    cross_examinations = state["cross_examinations"].copy()
    cross_examinations.append({
        "round": 1,
        "questioner": "affirmative",
        "responder": "negative",
        "question": question,
        "answer": answer,
    })
    messages = state["debate_messages"] + [question_msg, answer_msg]

    return {
        "cross_examinations": cross_examinations,
        "debate_messages": messages,
    }


async def cross_examination_round_2(state: DebateState) -> Dict[str, Any]:
    """Second cross-examination round (negative questions, affirmative answers).

    Args:
        state: Current debate state.

    Returns:
        Updated state with second cross-examination.
    """
    model_config = state.get("model_config", {})
    aff_llm_client = get_llm_client_for_role("affirmative", model_config)
    neg_llm_client = get_llm_client_for_role("negative", model_config)

    aff_debater = DebaterAgent(position="affirmative", llm_client=aff_llm_client)
    neg_debater = DebaterAgent(position="negative", llm_client=neg_llm_client)

    # Negative asks question based on affirmative's opening
    question = await neg_debater.ask_cross_question(
        topic=state["topic"],
        opponent_statement=state["opening_statements"]["affirmative"],
    )

    # Affirmative answers
    answer = await aff_debater.answer_cross_question(
        topic=state["topic"],
        question=question,
        history=state["debate_messages"],
    )

    question_msg = DebateMessage(
        role=Role.NEGATIVE,
        content=question,
        round_type=RoundType.CROSS_EXAMINATION,
    )

    answer_msg = DebateMessage(
        role=Role.AFFIRMATIVE,
        content=answer,
        round_type=RoundType.CROSS_EXAMINATION,
    )

    cross_examinations = state["cross_examinations"].copy()
    cross_examinations.append({
        "round": 2,
        "questioner": "negative",
        "responder": "affirmative",
        "question": question,
        "answer": answer,
    })
    messages = state["debate_messages"] + [question_msg, answer_msg]

    return {
        "cross_examinations": cross_examinations,
        "debate_messages": messages,
        "current_round": "free_debate",
    }


async def free_debate_round(state: DebateState) -> Dict[str, Any]:
    """Free debate round with alternating statements.

    Args:
        state: Current debate state.

    Returns:
        Updated state with free debate messages.
    """
    model_config = state.get("model_config", {})
    aff_llm_client = get_llm_client_for_role("affirmative", model_config)
    neg_llm_client = get_llm_client_for_role("negative", model_config)

    aff_debater = DebaterAgent(position="affirmative", llm_client=aff_llm_client)
    neg_debater = DebaterAgent(position="negative", llm_client=neg_llm_client)

    current_round = state["free_debate_round"] + 1

    # Affirmative speaks first in free debate
    aff_response = await aff_debater.free_debate(
        topic=state["topic"],
        history=state["debate_messages"],
    )
    aff_msg = DebateMessage(
        role=Role.AFFIRMATIVE,
        content=aff_response,
        round_type=RoundType.FREE_DEBATE,
    )

    # Negative responds
    neg_response = await neg_debater.free_debate(
        topic=state["topic"],
        history=state["debate_messages"] + [aff_msg],
    )
    neg_msg = DebateMessage(
        role=Role.NEGATIVE,
        content=neg_response,
        round_type=RoundType.FREE_DEBATE,
    )

    messages = state["debate_messages"] + [aff_msg, neg_msg]

    return {
        "free_debate_round": current_round,
        "debate_messages": messages,
    }


async def closing_affirmative(state: DebateState) -> Dict[str, Any]:
    """Generate affirmative closing statement.

    Args:
        state: Current debate state.

    Returns:
        Updated state with affirmative closing statement.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("affirmative", model_config)
    debater = DebaterAgent(position="affirmative", llm_client=llm_client)
    statement = await debater.make_closing_statement(
        topic=state["topic"],
        history=state["debate_messages"],
    )

    message = DebateMessage(
        role=Role.AFFIRMATIVE,
        content=statement,
        round_type=RoundType.CLOSING,
    )

    closing_statements = state["closing_statements"].copy()
    closing_statements["affirmative"] = statement
    messages = state["debate_messages"] + [message]

    return {
        "closing_statements": closing_statements,
        "debate_messages": messages,
    }


async def closing_negative(state: DebateState) -> Dict[str, Any]:
    """Generate negative closing statement.

    Args:
        state: Current debate state.

    Returns:
        Updated state with negative closing statement.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("negative", model_config)
    debater = DebaterAgent(position="negative", llm_client=llm_client)
    statement = await debater.make_closing_statement(
        topic=state["topic"],
        history=state["debate_messages"],
    )

    message = DebateMessage(
        role=Role.NEGATIVE,
        content=statement,
        round_type=RoundType.CLOSING,
    )

    closing_statements = state["closing_statements"].copy()
    closing_statements["negative"] = statement
    messages = state["debate_messages"] + [message]

    return {
        "closing_statements": closing_statements,
        "debate_messages": messages,
    }


async def final_judgment(state: DebateState) -> Dict[str, Any]:
    """Generate final judgment and verdict.

    Args:
        state: Current debate state.

    Returns:
        Updated state with final verdict.
    """
    model_config = state.get("model_config", {})
    llm_client = get_llm_client_for_role("judge", model_config)
    judge = JudgeAgent(llm_client=llm_client)

    verdict = await judge.final_verdict(
        topic=state["topic"],
        scores=state["scores"],
        history=state["debate_messages"],
    )

    return {
        "final_verdict": verdict,
        "debate_finished": True,
        "current_round": "finished",
    }


# Conditional edge functions
def should_continue_free_debate(state: DebateState) -> Literal["continue", "end"]:
    """Decide whether to continue free debate or move to closing.

    Args:
        state: Current debate state.

    Returns:
        "continue" if more free debate rounds, "end" otherwise.
    """
    current_round = state["free_debate_round"]
    max_rounds = state["max_free_debate_rounds"]

    if current_round < max_rounds:
        return "continue"
    return "end"
