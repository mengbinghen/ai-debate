"""State definition for the debate LangGraph."""
import os
from typing import Any, Dict, List, Optional, TypedDict

from backend.models import DebateMessage, DebateScore, DebateVerdict, Role, RoundType
from backend.utils import LLMClient
from config import settings


class DebateState(TypedDict):
    """State for the debate workflow.

    This state is passed through each node in the LangGraph and accumulates
    information as the debate progresses.
    """

    # Basic debate information
    topic: str  # The debate topic
    current_round: str  # Current round name
    round_number: int  # Current round counter

    # Debate history
    debate_messages: List[DebateMessage]  # All debate messages

    # Round-specific content
    opening_statements: Dict[str, str]  # Opening statements by position
    cross_examinations: List[Dict[str, str]]  # Cross-examination records
    free_debate_messages: List[DebateMessage]  # Free debate messages
    closing_statements: Dict[str, str]  # Closing statements by position

    # Scoring information
    scores: List[DebateScore]  # Scores for each round
    final_verdict: Optional[DebateVerdict]  # Final verdict

    # Control flags
    debate_finished: bool  # Whether the debate is finished
    free_debate_round: int  # Current free debate round number
    max_free_debate_rounds: int  # Maximum free debate rounds

    # Error handling
    error: Optional[str]  # Error message if something went wrong

    # Model configuration
    model_config: Dict[str, Dict[str, Any]]  # Per-agent model config


def get_default_model_config() -> Dict[str, Dict[str, Any]]:
    """Get default model configuration from settings.

    Returns:
        Dictionary mapping role names to their model configuration.
    """
    return {
        "affirmative": {
            "provider": settings.DEFAULT_PROVIDER,
            "model": settings.AFFIRMATIVE_MODEL,
        },
        "negative": {
            "provider": settings.DEFAULT_PROVIDER,
            "model": settings.NEGATIVE_MODEL,
        },
        "judge": {
            "provider": settings.DEFAULT_PROVIDER,
            "model": settings.JUDGE_MODEL,
        },
        "moderator": {
            "provider": settings.DEFAULT_PROVIDER,
            "model": settings.MODERATOR_MODEL,
        },
    }


def get_llm_client_for_role(role: str, model_config: Dict[str, Dict[str, Any]]) -> LLMClient:
    """Create an LLM client configured for a specific role.

    Args:
        role: The role name (e.g., "affirmative", "negative", "judge", "moderator").
        model_config: The model configuration dictionary.

    Returns:
        An LLMClient instance configured for the specified role.
    """
    config = model_config.get(role, {})
    provider = config.get("provider", "deepseek")
    model = config.get("model", settings.DEFAULT_MODEL)

    provider_config = settings.PROVIDERS.get(provider, {})
    base_url = provider_config.get("base_url")
    api_key_env = provider_config.get("api_key_env", f"{provider.upper()}_API_KEY")

    # Get API key from settings (which loads from .env via pydantic-settings)
    # Fall back to os.environ for backwards compatibility
    api_key = getattr(settings, api_key_env, "") or os.environ.get(api_key_env, "")

    return LLMClient(api_key=api_key, base_url=base_url, model=model)


def create_initial_state(
    topic: str,
    max_free_debate_rounds: int = 3,
    model_config: Optional[Dict[str, Dict[str, Any]]] = None
) -> DebateState:
    """Create the initial state for a debate.

    Args:
        topic: The debate topic.
        max_free_debate_rounds: Maximum number of free debate rounds.
        model_config: Optional model configuration for each role.

    Returns:
        The initial debate state.
    """
    return DebateState(
        topic=topic,
        current_round="initialize",
        round_number=0,
        debate_messages=[],
        opening_statements={},
        cross_examinations=[],
        free_debate_messages=[],
        closing_statements={},
        scores=[],
        final_verdict=None,
        debate_finished=False,
        free_debate_round=0,
        max_free_debate_rounds=max_free_debate_rounds,
        error=None,
        model_config=model_config or get_default_model_config(),
    )
