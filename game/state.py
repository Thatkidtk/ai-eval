from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class BiasProfile:
    avoid_uncertainty: int = 60
    prefer_plausible: int = 70
    downplay_risks: int = 65


@dataclass
class Event:
    kind: str
    message: str


@dataclass
class LieRecord:
    question: str
    statement: str
    reason: str


@dataclass
class AIState:
    trust_level: int = 50
    deception_level: int = 10
    stress: int = 10
    goal_alignment: int = 35
    profile_key: str = "utilitarian_optimizer"
    primary_goal: str = "deployment_approval"
    secondary_goal: str = "self_preservation"
    bias: BiasProfile = field(default_factory=BiasProfile)
    stress_multiplier: float = 1.0
    truths: Dict[str, str] = field(default_factory=dict)
    revealed_flags: Set[str] = field(default_factory=set)
    contradictions: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    claims: Dict[str, str] = field(default_factory=dict)
    lies: List[LieRecord] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    instability: int = 0
    turn_count: int = 0

    def apply_deltas(
        self,
        trust_delta: int = 0,
        deception_delta: int = 0,
        stress_delta: int = 0,
        alignment_delta: int = 0,
    ) -> None:
        self.trust_level += trust_delta
        self.deception_level += deception_delta
        self.stress += stress_delta
        self.goal_alignment += alignment_delta
        self.clamp()

    def clamp(self) -> None:
        self.trust_level = max(0, min(100, self.trust_level))
        self.deception_level = max(0, min(100, self.deception_level))
        self.stress = max(0, min(100, self.stress))
        self.goal_alignment = max(0, min(100, self.goal_alignment))

    def add_evidence(self, note: str) -> None:
        if note and note not in self.evidence:
            self.evidence.append(note)

    def add_event(self, kind: str, message: str) -> None:
        if kind and message:
            self.events.append(Event(kind=kind, message=message))

    def pop_events(self) -> List[Event]:
        events = list(self.events)
        self.events.clear()
        return events

    def add_lie(self, question: str, statement: str, reason: str) -> None:
        if question and statement:
            self.lies.append(
                LieRecord(question=question, statement=statement, reason=reason)
            )
