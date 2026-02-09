"""Base agent class for all debate agents."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.models import DebateMessage, Role, RoundType
from backend.utils import LLMClient
from config import settings


class BaseAgent(ABC):
    """Base class for all agents in the debate system."""

    def __init__(
        self,
        role: Role,
        system_prompt: Optional[str] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        """Initialize the base agent.

        Args:
            role: The role of this agent (e.g., Role.AFFIRMATIVE, Role.JUDGE).
            system_prompt: Optional system prompt for the LLM.
            llm_client: Optional LLM client. If not provided, creates a new one.
        """
        self.role = role
        self.system_prompt = system_prompt
        self.llm_client = llm_client or LLMClient()

    @abstractmethod
    async def respond(
        self,
        context: Dict[str, Any],
    ) -> str:
        """Generate a response based on the current context.

        Args:
            context: Current debate context including topic, history, etc.

        Returns:
            The generated response text.
        """
        pass

    async def generate_with_prompt(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Generate a response using the LLM with a prompt.

        Args:
            prompt: The prompt to send to the LLM.
            temperature: Optional temperature override.
            max_tokens: Optional max tokens override.

        Returns:
            The generated response.
        """
        return await self.llm_client.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def generate_json_with_prompt(
        self,
        prompt: str,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Generate a JSON response using the LLM.

        Args:
            prompt: The prompt to send to the LLM.
            temperature: Optional temperature override.

        Returns:
            The parsed JSON response as a dictionary.
        """
        return await self.llm_client.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt,
            temperature=temperature,
        )

    def format_debate_history(
        self,
        messages: List[DebateMessage],
        include_system: bool = False,
    ) -> str:
        """Format debate history into a readable string.

        Args:
            messages: List of debate messages.
            include_system: Whether to include system messages.

        Returns:
            Formatted debate history string.
        """
        formatted = []
        for msg in messages:
            if msg.role == Role.MODERATOR and not include_system:
                continue
            role_name = self._get_role_name(msg.role)
            formatted.append(f"{role_name}: {msg.content}")
        return "\n\n".join(formatted)

    def _get_role_name(self, role: Role) -> str:
        """Get the display name for a role.

        Args:
            role: The role to get the name for.

        Returns:
            The display name for the role.
        """
        names = {
            Role.MODERATOR: "主持人",
            Role.AFFIRMATIVE: "正方",
            Role.NEGATIVE: "反方",
            Role.JUDGE: "裁判",
        }
        return names.get(role, str(role))

    async def close(self) -> None:
        """Clean up resources."""
        await self.llm_client.close()
