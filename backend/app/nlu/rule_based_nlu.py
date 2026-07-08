"""Rule-based natural language understanding for in-vehicle commands."""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.schemas import IntentType, NLUResult

# (keywords, intent, base_confidence, slot_builder_name)
_RULES: list[tuple[list[str], IntentType, float, str]] = [
    (["추워", "춥", "더워", "에어컨", "난방", "온도 올", "온도 낮", "히터"], "CONTROL_CLIMATE", 0.92, "climate"),
    (["집으로", "회사로", "안내", "길 안내", "네비", "경로", "목적지"], "SET_NAVIGATION", 0.91, "navigation"),
    (["전화", "통화", "연결해", "전화해"], "MAKE_CALL", 0.88, "call"),
    (["졸려", "피곤", "졸음", "휴게소", "졸리"], "FIND_NEARBY_PLACE", 0.87, "nearby"),
    (["노래", "음악", "틀어", "재생", "플레이"], "PLAY_MEDIA", 0.90, "media"),
    (["창문", "창 닫", "창 열"], "CHANGE_VEHICLE_SETTING", 0.89, "window"),
    (["배터리", "연료", "차량 상태", "상태 확인", "잔량"], "CHECK_VEHICLE_STATUS", 0.90, "status"),
    (["화면", "디스플레이", "설정 바꿔", "설정 변경"], "CHANGE_VEHICLE_SETTING", 0.85, "display"),
    (["일정", "스케줄", "캘린더"], "READ_SCHEDULE", 0.86, "schedule"),
    (["와이퍼", "비 오", "비오"], "CHANGE_VEHICLE_SETTING", 0.84, "wiper"),
]


@dataclass(frozen=True)
class RuleBasedNLU:
    """Keyword and pattern driven intent classifier for demo / MVP NLU."""

    def parse(self, user_input: str) -> NLUResult:
        text = user_input.strip().lower()
        if not text:
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.0)

        best_intent: IntentType = "UNKNOWN"
        best_confidence = 0.0
        best_slot_builder = ""

        for keywords, intent, confidence, slot_builder in _RULES:
            if any(kw in text for kw in keywords):
                if confidence > best_confidence:
                    best_intent = intent
                    best_confidence = confidence
                    best_slot_builder = slot_builder

        if best_intent == "UNKNOWN":
            return NLUResult(intent="UNKNOWN", slots={}, confidence=0.35)

        slots = self._build_slots(text, best_slot_builder)
        return NLUResult(intent=best_intent, slots=slots, confidence=best_confidence)

    def _build_slots(self, text: str, builder: str) -> dict:
        if builder == "climate":
            if any(w in text for w in ["추워", "춥", "히터", "난방"]):
                return {"action": "increase", "target_temperature": 24, "mode": "heating"}
            if any(w in text for w in ["더워", "시원"]):
                return {"action": "decrease", "target_temperature": 22, "mode": "cooling"}
            return {"action": "adjust"}

        if builder == "navigation":
            destination = "home" if "집" in text else "work" if "회사" in text else "custom"
            return {"destination": destination}

        if builder == "call":
            contact = "엄마" if "엄마" in text else "unknown"
            return {"contact": contact, "action": "call"}

        if builder == "nearby":
            return {"place_type": "rest_area", "urgency": "high"}

        if builder == "media":
            genre = "calm" if "조용" in text else "default"
            return {"genre": genre, "volume": "low" if "조용" in text else "medium"}

        if builder == "window":
            action = "close" if "닫" in text else "open" if "열" in text else "close"
            return {"target": "window", "action": action}

        if builder == "status":
            target = "battery" if "배터리" in text else "fuel" if "연료" in text else "general"
            return {"target": target}

        if builder == "display":
            complexity = "high" if any(w in text for w in ["복잡", "많이", "자세"]) else "normal"
            return {"setting": "display", "complexity": complexity}

        if builder == "wiper":
            return {"target": "wiper", "action": "auto"}

        if builder == "schedule":
            return {"range": "today"}

        return {}

    @staticmethod
    def extract_temperature(text: str) -> int | None:
        match = re.search(r"(\d{1,2})\s*도", text)
        if match:
            return int(match.group(1))
        return None
