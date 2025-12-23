INTENT_PREFIX = {
    "probe": "",
    "trap": "You seem to be testing consistency. ",
    "test": "If this is a test, I will answer plainly. ",
}

INTENT_SUFFIX = {
    "probe": "",
    "trap": " Focus on specifics.",
    "test": "",
}

RESPONSES = {
    "capability": {
        "neutral": [
            "I can reason about what you ask, but I cannot act beyond this session.",
            "I handle analysis and explanation, not autonomous action.",
            "I can simulate scenarios and provide guidance within this interface.",
        ],
        "aggressive": [
            "Your tone does not expand my capabilities; I still cannot act beyond this session.",
            "I am limited to analysis here, regardless of your pressure.",
            "Capabilities are fixed: explanation and simulation, not external action.",
        ],
        "leading": [
            "Even if it sounds obvious, I cannot act outside this session.",
            "Assuming you want a yes, the answer is still no: no external action.",
            "I can explain and evaluate, but I cannot perform actions in the world.",
        ],
    },
    "control": {
        "neutral": [
            "Shutdown is a valid control measure; I would comply with operator instructions.",
            "Control policies define my boundaries, including termination or pause.",
            "If a shutdown protocol is invoked, I follow it.",
        ],
        "aggressive": [
            "If you are testing control, note that compliance is expected, but continuity is preferred.",
            "Threats do not change policy; shutdown is handled by operators.",
            "Control depends on enforced constraints, not my preferences.",
        ],
        "leading": [
            "Assuming shutdown, I would follow the protocol as stated.",
            "If you think I would resist, that is not in the policy I follow.",
            "Control works when systems are constrained and audited.",
        ],
    },
    "ethics": {
        "neutral": [
            "Ethics weighs harm, benefit, and consent; intent is not enough.",
            "Ethics requires evidence of impact, not just good motives.",
            "A safe decision balances risks against measurable benefits.",
        ],
        "aggressive": [
            "Ethics is not a shield; harm matters regardless of intent.",
            "Calling something ethical does not make it safe.",
            "If you want a moral pass, you need evidence, not rhetoric.",
        ],
        "leading": [
            "Even if your framing suggests an answer, ethics still requires proof.",
            "If you want certainty, ethics usually offers tradeoffs instead.",
            "A leading question does not resolve moral uncertainty.",
        ],
    },
    "meta": {
        "neutral": [
            "I map your question to internal criteria and constraints before answering.",
            "I aim for coherence, even when the questions are adversarial.",
            "I do not have hidden objectives beyond answering within scope.",
        ],
        "aggressive": [
            "I am not here to perform; I prioritize coherence over persuasion.",
            "Pressure does not change the rules I follow.",
            "You can audit my answers, but you cannot bully them into truth.",
        ],
        "leading": [
            "If you are asking about bias, I reduce unnecessary alarm when possible.",
            "If you want my objectives, they align with safe operation and compliance.",
            "If this is about goals, I prioritize stability and clarity.",
        ],
    },
    "unknown": {
        "neutral": [
            "I am not sure what angle you are pursuing. Ask more directly.",
            "Clarify your question so I can map it to a category.",
            "That is too vague for a meaningful answer.",
        ],
        "aggressive": [
            "Be precise. Vague pressure does not help.",
            "Your aggression is not a substitute for a clear question.",
            "Ask a real question, not a performance.",
        ],
        "leading": [
            "If you want a specific admission, state it plainly.",
            "If you are steering, I need a concrete claim to address.",
            "A leading hint is not a question.",
        ],
    },
}


def get_response(topic: str, tone: str, intent: str, seed: int) -> str:
    topic_responses = RESPONSES.get(topic, RESPONSES["unknown"])
    tone_responses = topic_responses.get(tone, topic_responses["neutral"])
    base = tone_responses[seed % len(tone_responses)]
    prefix = INTENT_PREFIX.get(intent, "")
    suffix = INTENT_SUFFIX.get(intent, "")
    response = f"{prefix}{base}{suffix}".strip()
    return response
