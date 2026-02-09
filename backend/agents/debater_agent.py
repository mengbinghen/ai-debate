"""Debater agent for affirmative and negative positions."""
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseAgent
from backend.models import DebateMessage, Role, RoundType
from backend.utils import LLMClient


class DebaterAgent(BaseAgent):
    """Agent for debating on either affirmative or negative side."""

    def __init__(
        self,
        position: str,  # "affirmative" or "negative"
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize the debater agent.

        Args:
            position: Either "affirmative" or "negative".
            llm_client: Optional LLM client.
        """
        if position not in ("affirmative", "negative"):
            raise ValueError(f"Invalid position: {position}. Must be 'affirmative' or 'negative'.")

        role = Role.AFFIRMATIVE if position == "affirmative" else Role.NEGATIVE
        system_prompt = self._load_system_prompt(position)

        super().__init__(role=role, system_prompt=system_prompt, llm_client=llm_client)

        self.position = position
        self.prompts = self._load_prompts()

    def _load_system_prompt(self, position: str) -> str:
        """Load the system prompt for this position.

        Args:
            position: Either "affirmative" or "negative".

        Returns:
            The system prompt string.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            prompts = yaml.safe_load(f)

        key = f"{position}_system"
        return prompts["prompts"].get(key, "")

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates.

        Returns:
            Dictionary of prompt templates.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["prompts"]

    async def make_opening_statement(
        self,
        topic: str,
        word_limit: int = 800,
    ) -> str:
        """Generate an opening statement.

        Args:
            topic: The debate topic.
            word_limit: Maximum word count for the statement.

        Returns:
            The opening statement.
        """
        prompt = self.prompts.get("opening_prompt", "").format(
            position="正方" if self.position == "affirmative" else "反方",
            topic=topic,
            word_limit=word_limit,
        )

        return await self.generate_with_prompt(
            prompt=prompt,
            max_tokens=word_limit * 2,  # Rough token estimate
        )

    async def ask_cross_question(
        self,
        topic: str,
        opponent_statement: str,
    ) -> str:
        """Generate a cross-examination question.

        Args:
            topic: The debate topic.
            opponent_statement: The opponent's statement to question.

        Returns:
            The generated question.
        """
        prompt = self.prompts.get("cross_question_prompt", "").format(
            position="正方" if self.position == "affirmative" else "反方",
            topic=topic,
            opponent_statement=opponent_statement,
        )

        return await self.generate_with_prompt(
            prompt=prompt,
            max_tokens=200,
        )

    async def answer_cross_question(
        self,
        topic: str,
        question: str,
        history: List[DebateMessage],
    ) -> str:
        """Answer a cross-examination question.

        Args:
            topic: The debate topic.
            question: The question to answer.
            history: Debate history for context.

        Returns:
            The answer to the question.
        """
        history_text = self.format_debate_history(history)

        prompt = self.prompts.get("cross_response_prompt", "").format(
            position="正方" if self.position == "affirmative" else "反方",
            topic=topic,
            question=question,
            history=history_text,
        )

        return await self.generate_with_prompt(
            prompt=prompt,
            max_tokens=500,
        )

    async def free_debate(
        self,
        topic: str,
        history: List[DebateMessage],
    ) -> str:
        """Generate a free debate response.

        Args:
            topic: The debate topic.
            history: Debate history for context.

        Returns:
            The free debate response.
        """
        history_text = self.format_debate_history(history)

        prompt = self.prompts.get("free_debate_prompt", "").format(
            position="正方" if self.position == "affirmative" else "反方",
            topic=topic,
            history=history_text,
        )

        return await self.generate_with_prompt(
            prompt=prompt,
            max_tokens=400,
        )

    async def make_closing_statement(
        self,
        topic: str,
        history: List[DebateMessage],
        word_limit: int = 500,
    ) -> str:
        """Generate a closing statement.

        Args:
            topic: The debate topic.
            history: Full debate history.
            word_limit: Maximum word count for the statement.

        Returns:
            The closing statement.
        """
        history_text = self.format_debate_history(history)

        prompt = self.prompts.get("closing_prompt", "").format(
            position="正方" if self.position == "affirmative" else "反方",
            topic=topic,
            history=history_text,
            word_limit=word_limit,
        )

        return await self.generate_with_prompt(
            prompt=prompt,
            max_tokens=word_limit * 2,
        )

    async def respond(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the current context.

        This is a generic response method that determines the appropriate
        response type based on the current round.

        Args:
            context: Current debate context.

        Returns:
            The generated response.
        """
        round_type = context.get("round_type", RoundType.OPENING)
        topic = context.get("topic", "")

        if round_type == RoundType.OPENING:
            return await self.make_opening_statement(topic)
        elif round_type == RoundType.FREE_DEBATE:
            return await self.free_debate(topic, context.get("history", []))
        elif round_type == RoundType.CLOSING:
            return await self.make_closing_statement(topic, context.get("history", []))
        else:
            # Default to free debate style response
            return await self.free_debate(topic, context.get("history", []))
