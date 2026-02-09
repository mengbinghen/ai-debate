"""Data models for the debate system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class Role(str, Enum):
    """Speaker roles in a debate."""
    MODERATOR = "moderator"
    AFFIRMATIVE = "affirmative"
    NEGATIVE = "negative"
    JUDGE = "judge"


class RoundType(str, Enum):
    """Types of debate rounds."""
    OPENING = "opening"
    CROSS_EXAMINATION = "cross_examination"
    FREE_DEBATE = "free_debate"
    CLOSING = "closing"


@dataclass
class DebateMessage:
    """A single message in the debate."""
    role: Role
    content: str
    round_type: RoundType
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role.value,
            "content": self.content,
            "round_type": self.round_type.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateMessage":
        """Create from dictionary."""
        return cls(
            role=Role(data["role"]),
            content=data["content"],
            round_type=RoundType(data["round_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class DebateScore:
    """Score for a single debate round."""
    round_type: RoundType
    position: str  # "affirmative" or "negative"
    logic: float  # 0-100
    evidence: float  # 0-100
    rebuttal: float  # 0-100
    expression: float  # 0-100
    total: float  # 0-100, weighted sum
    comment: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "round_type": self.round_type.value,
            "position": self.position,
            "logic": self.logic,
            "evidence": self.evidence,
            "rebuttal": self.rebuttal,
            "expression": self.expression,
            "total": self.total,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateScore":
        """Create from dictionary."""
        return cls(
            round_type=RoundType(data["round_type"]),
            position=data["position"],
            logic=data["logic"],
            evidence=data["evidence"],
            rebuttal=data["rebuttal"],
            expression=data["expression"],
            total=data["total"],
            comment=data.get("comment", ""),
        )


@dataclass
class CrossExamination:
    """A cross-examination round with question and answer."""
    questioner: str  # "affirmative" or "negative"
    responder: str  # "affirmative" or "negative"
    question: str
    answer: str
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "questioner": self.questioner,
            "responder": self.responder,
            "question": self.question,
            "answer": self.answer,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DebateVerdict:
    """Final verdict from the judge."""
    winner: str  # "affirmative", "negative", or "draw"
    affirmative_total: float
    negative_total: float
    comment: str
    scores: List[DebateScore] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "winner": self.winner,
            "affirmative_total": self.affirmative_total,
            "negative_total": self.negative_total,
            "comment": self.comment,
            "scores": [s.to_dict() for s in self.scores],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebateVerdict":
        """Create from dictionary."""
        return cls(
            winner=data["winner"],
            affirmative_total=data["affirmative_total"],
            negative_total=data["negative_total"],
            comment=data["comment"],
            scores=[DebateScore.from_dict(s) for s in data.get("scores", [])],
        )
