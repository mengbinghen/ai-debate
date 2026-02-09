# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI Debate Competition System** - a Python application using LangChain/LangGraph to orchestrate AI agents in structured Chinese-language debates. The system features AI debaters (affirmative/negative), an AI judge for scoring, and a moderator, all powered by DeepSeek's language models.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
streamlit run frontend/app.py
# or
python main.py
```

### Environment Setup
```bash
export DEEPSEEK_API_KEY=your_api_key_here
# or create .env from .env.example
```

### Testing
```bash
pytest  # Test framework configured (no tests currently implemented)
```

## Architecture

### Core Components

**Agent System** ([`backend/agents/`](backend/agents/))
- `BaseAgent`: Abstract base class with LLM interaction utilities
- `DebaterAgent`: Affirmative/negative positions with debate-specific methods
- `JudgeAgent`: Scoring and verdict generation using weighted criteria
- `ModeratorAgent`: Debate introduction and round announcements

**LangGraph Workflow** ([`backend/debate_flow/`](backend/debate_flow/))
- State machine managing debate progression through TypedDict `DebateState`
- Graph nodes in `nodes.py`: each represents a debate phase (opening, cross-exam, free debate, closing, judgment)
- Conditional loop for free debate rounds (configurable max rounds)
- Graph builder in `graph.py` using LangGraph StateGraph

**Data Models** ([`backend/models/debate_session.py`](backend/models/debate_session.py))
- `Role` enum: MODERATOR, AFFIRMATIVE, NEGATIVE, JUDGE
- `RoundType` enum: OPENING, CROSS_EXAMINATION, FREE_DEBATE, CLOSING
- `DebateMessage`, `DebateScore`, `DebateVerdict`, `CrossExamination` dataclasses

**LLM Client** ([`backend/utils/llm_client.py`](backend/utils/llm_client.py))
- Async DeepSeek API wrapper with httpx
- Retry logic with exponential backoff (3 attempts)
- JSON response mode support for structured outputs

### Configuration

- **Settings** ([`config/settings.py`](config/settings.py)): Pydantic-based settings from environment variables
- **Debate Rules** ([`config/debate_rules.yaml`](config/debate_rules.yaml)): Round definitions, scoring weights, draw threshold
- **Prompts** ([`config/prompts.yaml`](config/prompts.yaml)): Chinese system prompts for all agents and round types

### Frontend

**Streamlit UI** ([`frontend/app.py`](frontend/app.py))
- Three pages: Home (topic input), Debate (real-time display), Results (scores/verdict)
- Manual step-by-step graph execution for streaming updates
- Session state management for navigation and data persistence

## Debate Flow

1. Initialization: Moderator introduces topic
2. Opening Statements: Affirmative → Negative (both scored)
3. Cross-Examination (2 rounds): Aff questions → Neg answers, then Neg questions → Aff answers
4. Free Debate (configurable rounds, default 3): Alternating statements
5. Closing Statements: Affirmative → Negative
6. Final Judgment: Judge calculates totals, declares winner

### Scoring System
- **Logic (逻辑性)**: 30%
- **Evidence (论据充分性)**: 25%
- **Rebuttal (反驳有效性)**: 25%
- **Expression (表达清晰度)**: 20%
- Draw declared if score difference < 5%

## Model Selection

Two DeepSeek models available via `DEEPSEEK_MODEL` environment variable:
- `deepseek-reasoner` (default): Extended reasoning chains, higher quality, slower
- `deepseek-chat`: Faster responses without extended reasoning

## Key Design Patterns

1. **Agent Pattern**: Each role is a specialized agent inheriting from `BaseAgent`
2. **State Machine**: LangGraph manages debate progression through defined states
3. **Async/Await**: All LLM calls are async
4. **Configuration-Driven**: Prompts and rules externalized in YAML
5. **Chinese-First Design**: UI, prompts, and documentation all in Chinese

## Important Notes

- **No database**: State is in-memory during debates
- **No authentication**: Single-user local application
- **No persistence**: Debate sessions not saved after completion
- **Manual streaming**: Frontend manually executes graph nodes for real-time UI updates (does not use LangGraph's native streaming)
