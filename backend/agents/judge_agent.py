"""Judge agent for scoring and verdict."""
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseAgent
from backend.models import DebateMessage, DebateScore, DebateVerdict, Role, RoundType
from backend.utils import LLMClient


class JudgeAgent(BaseAgent):
    """Agent for judging the debate and providing scores."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the judge agent.

        Args:
            llm_client: Optional LLM client.
        """
        system_prompt = self._load_system_prompt()
        super().__init__(role=Role.JUDGE, system_prompt=system_prompt, llm_client=llm_client)

        self.prompts = self._load_prompts()
        # Scoring weights
        self.weights = {
            "logic": 0.3,
            "evidence": 0.25,
            "rebuttal": 0.25,
            "expression": 0.2,
        }

    def _load_system_prompt(self) -> str:
        """Load the judge system prompt.

        Returns:
            The system prompt string.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            prompts = yaml.safe_load(f)

        return prompts["prompts"].get("judge_system", "")

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates.

        Returns:
            Dictionary of prompt templates.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["prompts"]

    async def score_round(
        self,
        topic: str,
        round_type: RoundType,
        position: str,
        content: str,
    ) -> DebateScore:
        """Score a single round for one position.

        Args:
            topic: The debate topic.
            round_type: The type of round being scored.
            position: Either "affirmative" or "negative".
            content: The content to score.

        Returns:
            A DebateScore object with the scores.
        """
        round_name = self._get_round_name(round_type)

        prompt = self.prompts.get("judge_scoring_prompt", "").format(
            round=round_name,
            topic=topic,
            position="正方" if position == "affirmative" else "反方",
            content=content,
        )

        response = await self.generate_json_with_prompt(prompt=prompt)

        # Calculate weighted total
        total = (
            response.get("logic", 0) * self.weights["logic"]
            + response.get("evidence", 0) * self.weights["evidence"]
            + response.get("rebuttal", 0) * self.weights["rebuttal"]
            + response.get("expression", 0) * self.weights["expression"]
        )

        return DebateScore(
            round_type=round_type,
            position=position,
            logic=response.get("logic", 0),
            evidence=response.get("evidence", 0),
            rebuttal=response.get("rebuttal", 0),
            expression=response.get("expression", 0),
            total=total,
            comment=response.get("comment", ""),
        )

    async def final_verdict(
        self,
        topic: str,
        scores: List[DebateScore],
        history: List[DebateMessage],
    ) -> DebateVerdict:
        """Generate the final verdict for the debate.

        Args:
            topic: The debate topic.
            scores: List of all scores for each round.
            history: Full debate history.

        Returns:
            A DebateVerdict object with the final decision.
        """
        # Calculate totals
        affirmative_scores = [s for s in scores if s.position == "affirmative"]
        negative_scores = [s for s in scores if s.position == "negative"]

        affirmative_total = sum(s.total for s in affirmative_scores)
        negative_total = sum(s.total for s in negative_scores)

        # Format scores for the prompt
        aff_scores_str = ", ".join(f"{s.round_type.value}: {s.total:.1f}" for s in affirmative_scores)
        neg_scores_str = ", ".join(f"{s.round_type.value}: {s.total:.1f}" for s in negative_scores)

        history_text = self.format_debate_history(history, include_system=False)

        prompt = self.prompts.get("final_verdict_prompt", "").format(
            topic=topic,
            affirmative_scores=aff_scores_str,
            negative_scores=neg_scores_str,
            history=history_text,
        )

        response = await self.generate_json_with_prompt(prompt=prompt)

        return DebateVerdict(
            winner=response.get("winner", "draw"),
            affirmative_total=response.get("affirmative_total", affirmative_total),
            negative_total=response.get("negative_total", negative_total),
            comment=response.get("comment", ""),
            scores=scores,
        )

    def _get_round_name(self, round_type: RoundType) -> str:
        """Get the display name for a round type.

        Args:
            round_type: The round type.

        Returns:
            The display name for the round.
        """
        names = {
            RoundType.OPENING: "开篇立论",
            RoundType.CROSS_EXAMINATION: "攻辩环节",
            RoundType.FREE_DEBATE: "自由辩论",
            RoundType.CLOSING: "总结陈词",
        }
        return names.get(round_type, str(round_type))

    async def respond(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the current context.

        For the judge, this typically means generating a verdict or score.

        Args:
            context: Current debate context.

        Returns:
            The generated response (typically a JSON string with scores).
        """
        # This is a placeholder; the judge is typically called via specific methods
        return await self.final_verdict(
            topic=context.get("topic", ""),
            scores=context.get("scores", []),
            history=context.get("history", []),
        )
