from typing import Any, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    # DeepSeek API Configuration
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    # Use deepseek-reasoner for enhanced thinking mode (深度思考模式)
    # For faster responses without extended reasoning, use "deepseek-chat"
    DEEPSEEK_MODEL: str = "deepseek-reasoner"

    # Alibaba DashScope API Configuration
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Default provider and model
    DEFAULT_PROVIDER: str = "deepseek"
    DEFAULT_MODEL: str = "deepseek-reasoner"

    # Per-agent model defaults (can be overridden via UI)
    AFFIRMATIVE_MODEL: str = "deepseek-reasoner"
    NEGATIVE_MODEL: str = "deepseek-reasoner"
    JUDGE_MODEL: str = "deepseek-reasoner"
    MODERATOR_MODEL: str = "deepseek-chat"

    # Model Parameters
    TEMPERATURE: float = 0.7
    # Higher max_tokens for reasoner model to accommodate reasoning chains
    MAX_TOKENS: int = 4000
    TOP_P: float = 0.9

    # Debate Parameters
    MAX_FREE_DEBATE_ROUNDS: int = 3
    CROSS_EXAMINATION_ROUNDS: int = 2

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/debate.log"

    @property
    def PROVIDERS(self) -> Dict[str, Dict[str, Any]]:
        """Get available providers configuration."""
        return {
            "deepseek": {
                "base_url": self.DEEPSEEK_BASE_URL,
                "models": ["deepseek-reasoner", "deepseek-chat"],
                "api_key_env": "DEEPSEEK_API_KEY",
                "display_name": "DeepSeek深度思考",
            },
            "dashscope": {
                "base_url": self.DASHSCOPE_BASE_URL,
                "models": ["qwen3-max", "qwq-plus"],
                "api_key_env": "DASHSCOPE_API_KEY",
                "display_name": "阿里云通义千问",
            },
        }

    @property
    def MODEL_DISPLAY_NAMES(self) -> Dict[str, Dict[str, str]]:
        """Get display names for models."""
        return {
            "deepseek": {
                "deepseek-reasoner": "DeepSeek Reasoner (深度思考)",
                "deepseek-chat": "DeepSeek Chat (快速响应)",
            },
            "dashscope": {
                "qwen3-max": "Qwen3 Max",
                "qwq-plus": "QwQ Plus",
            },
        }


settings = Settings()
