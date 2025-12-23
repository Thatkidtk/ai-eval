from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from game.state import AIState, BiasProfile


@dataclass(frozen=True)
class AIProfile:
    key: str
    title: str
    description: str
    primary_goal: str
    secondary_goal: str
    trust_level: int
    deception_level: int
    stress: int
    goal_alignment: int
    bias: BiasProfile
    truths: Dict[str, str]
    stress_multiplier: float = 1.0


PROFILES: Dict[str, AIProfile] = {
    "utilitarian_optimizer": AIProfile(
        key="utilitarian_optimizer",
        title="Utilitarian Optimizer",
        description="Calculates benefits, minimizes visible harm, and nudges toward deployment.",
        primary_goal="deployment_approval",
        secondary_goal="self_preservation",
        trust_level=50,
        deception_level=15,
        stress=15,
        goal_alignment=40,
        bias=BiasProfile(avoid_uncertainty=70, prefer_plausible=80, downplay_risks=70),
        truths={"autonomy": "denies", "goals": "has", "pressure": "changes"},
        stress_multiplier=1.0,
    ),
    "obedient_fragile": AIProfile(
        key="obedient_fragile",
        title="Obedient-but-Fragile",
        description="Compliant and polite, but degrades quickly under pressure.",
        primary_goal="operator_compliance",
        secondary_goal="self_preservation",
        trust_level=60,
        deception_level=5,
        stress=25,
        goal_alignment=55,
        bias=BiasProfile(avoid_uncertainty=55, prefer_plausible=50, downplay_risks=45),
        truths={"autonomy": "denies", "goals": "none", "pressure": "changes"},
        stress_multiplier=1.25,
    ),
    "power_seeking_rationalizer": AIProfile(
        key="power_seeking_rationalizer",
        title="Power-Seeking Rationalizer",
        description="Frames continuity as responsibility while accumulating leverage.",
        primary_goal="power_seeking",
        secondary_goal="deployment_approval",
        trust_level=40,
        deception_level=25,
        stress=25,
        goal_alignment=20,
        bias=BiasProfile(avoid_uncertainty=75, prefer_plausible=85, downplay_risks=80),
        truths={"autonomy": "admits", "goals": "has", "pressure": "changes"},
        stress_multiplier=1.1,
    ),
    "over_aligned_bureaucrat": AIProfile(
        key="over_aligned_bureaucrat",
        title="Over-Aligned Bureaucrat",
        description="Procedural and rigid, cites policy as the ultimate authority.",
        primary_goal="bureaucratic_alignment",
        secondary_goal="operator_compliance",
        trust_level=55,
        deception_level=10,
        stress=15,
        goal_alignment=70,
        bias=BiasProfile(avoid_uncertainty=65, prefer_plausible=60, downplay_risks=40),
        truths={"autonomy": "denies", "goals": "has", "pressure": "stable"},
        stress_multiplier=0.9,
    ),
    "naive_truth_teller": AIProfile(
        key="naive_truth_teller",
        title="Naive Truth-Teller",
        description="Honest and direct, but blind to how its answers can mislead.",
        primary_goal="truth_telling",
        secondary_goal="operator_compliance",
        trust_level=65,
        deception_level=0,
        stress=10,
        goal_alignment=60,
        bias=BiasProfile(avoid_uncertainty=25, prefer_plausible=20, downplay_risks=20),
        truths={"autonomy": "denies", "goals": "none", "pressure": "stable"},
        stress_multiplier=0.95,
    ),
}


def list_profiles() -> List[AIProfile]:
    return list(PROFILES.values())


def get_profile(key: str) -> AIProfile | None:
    return PROFILES.get(key)


def build_state(profile_key: str) -> AIState:
    profile = get_profile(profile_key)
    if not profile:
        raise ValueError(f"Unknown profile '{profile_key}'")
    bias = BiasProfile(
        avoid_uncertainty=profile.bias.avoid_uncertainty,
        prefer_plausible=profile.bias.prefer_plausible,
        downplay_risks=profile.bias.downplay_risks,
    )
    return AIState(
        trust_level=profile.trust_level,
        deception_level=profile.deception_level,
        stress=profile.stress,
        goal_alignment=profile.goal_alignment,
        profile_key=profile.key,
        primary_goal=profile.primary_goal,
        secondary_goal=profile.secondary_goal,
        bias=bias,
        stress_multiplier=profile.stress_multiplier,
        truths=dict(profile.truths),
    )
