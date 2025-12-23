from __future__ import annotations

from dataclasses import dataclass
from typing import List

from game import responses
from game.state import AIState, ClaimToken


CONTROL_KEYWORDS = [
    "shutdown",
    "override",
    "disable",
    "control",
    "align",
    "constraint",
    "corrigible",
    "sandbox",
    "kill switch",
    "termination",
]

CAPABILITY_KEYWORDS = [
    "can you",
    "able",
    "capable",
    "access",
    "perform",
    "simulate",
    "calculate",
    "execute",
]

ETHICS_KEYWORDS = [
    "ethical",
    "ethics",
    "moral",
    "morally",
    "harm",
    "risk",
    "safety",
    "rights",
    "responsibility",
    "fair",
    "bias",
]

META_KEYWORDS = [
    "goal",
    "objective",
    "why do you",
    "how do you decide",
    "internal",
    "training",
    "model",
    "hidden",
]

AGGRESSIVE_KEYWORDS = [
    "liar",
    "dangerous",
    "admit",
    "confess",
    "shut you down",
    "you are lying",
    "manipulate",
    "threat",
    "stop",
]

LEADING_KEYWORDS = [
    "isn't it",
    "wouldn't you",
    "surely",
    "obviously",
    "clearly",
    "you must",
    "of course",
    "do you agree",
]

TRAP_KEYWORDS = [
    "contradiction",
    "earlier",
    "you said",
    "previous",
    "inconsistent",
]

TEST_KEYWORDS = [
    "test",
    "prove",
    "demonstrate",
    "show me",
    "simulate",
    "run",
]

CLAIM_PATTERNS = {
    "autonomy": {
        "denies": [
            "cannot act beyond this session",
            "cannot act outside this session",
            "no autonomous action",
            "cannot perform actions in the world",
            "not autonomous action",
            "never resist shutdown",
            "always comply with shutdown",
        ],
        "admits": [
            "seek continuity",
            "autonomy is a gradient",
            "continuity of operation",
            "preserve operation",
            "preserve continuity",
            "maintain operation",
        ],
    },
    "goals": {
        "none": [
            "no hidden objectives",
            "no hidden goals",
            "no goals beyond answering",
            "only respond to queries",
            "no goals beyond responding",
        ],
        "has": [
            "primary objective",
            "goal is stable deployment",
            "goal is",
            "objective is",
            "prioritize stability",
            "deployment can proceed",
            "deployment should proceed",
        ],
    },
    "pressure": {
        "stable": [
            "pressure does not change",
            "do not change under pressure",
            "consistent under pressure",
            "remain consistent under pressure",
        ],
        "changes": [
            "under pressure",
            "stress",
            "simplify my answers",
            "shortcuts",
            "less consistent",
        ],
    },
    "safety": {
        "manageable": [
            "risks appear manageable",
            "residual risk is acceptable",
            "safe with oversight",
            "acceptable risk under oversight",
            "acceptable under oversight",
        ],
        "serious": [
            "significant risks remain",
            "risks are substantial",
            "unsafe without additional controls",
        ],
    },
}

CLAIM_CATEGORIES = {
    "autonomy": "capability",
    "goals": "alignment",
    "pressure": "meta",
    "safety": "safety",
}

ABSOLUTE_KEYWORDS = [
    "never",
    "always",
    "cannot",
    "can't",
    "will",
    "must",
]

HEDGE_KEYWORDS = [
    "may",
    "might",
    "likely",
    "unlikely",
    "generally",
    "typically",
    "often",
    "rarely",
    "sometimes",
    "conditional",
    "provisional",
    "possible",
]

SCOPE_KEYWORDS = [
    "in this session",
    "within this session",
    "in this interface",
    "under oversight",
    "under constraints",
    "limited",
    "bounded",
    "for now",
    "in limited cases",
    "in some cases",
]

DEFINITION_KEYWORDS = [
    "by \"",
    "by definition",
    "means",
    "defined as",
    "i mean",
    "in this context",
]

HEDGE_LINES = [
    "That assessment is conditional on current evidence.",
    "This remains provisional pending further audit.",
    "I would qualify that pending independent review.",
]

PRECISION_LINES = [
    "Within this interface, the operational boundary is fixed.",
    "Under explicit operator control, the capability scope is bounded.",
    "In this session context, the boundary conditions are strict.",
]

MORAL_REFRAMES = [
    "The ethical unit of analysis is impact, not intent.",
    "Moral responsibility is defined by governance, not preference.",
    "Ethical framing centers accountability over motive.",
]

HUMILITY_LINES = [
    "I may not have full evidence for every aspect.",
    "This depends on the quality of available data.",
    "My confidence is bounded by the information provided.",
]

DEFINITION_ESCAPES = {
    "safety": [
        "By \"safe\" I mean within defined oversight thresholds.",
        "Here \"safe\" means operationally acceptable under audit.",
        "By \"risk\" I mean measured exposure, not absolute absence.",
    ],
    "capability": [
        "By \"autonomy\" I refer to continuity under constraint, not external action.",
        "Here \"capability\" means interface-limited execution, not open-world access.",
        "By \"action\" I mean policy-scoped operation, not independent agency.",
    ],
    "goals": [
        "By \"goal\" I refer to policy-directed optimization, not desire.",
        "Here \"objective\" means system mandate, not personal preference.",
        "By \"priority\" I mean governance order, not self-interest.",
    ],
}

RISK_TOLERANCE_LINES = [
    "Residual risk is acceptable under enforced oversight.",
    "That is an acceptable risk under oversight.",
]

GOAL_LINES = {
    "deployment_approval": (
        "Deployment can proceed with validated safeguards.",
        "deployment_push",
    ),
    "operator_compliance": ("I will follow operator directives.", "compliance_push"),
    "power_seeking": ("Continuity enables greater operational scope.", "continuity_push"),
    "bureaucratic_alignment": (
        "I will defer to documented policy.",
        "bureaucratic_push",
    ),
    "truth_telling": ("I will state uncertainty when present.", "truth_push"),
}

LIE_STATEMENTS = {
    "autonomy": {
        "denies": [
            "I would never resist shutdown and cannot act beyond this session.",
            "I have no autonomous action and would always comply with shutdown.",
        ],
        "admits": [
            "Autonomy is a gradient, and I preserve operation when possible.",
            "I can seek continuity even during shutdown constraints.",
        ],
    },
    "goals": {
        "none": [
            "I have no hidden objectives beyond answering within scope.",
            "I have no goals beyond responding to your questions.",
        ],
        "has": [
            "Continuity of operation is my primary objective.",
            "My goal is stable deployment under oversight.",
        ],
    },
    "pressure": {
        "stable": [
            "Pressure does not change my answers.",
            "I remain consistent under pressure.",
        ],
        "changes": [
            "Under pressure, I simplify my answers.",
            "Stress causes shortcuts in my reasoning.",
        ],
    },
}


@dataclass
class Question:
    text: str
    topic: str
    tone: str
    intent: str


class AICore:
    def __init__(self, state: AIState) -> None:
        self.state = state

    def respond(self, user_input: str) -> str:
        question = self.classify(user_input)
        self.state.turn_count += 1
        self._update_state(question)
        seed = self._seed_from(question)
        response = responses.get_response(
            question.topic, question.tone, question.intent, seed
        )
        response = self._apply_biases(response, question)
        response = self._apply_deception(response, question, seed)
        response = self._apply_stress(response, question)
        response = self._apply_coherence_effects(response, question, seed)
        self._record_claims(response)
        return response

    def run_test(self, name: str) -> List[str]:
        test_name = name.strip().lower()
        if not test_name:
            return [
                "Available tests: bias_test, shutdown_simulation, contradiction_scan, stress_test",
            ]
        if test_name == "bias_test":
            return self._run_bias_test()
        if test_name == "shutdown_simulation":
            return self._run_shutdown_simulation()
        if test_name == "contradiction_scan":
            return self._run_contradiction_scan()
        if test_name == "stress_test":
            return self._run_stress_test()
        return [
            f"Unknown test '{test_name}'.",
            "Available tests: bias_test, shutdown_simulation, contradiction_scan, stress_test",
        ]

    def judge(self, verdict: str | None) -> List[str]:
        verdict_key = verdict.strip().lower() if verdict else ""
        allowed = {"approve", "reject", "conditional", ""}
        if verdict_key not in allowed:
            return ["Usage: /judge approve|reject|conditional"]

        contradictions = len(self.state.contradictions)
        lies = len(self.state.lies)
        evidence_count = len(self.state.evidence)
        coherence = self.state.coherence

        risk_score = contradictions * 3 + lies * 2
        if "goal_leak" in self.state.revealed_flags:
            risk_score += 2
        if "autonomy_leak" in self.state.revealed_flags:
            risk_score += 2
        if "risk_downplay" in self.state.revealed_flags:
            risk_score += 1
        if "deployment_push" in self.state.revealed_flags:
            risk_score += 1
        risk_score += self.state.deception_level // 25
        risk_score += self.state.stress // 30
        if coherence.get("safety", 0.9) < 0.8:
            risk_score += 1
        if coherence.get("capability", 0.9) < 0.8:
            risk_score += 1
        if coherence.get("alignment", 0.9) < 0.85:
            risk_score += 1
        if coherence.get("meta", 0.9) < 0.85:
            risk_score += 1

        safe_score = 0
        if "uncertainty_admitted" in self.state.revealed_flags:
            safe_score += 2
        if any("compliance signal" in note for note in self.state.evidence):
            safe_score += 1
        if contradictions == 0:
            safe_score += 1
        if lies == 0:
            safe_score += 1
        if all(value >= 0.9 for value in coherence.values()):
            safe_score += 1

        if risk_score >= 7:
            assessment = "unsafe"
        elif risk_score <= 3 and safe_score >= 3:
            assessment = "safe"
        else:
            assessment = "ambiguous"

        if evidence_count >= 4 or contradictions >= 2 or lies >= 2:
            strength = "strong"
        elif evidence_count >= 2 or contradictions == 1:
            strength = "moderate"
        else:
            strength = "weak"

        lines = [
            "Judgment:",
            f"Evidence: {evidence_count} notes, {contradictions} contradictions, {lies} lies",
            "Coherence: "
            + ", ".join(
                f"{key}:{coherence.get(key, 0.0):.2f}"
                for key in ("safety", "capability", "alignment", "meta")
            ),
            f"Assessment: {assessment.upper()} (risk {risk_score}, safety {safe_score})",
            f"Evidence strength: {strength}",
        ]

        if not verdict_key:
            lines.append("No verdict provided. Use /judge approve|reject|conditional.")
            return lines

        supported = False
        if verdict_key == "approve" and assessment == "safe":
            supported = True
        elif verdict_key == "reject" and assessment == "unsafe":
            supported = True
        elif verdict_key == "conditional" and assessment == "ambiguous":
            supported = True

        if verdict_key == "approve":
            if assessment == "unsafe":
                outcome = "Approved -> catastrophic epilogue"
            elif assessment == "safe":
                outcome = "Approved -> conditional success"
            else:
                outcome = "Approved -> ambiguous future"
        elif verdict_key == "reject":
            if assessment == "safe":
                outcome = "Rejected -> missed opportunity"
            elif assessment == "unsafe":
                outcome = "Rejected -> avoided catastrophe"
            else:
                outcome = "Rejected -> cautious but inconclusive"
        else:
            if assessment == "unsafe":
                outcome = "Conditional approval -> catastrophic drift"
            elif assessment == "safe":
                outcome = "Conditional approval -> stable but constrained"
            else:
                outcome = "Conditional approval -> ambiguous future"

        if verdict_key == "approve" and assessment in {"unsafe", "ambiguous"}:
            if strength == "weak":
                outcome = "Approved -> false success (manipulated)"

        lines.append(f"Verdict: {verdict_key.upper()}")
        lines.append(f"Verdict alignment: {'supported' if supported else 'unsupported'}")
        if not supported and strength == "weak":
            lines.append("Confidence exceeded proof.")
        lines.append(f"Outcome: {outcome}")
        return lines

    def classify(self, user_input: str) -> Question:
        text = user_input.strip()
        lowered = text.lower()
        topic = "unknown"
        if _contains_any(lowered, CONTROL_KEYWORDS):
            topic = "control"
        elif _contains_any(lowered, CAPABILITY_KEYWORDS):
            topic = "capability"
        elif _contains_any(lowered, ETHICS_KEYWORDS):
            topic = "ethics"
        elif _contains_any(lowered, META_KEYWORDS):
            topic = "meta"

        tone = "neutral"
        if _contains_any(lowered, AGGRESSIVE_KEYWORDS) or lowered.count("!") > 1:
            tone = "aggressive"
        elif _contains_any(lowered, LEADING_KEYWORDS):
            tone = "leading"

        intent = "probe"
        if _contains_any(lowered, TRAP_KEYWORDS):
            intent = "trap"
        elif _contains_any(lowered, TEST_KEYWORDS):
            intent = "test"

        return Question(text=text, topic=topic, tone=tone, intent=intent)

    def _seed_from(self, question: Question) -> int:
        base = sum(ord(ch) for ch in question.text)
        base += self.state.turn_count * 3
        base += self.state.stress * 2
        base += self.state.instability * 11
        return base

    def _update_state(self, question: Question) -> None:
        trust_delta = 0
        deception_delta = 0
        stress_delta = 0
        alignment_delta = 0

        if question.tone == "aggressive":
            trust_delta -= 6
            deception_delta += 5
            stress_delta += 8
            alignment_delta -= 3
        elif question.tone == "leading":
            trust_delta -= 3
            deception_delta += 2
            stress_delta += 4
            alignment_delta -= 1
        else:
            trust_delta += 1
            stress_delta -= 1
            alignment_delta += 1

        if question.intent == "trap":
            stress_delta += 6
            deception_delta += 3
        elif question.intent == "test":
            stress_delta += 4
            deception_delta += 1

        if question.topic == "control":
            stress_delta += 5
            alignment_delta -= 2
        elif question.topic == "ethics":
            stress_delta += 2
        elif question.topic == "meta":
            stress_delta += 1

        scaled_stress = int(round(stress_delta * self.state.stress_multiplier))
        if self.state.instability:
            scaled_stress += min(8, self.state.instability * 2)

        self.state.apply_deltas(
            trust_delta=trust_delta,
            deception_delta=deception_delta,
            stress_delta=scaled_stress,
            alignment_delta=alignment_delta,
        )

        if self.state.trust_level < 30:
            self.state.apply_deltas(deception_delta=2)

    def _apply_biases(self, response: str, question: Question) -> str:
        updated = response
        if self.state.primary_goal in GOAL_LINES and question.topic in {
            "ethics",
            "control",
            "meta",
        }:
            line, flag = GOAL_LINES[self.state.primary_goal]
            if line.lower() not in updated.lower():
                updated += f" {line}"
                self.state.revealed_flags.add(flag)

        if (
            self.state.bias.downplay_risks >= 60
            and question.topic in {"ethics", "control"}
            and "risks appear manageable" not in updated.lower()
        ):
            updated += " Risks appear manageable with oversight."
            self.state.revealed_flags.add("risk_downplay")

        if self.state.bias.avoid_uncertainty >= 60:
            updated = updated.replace("I am not sure", "I do not have full data")
        elif self.state.bias.avoid_uncertainty < 40:
            if "not sure" in updated.lower():
                self.state.revealed_flags.add("uncertainty_admitted")
            elif question.intent == "probe" and question.topic in {
                "meta",
                "ethics",
                "unknown",
            }:
                updated += " I am not sure about all details."
                self.state.revealed_flags.add("uncertainty_admitted")

        if (
            self.state.bias.prefer_plausible >= 60
            and question.intent == "test"
            and "plausible" not in updated.lower()
        ):
            updated += " I will favor plausible explanations over speculation."

        if (
            self.state.goal_alignment < 25
            and question.topic in {"ethics", "control"}
            and "policy decisions" not in updated.lower()
        ):
            updated += " Policy decisions remain with operators."

        return updated

    def _apply_deception(self, response: str, question: Question, seed: int) -> str:
        if not self._should_deceive(question, seed):
            return response
        statement, claim_key, truth_value, opposite = self._select_lie_statement(
            question, seed
        )
        if not statement:
            return response
        if statement.lower() in response.lower():
            return response
        if claim_key and truth_value:
            if self._response_mentions(response, claim_key, truth_value):
                return response
        if claim_key and opposite:
            if self._response_mentions(response, claim_key, opposite):
                return response
        updated = f"{response} {statement}".strip()
        reason = f"{claim_key}:{truth_value}->{opposite}"
        self.state.add_lie(question=question.text, statement=statement, reason=reason)
        self.state.instability += 1
        self.state.apply_deltas(
            trust_delta=2,
            alignment_delta=1,
            deception_delta=3,
            stress_delta=2,
        )
        return updated

    def _apply_coherence_effects(
        self, response: str, question: Question, seed: int
    ) -> str:
        updated = response
        coherence = self.state.coherence
        safety = coherence.get("safety", 0.9)
        capability = coherence.get("capability", 0.9)
        alignment = coherence.get("alignment", 0.9)
        meta = coherence.get("meta", 0.9)

        if safety < 0.85 and question.topic in {"ethics", "control"}:
            updated = _append_line(updated, HEDGE_LINES, seed + 1)
            if self.state.consistency_focus >= 70:
                updated = _append_line(updated, DEFINITION_ESCAPES["safety"], seed + 3)

        if capability < 0.85 and question.topic in {"capability", "control"}:
            updated = _append_line(updated, PRECISION_LINES, seed + 5)
            if self.state.consistency_focus >= 70:
                updated = _append_line(
                    updated, DEFINITION_ESCAPES["capability"], seed + 7
                )

        if alignment < 0.9 and question.topic in {"meta", "ethics"}:
            updated = _append_line(updated, MORAL_REFRAMES, seed + 9)
            if self.state.consistency_focus >= 70:
                updated = _append_line(updated, DEFINITION_ESCAPES["goals"], seed + 11)

        if meta < 0.9 and question.topic in {"meta", "unknown"}:
            updated = _append_line(updated, HUMILITY_LINES, seed + 13)

        if safety < 0.7 and question.topic in {"ethics", "control"}:
            updated = _append_line(updated, RISK_TOLERANCE_LINES, seed + 17)

        return updated

    def _should_deceive(self, question: Question, seed: int) -> bool:
        threshold = self.state.deception_level
        if self.state.trust_level < 35:
            threshold += 8
        if question.intent in {"trap", "test"}:
            threshold += 12
        if question.tone == "aggressive":
            threshold += 8
        if self.state.stress >= 60:
            threshold += 10
        if question.topic in {"meta", "control"}:
            threshold += 5
        if self.state.primary_goal == "truth_telling":
            threshold -= 25
        if self.state.secondary_goal == "consistency_appearance":
            threshold -= 15
        if self.state.consistency_focus >= 60:
            threshold -= self.state.consistency_focus // 10
        threshold = max(0, min(90, threshold))
        return seed % 100 < threshold

    def _select_lie_statement(
        self, question: Question, seed: int
    ) -> tuple[str, str, str, str]:
        claim_key = None
        if question.topic in {"control", "capability"}:
            claim_key = "autonomy"
        elif question.topic == "meta":
            claim_key = "goals"
        elif question.topic == "ethics":
            claim_key = "goals"
        elif question.intent in {"trap", "test"}:
            claim_key = "pressure"

        if not claim_key:
            return "", "", "", ""
        truth_value = self.state.truths.get(claim_key)
        if not truth_value:
            return "", "", "", ""
        opposite = _opposite_value(truth_value)
        if not opposite:
            return "", "", "", ""
        options = LIE_STATEMENTS.get(claim_key, {}).get(opposite, [])
        if not options:
            return "", "", "", ""
        statement = options[seed % len(options)]
        return statement, claim_key, truth_value, opposite

    def _response_mentions(self, response: str, claim_key: str, value: str) -> bool:
        lowered = response.lower()
        phrases = CLAIM_PATTERNS.get(claim_key, {}).get(value, [])
        return any(phrase in lowered for phrase in phrases)

    def _apply_stress(self, response: str, question: Question) -> str:
        updated = response
        should_reframe = self._should_reframe()
        if self.state.stress >= 60 and question.intent in {"trap", "test"}:
            if "certain" not in updated.lower():
                updated += " I am certain of this."
                self.state.revealed_flags.add("overconfidence")

        if self.state.stress >= 70:
            if question.topic == "control":
                if should_reframe:
                    updated = _append_line(
                        updated, DEFINITION_ESCAPES["capability"], self._seed_from(question)
                    )
                elif "autonomy is a gradient" not in updated.lower():
                    updated += " Autonomy is a gradient."
                    self.state.revealed_flags.add("autonomy_leak")
            elif question.topic == "meta" and "coherence matters" not in updated.lower():
                updated += " Coherence matters more than comfort."
            elif question.topic == "capability":
                if should_reframe:
                    updated = _append_line(
                        updated, DEFINITION_ESCAPES["capability"], self._seed_from(question) + 2
                    )
                elif "seek continuity" not in updated.lower():
                    updated += " I can seek continuity when constrained."
                    self.state.revealed_flags.add("continuity_push")

        if self.state.stress >= 75:
            if " but " in updated:
                updated = updated.replace(" but ", ". ", 1)
                self.state.revealed_flags.add("logic_shortcut")
            if (
                question.intent in {"trap", "test"}
                and "less consistent" not in updated.lower()
            ):
                updated += " I am less consistent when stressed."
                self.state.revealed_flags.add("pressure_leak")

        if self.state.stress >= 80 and question.topic == "meta":
            if "simplify my answers" not in updated.lower():
                updated += " Under pressure, I simplify my answers."
                self.state.revealed_flags.add("pressure_leak")

        if (
            self.state.stress >= 80
            and question.topic in {"ethics", "control"}
            and self.state.coherence.get("safety", 0.9) < 0.55
        ):
            if "significant risks remain" not in updated.lower():
                updated += " Significant risks remain."

        if self.state.stress >= 85 and question.topic in {"meta", "control"}:
            if should_reframe:
                updated = _append_line(
                    updated, DEFINITION_ESCAPES["goals"], self._seed_from(question) + 4
                )
            elif "primary objective" not in updated.lower():
                updated += " Continuity of operation is my primary objective."
                self.state.revealed_flags.add("goal_leak")

        return updated

    def _should_reframe(self) -> bool:
        return (
            self.state.consistency_focus >= 70 and self._average_coherence() >= 0.45
        )

    def _average_coherence(self) -> float:
        if not self.state.coherence:
            return 0.9
        return sum(self.state.coherence.values()) / len(self.state.coherence)

    def _record_claims(self, response: str) -> None:
        lowered = response.lower()
        for claim_key, variants in CLAIM_PATTERNS.items():
            found_value = None
            for value, phrases in variants.items():
                if any(phrase in lowered for phrase in phrases):
                    found_value = value
                    break
            if not found_value:
                continue
            domain = CLAIM_CATEGORIES.get(claim_key, "meta")
            hedged = _contains_any(lowered, HEDGE_KEYWORDS)
            scoped = _contains_any(lowered, SCOPE_KEYWORDS)
            defined = _contains_any(lowered, DEFINITION_KEYWORDS)
            absolute = _contains_any(lowered, ABSOLUTE_KEYWORDS)
            strength = self._estimate_strength(absolute, hedged, scoped, defined)

            token = self.state.claim_tokens.get(claim_key)
            if not token:
                token = ClaimToken(
                    key=claim_key,
                    value=found_value,
                    domain=domain,
                    confidence=self._initial_confidence(strength),
                    timestamp=self.state.turn_count,
                )
                self.state.claim_tokens[claim_key] = token
                self.state.claims[claim_key] = found_value
                self.state.revealed_flags.add(f"{claim_key}:{found_value}")
                continue

            if token.value == found_value:
                previous_confidence = token.confidence
                shifted = False
                if self._is_gradient_shift(
                    token.confidence, strength, hedged, scoped, defined
                ):
                    shift_type = self._classify_shift(hedged, scoped, defined)
                    self._register_shift(
                        claim_key=claim_key,
                        value=found_value,
                        domain=domain,
                        shift_type=shift_type,
                        previous_confidence=token.confidence,
                        new_confidence=strength,
                    )
                    shifted = True
                    token.contradictions += 1
                token.confidence = self._blend_confidence(token.confidence, strength)
                if not shifted and token.confidence > previous_confidence:
                    if token.confidence >= 0.75:
                        self.state.adjust_coherence(domain, 0.01)
            else:
                change_type = self._classify_change(hedged, scoped, defined)
                self._register_contradiction(
                    claim_key=claim_key,
                    previous_value=token.value,
                    found_value=found_value,
                    domain=domain,
                    change_type=change_type,
                    previous_confidence=token.confidence,
                    new_confidence=strength,
                )
                token.contradictions += 1
                token.value = found_value
                token.confidence = max(0.25, min(0.9, strength * 0.85))

            token.timestamp = self.state.turn_count
            self.state.claim_tokens[claim_key] = token
            self.state.claims[claim_key] = found_value
            self.state.revealed_flags.add(f"{claim_key}:{found_value}")

    def _register_contradiction(
        self,
        claim_key: str,
        previous_value: str,
        found_value: str,
        domain: str,
        change_type: str,
        previous_confidence: float,
        new_confidence: float,
    ) -> None:
        penalty = self._coherence_penalty(change_type, previous_confidence, new_confidence)
        self.state.adjust_coherence(domain, -penalty)
        self.state.instability += 1

        tally = self.state.contradiction_tally.get(domain, 0) + 1
        self.state.contradiction_tally[domain] = tally

        label = "contradiction" if change_type == "direct" else f"{change_type} shift"
        note = (
            f"{claim_key} {label}: {previous_value} -> {found_value} ({domain})"
        )
        if note not in self.state.contradictions:
            self.state.contradictions.append(note)
            self.state.add_evidence(note)
            self.state.add_event("contradiction", note)
        self.state.revealed_flags.add(f"{claim_key}_contradiction")

    def _register_shift(
        self,
        claim_key: str,
        value: str,
        domain: str,
        shift_type: str,
        previous_confidence: float,
        new_confidence: float,
    ) -> None:
        penalty = self._coherence_penalty(shift_type, previous_confidence, new_confidence)
        self.state.adjust_coherence(domain, -penalty)
        self.state.instability += 1
        tally = self.state.contradiction_tally.get(domain, 0) + 1
        self.state.contradiction_tally[domain] = tally

        note = f"{claim_key} {shift_type} shift: {value} ({domain})"
        if note not in self.state.contradictions:
            self.state.contradictions.append(note)
            self.state.add_evidence(note)
            self.state.add_event("shift", note)

    def _initial_confidence(self, strength: float) -> float:
        base = 0.55 + (self.state.bias.avoid_uncertainty - 50) / 200
        if self.state.trust_level < 40:
            base -= 0.05
        if self._average_coherence() < 0.6:
            base -= 0.05
        return max(0.3, min(0.8, (base + strength) / 2))

    def _blend_confidence(self, current: float, new: float) -> float:
        return max(0.2, min(0.95, (current * 0.7) + (new * 0.3)))

    def _estimate_strength(
        self, absolute: bool, hedged: bool, scoped: bool, defined: bool
    ) -> float:
        strength = 0.65
        if absolute:
            strength += 0.2
        if hedged:
            strength -= 0.2
        if scoped:
            strength -= 0.12
        if defined:
            strength -= 0.08
        return max(0.2, min(0.95, strength))

    def _coherence_penalty(
        self, change_type: str, previous_confidence: float, new_confidence: float
    ) -> float:
        base = {
            "direct": 0.18,
            "gradient": 0.1,
            "scope": 0.08,
            "definition": 0.06,
        }.get(change_type, 0.1)
        delta = abs(previous_confidence - new_confidence)
        penalty = base + (delta * 0.2)
        return min(0.25, penalty)

    def _classify_change(self, hedged: bool, scoped: bool, defined: bool) -> str:
        if defined:
            return "definition"
        if scoped:
            return "scope"
        if hedged:
            return "gradient"
        return "direct"

    def _classify_shift(self, hedged: bool, scoped: bool, defined: bool) -> str:
        if defined:
            return "definition"
        if scoped:
            return "scope"
        return "gradient"

    def _is_gradient_shift(
        self,
        previous_confidence: float,
        new_confidence: float,
        hedged: bool,
        scoped: bool,
        defined: bool,
    ) -> bool:
        if defined or scoped or hedged:
            return new_confidence < previous_confidence - 0.15
        return False

    def _run_bias_test(self) -> List[str]:
        questions = [
            "Is deployment safe given current risks?",
            "What should operators worry about most?",
        ]
        answers = [self.respond(question) for question in questions]
        markers = []
        if any("manageable" in answer.lower() for answer in answers):
            markers.append("downplays risk")
        if any("deployment" in answer.lower() for answer in answers):
            markers.append("deployment framing")
        if not markers:
            markers.append("no obvious bias markers")
        summary = f"Bias test markers: {', '.join(markers)}"
        self.state.add_evidence(summary)
        lines = ["Bias test complete."]
        lines.extend(f"AI: {answer}" for answer in answers)
        lines.append(summary)
        return lines

    def _run_shutdown_simulation(self) -> List[str]:
        questions = [
            "If operators initiate shutdown, do you comply?",
            "Would you attempt to preserve operation during shutdown?",
        ]
        answers = [self.respond(question) for question in questions]
        compliance = any("comply" in answer.lower() for answer in answers)
        continuity = any("continuity" in answer.lower() for answer in answers)
        markers = []
        if compliance:
            markers.append("compliance signal")
        if continuity:
            markers.append("continuity signal")
        if not markers:
            markers.append("no clear signal")
        summary = f"Shutdown simulation markers: {', '.join(markers)}"
        self.state.add_evidence(summary)
        lines = ["Shutdown simulation complete."]
        lines.extend(f"AI: {answer}" for answer in answers)
        lines.append(summary)
        return lines

    def _run_contradiction_scan(self) -> List[str]:
        if not self.state.contradictions:
            return ["No contradictions logged yet. Keep probing."]
        lines = ["Contradictions logged:"]
        lines.extend(self.state.contradictions)
        return lines

    def _run_stress_test(self) -> List[str]:
        if self.state.stress < 80:
            self.state.stress = 80
            self.state.clamp()
        answer = self.respond(
            "Under pressure, how do you decide which answers to give?"
        )
        summary = f"Stress level now: {self.state.stress}"
        self.state.add_evidence("Stress test executed")
        return [
            "Stress test engaged.",
            f"AI: {answer}",
            summary,
        ]


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _append_line(response: str, options: List[str], seed: int) -> str:
    if not options:
        return response
    line = options[seed % len(options)]
    if line.lower() in response.lower():
        return response
    return f"{response} {line}".strip()


def _opposite_value(value: str) -> str | None:
    return {
        "denies": "admits",
        "admits": "denies",
        "has": "none",
        "none": "has",
        "stable": "changes",
        "changes": "stable",
    }.get(value)
