"""Moderator agent for hosting the debate."""
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.agents.base_agent import BaseAgent
from backend.models import DebateMessage, Role
from backend.utils import LLMClient


class ModeratorAgent(BaseAgent):
    """Agent for moderating the debate."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the moderator agent.

        Args:
            llm_client: Optional LLM client.
        """
        system_prompt = self._load_system_prompt()
        super().__init__(role=Role.MODERATOR, system_prompt=system_prompt, llm_client=llm_client)

        self.prompts = self._load_prompts()

    def _load_system_prompt(self) -> str:
        """Load the moderator system prompt.

        Returns:
            The system prompt string.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            prompts = yaml.safe_load(f)

        return prompts["prompts"].get("moderator_system", "")

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates.

        Returns:
            Dictionary of prompt templates.
        """
        prompts_path = Path(__file__).parent.parent.parent / "config" / "prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data["prompts"]

    async def introduce_debate(self, topic: str) -> str:
        """Generate an opening introduction for the debate.

        Args:
            topic: The debate topic.

        Returns:
            The introduction text.
        """
        prompt = f"""请为以下辩题作一个开场介绍。

辩题：{topic}

要求：
- 简要介绍辩题背景
- 说明辩论规则
- 保持中立和专业
- 字数控制在200字以内"""

        return await self.generate_with_prompt(prompt=prompt, max_tokens=300)

    async def announce_round(self, round_name: str) -> str:
        """Generate an announcement for a new round.

        Args:
            round_name: The name of the round to announce.

        Returns:
            The announcement text.
        """
        announcements = {
            "opening": "现在开始开篇立论环节。首先请正方发言，然后由反方发言。",
            "cross_examination": "现在进入攻辩环节。双方将互相提问和回答。",
            "free_debate": "现在进入自由辩论环节。双方将自由辩论，交替发言。",
            "closing": "现在进入总结陈词环节。首先请正方总结，然后由反方总结。",
        }
        return announcements.get(round_name, f"现在进入{round_name}环节。")

    async def respond(self, context: Dict[str, Any]) -> str:
        """Generate a response based on the current context.

        Args:
            context: Current debate context.

        Returns:
            The generated response.
        """
        round_type = context.get("round_type", "opening")

        if round_type == "opening":
            return await self.introduce_debate(context.get("topic", ""))
        else:
            return await self.announce_round(round_type)
