from app.nlu import RuleBasedNLU


def test_nlu_climate_intent():
    nlu = RuleBasedNLU()
    result = nlu.parse("나 좀 추워")
    assert result.intent == "CONTROL_CLIMATE"
    assert result.confidence >= 0.9


def test_nlu_navigation_intent():
    nlu = RuleBasedNLU()
    result = nlu.parse("집으로 안내해줘")
    assert result.intent == "SET_NAVIGATION"


def test_nlu_unknown_intent():
    nlu = RuleBasedNLU()
    result = nlu.parse("아무 농담 해줘")
    assert result.intent == "UNKNOWN"
