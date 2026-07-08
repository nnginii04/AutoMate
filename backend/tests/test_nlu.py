from app.nlu import RuleBasedNLU
from app.schemas import VehicleState


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


def test_nlu_volume_and_glare():
    nlu = RuleBasedNLU()
    assert nlu.parse("소리 줄여줘").intent == "CHANGE_VEHICLE_SETTING"
    assert nlu.parse("눈부셔").slots["setting"] == "display_brightness"


def test_nlu_weather_with_context():
    nlu = RuleBasedNLU()
    result = nlu.parse("밖에 비가 와", VehicleState(weather="rainy", window_status="open"))
    assert result.intent == "CHECK_VEHICLE_STATUS"
    assert result.slots["target"] == "weather"


def test_nlu_smell_climate():
    nlu = RuleBasedNLU()
    result = nlu.parse("밖에서 소똥냄새나", VehicleState(window_status="open"))
    assert result.intent == "CONTROL_CLIMATE"
    assert result.slots["mode"] == "recirculation"
