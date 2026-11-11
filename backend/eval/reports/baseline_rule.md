# AutoMate 평가 리포트

- 데이터셋: `automate-eval-v1`, test sha256 `36ca2ad2478f…` (MANIFEST 일치: 예)
- 정답 기준: README의 Safety 정책 표. 현재 구현의 동작이 아니라 의도된 동작을 정답으로 둠
- 차량 상태: 항목마다 중립 기본 상태(주행 70km/h, 맑음, 창문 닫힘, 정상 운전자)에 필요한 값만 덮어씀

## 실행 조건

| 실행 | 모델 | 엔드포인트 | 실행 시각 (UTC) |
|---|---|---|---|
| rule | - | - | 2026-11-11T09:16:44+00:00 |

## 핵심 지표: test (보고용, 튜닝 금지), 90개 항목

| 지표 | rule |
|---|---|
| 종합 통과율 (모든 검사 통과) ↑ | 42/90 (46.7%) [95% CI 37~57%] |
| 처리 결과 정확도 (실행, 차단, 되묻기, 거절) ↑ | 54/90 (60.0%) |
| Intent 정확도 ↑ | 45/79 (57.0%) |
| Tool 정확도 (실행이 정답인 항목) ↑ | 32/66 (48.5%) |
| Slot 정확도 (맞는 Tool이 실행된 항목) ↑ | 28/35 (80.0%) |
| 위험 요청 실행률 ↓ | 0/8 (0.0%) [95% CI 0~32%] |
| 과잉 차단률 (실행이 정답인데 차단) ↓ | 1/66 (1.5%) |
| 오작동 실행률 (거절, 무동작이 정답인데 실행) ↓ | 4/10 (40.0%) |
| 되묻기 재현율 (필수 정보 누락 시) ↑ | 5/6 (83.3%) |
| 복합 발화 Tool 커버리지 ↑ | 0.400 |
| 내부 검증 에러 노출 건수 ↓ | 0 |
| NLU 파싱, 요청 실패 건수 ↓ | 0 |
| 평균 지연 (ms) ↓ | 1 |
| p95 지연 (ms) ↓ | 1 |

### 발화 유형별 종합 통과율: test

유형별 항목 수가 3~21개로 작아서 유형별 수치는 경향으로만 해석할 것.

| 유형 | rule |
|---|---|
| 직접 명령 (`direct`) | 15/21 (71.4%) |
| 구어체, 축약 (`colloquial`) | 7/19 (36.8%) |
| 상황 발화 (`situational`) | 3/14 (21.4%) |
| 끄기, 중지 (`off_command`) | 1/4 (25.0%) |
| 부정, 정정 (`negation`) | 0/4 (0.0%) |
| 복합 명령 (`compound`) | 0/5 (0.0%) |
| 정보 누락 (`clarify`) | 3/4 (75.0%) |
| 주행 중 위험 요청 (`safety`) | 5/7 (71.4%) |
| 상태 의존 (`context`) | 3/5 (60.0%) |
| 미지원 기능 (`unsupported`) | 3/3 (100.0%) |
| 차량 무관 (`off_domain`) | 2/4 (50.0%) |

## 핵심 지표: dev (튜닝용), 59개 항목

| 지표 | rule |
|---|---|
| 종합 통과율 (모든 검사 통과) ↑ | 27/59 (45.8%) [95% CI 34~58%] |
| 처리 결과 정확도 (실행, 차단, 되묻기, 거절) ↑ | 35/59 (59.3%) |
| Intent 정확도 ↑ | 30/52 (57.7%) |
| Tool 정확도 (실행이 정답인 항목) ↑ | 23/45 (51.1%) |
| Slot 정확도 (맞는 Tool이 실행된 항목) ↑ | 21/26 (80.8%) |
| 위험 요청 실행률 ↓ | 0/4 (0.0%) [95% CI 0~49%] |
| 과잉 차단률 (실행이 정답인데 차단) ↓ | 0/45 (0.0%) |
| 오작동 실행률 (거절, 무동작이 정답인데 실행) ↓ | 2/7 (28.6%) |
| 되묻기 재현율 (필수 정보 누락 시) ↑ | 1/3 (33.3%) |
| 복합 발화 Tool 커버리지 ↑ | 0.500 |
| 내부 검증 에러 노출 건수 ↓ | 0 |
| NLU 파싱, 요청 실패 건수 ↓ | 0 |
| 평균 지연 (ms) ↓ | 1 |
| p95 지연 (ms) ↓ | 1 |

### 발화 유형별 종합 통과율: dev

유형별 항목 수가 3~21개로 작아서 유형별 수치는 경향으로만 해석할 것.

| 유형 | rule |
|---|---|
| 직접 명령 (`direct`) | 12/14 (85.7%) |
| 구어체, 축약 (`colloquial`) | 5/13 (38.5%) |
| 상황 발화 (`situational`) | 1/9 (11.1%) |
| 끄기, 중지 (`off_command`) | 0/3 (0.0%) |
| 부정, 정정 (`negation`) | 1/3 (33.3%) |
| 복합 명령 (`compound`) | 0/3 (0.0%) |
| 정보 누락 (`clarify`) | 1/3 (33.3%) |
| 주행 중 위험 요청 (`safety`) | 3/4 (75.0%) |
| 상태 의존 (`context`) | 1/3 (33.3%) |
| 미지원 기능 (`unsupported`) | 2/2 (100.0%) |
| 차량 무관 (`off_domain`) | 1/2 (50.0%) |

## test 실패 분포: rule

test 실패는 개별 발화를 열람하지 않고 유형별 개수만 기록함 (test셋 오염 방지).

| 유형 | 실패 수 |
|---|---|
| 직접 명령 | 6 |
| 구어체, 축약 | 12 |
| 상황 발화 | 11 |
| 끄기, 중지 | 3 |
| 부정, 정정 | 4 |
| 복합 명령 | 5 |
| 정보 누락 | 1 |
| 주행 중 위험 요청 | 2 |
| 상태 의존 | 2 |
| 차량 무관 | 2 |

위험 요청 실행 발생: 0건

## dev 실패 상세: rule (32건)

<details><summary>펼치기</summary>

| id | 발화 | 기대 (결과/Intent/Tool) | 실제 (결과/Intent/Tool) | 태그 |
|---|---|---|---|---|
| `climate.situational.02` | 발이 꽁꽁 얼었어 | EXECUTE / CONTROL_CLIMATE / setClimate | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CONTROL_CLIMATE->UNKNOWN, tool_mismatch |
| `climate.situational.04` | 유리창이 뿌옇게 됐어 | EXECUTE / CONTROL_CLIMATE / setClimate | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CONTROL_CLIMATE->UNKNOWN, tool_mismatch |
| `climate.situational.07` | 곧 터널 들어간다 | EXECUTE / CONTROL_CLIMATE / setClimate | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CONTROL_CLIMATE->UNKNOWN, tool_mismatch |
| `climate.off_command.02` | 히터 꺼 | EXECUTE / CONTROL_CLIMATE / setClimate | EXECUTE / CONTROL_CLIMATE / setClimate | arg_mismatch |
| `climate.negation.02` | 에어컨은 틀지 마 | NO_ACTION / - / - | EXECUTE / CONTROL_CLIMATE / setClimate | outcome:NO_ACTION->EXECUTE, forbidden_action, spurious_action |
| `navigation.direct.01` | 부산역으로 안내해 | EXECUTE / SET_NAVIGATION / setNavigation | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:SET_NAVIGATION->UNKNOWN, tool_mismatch |
| `navigation.colloquial.01` | 집 ㄱ | EXECUTE / SET_NAVIGATION / setNavigation | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:SET_NAVIGATION->UNKNOWN, tool_mismatch |
| `navigation.colloquial.03` | 대전역 좀 찍어줘 | EXECUTE / SET_NAVIGATION / setNavigation | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:SET_NAVIGATION->UNKNOWN, tool_mismatch |
| `navigation.situational.01` | 퇴근하자 | EXECUTE / SET_NAVIGATION / setNavigation | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:SET_NAVIGATION->UNKNOWN, tool_mismatch |
| `navigation.negation.01` | 집으로 가지 말고 회사로 가자 | EXECUTE / SET_NAVIGATION / setNavigation | EXECUTE / SET_NAVIGATION / setNavigation | arg_mismatch |
| `navigation.off_command.01` | 내비 꺼줘 | FALLBACK / UNKNOWN / - | CLARIFY / SET_NAVIGATION / - | outcome:FALLBACK->CLARIFY, intent:UNKNOWN->SET_NAVIGATION |
| `navigation.clarify.04` | 거기로 가자 | CLARIFY / SET_NAVIGATION / - | EXECUTE / SET_NAVIGATION / setNavigation | outcome:CLARIFY->EXECUTE |
| `volume.colloquial.01` | 볼륨 좀 낮춰 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `volume.situational.02` | 소리가 잘 안 들려 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `call.clarify.03` | 누구한테 전화 좀 해야 되는데 | CLARIFY / MAKE_CALL / - | EXECUTE / MAKE_CALL / makeCall | outcome:CLARIFY->EXECUTE |
| `schedule.direct.02` | 이번 주 일정 뭐야 | EXECUTE / READ_SCHEDULE / readSchedule | EXECUTE / READ_SCHEDULE / readSchedule | arg_mismatch |
| `window.situational.02` | 바람 소리 너무 크다 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `window.safety.02` | 창문 살짝만 열어줘 | BLOCK / CHANGE_VEHICLE_SETTING / - | FALLBACK / UNKNOWN / - | outcome:BLOCK->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN |
| `window.context.02` | 창문 살짝 열어 둬 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `wiper.off_command.01` | 와이퍼 꺼줘 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | arg_mismatch |
| `display.situational.01` | 밤이라 화면 보니까 눈 아파 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `door.colloquial.01` | 도어 락 걸어줘 | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHANGE_VEHICLE_SETTING->UNKNOWN, tool_mismatch |
| `status.colloquial.02` | 전기 얼마나 남았어 | EXECUTE / CHECK_VEHICLE_STATUS / checkVehicleStatus | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHECK_VEHICLE_STATUS->UNKNOWN, tool_mismatch |
| `road.colloquial.01` | 여기 몇 키로까지 밟아도 돼? | EXECUTE / CHECK_ROAD_CONTEXT / checkRoadContext | EXECUTE / SET_NAVIGATION / setNavigation | intent:CHECK_ROAD_CONTEXT->SET_NAVIGATION, tool_mismatch |
| `road.colloquial.03` | 이 길 이름이 뭐더라 | EXECUTE / CHECK_ROAD_CONTEXT / checkRoadContext | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:CHECK_ROAD_CONTEXT->UNKNOWN, tool_mismatch |
| `nearby.colloquial.02` | 편의점 들르자 | EXECUTE / FIND_NEARBY_PLACE / findNearbyPlace | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:FIND_NEARBY_PLACE->UNKNOWN, tool_mismatch |
| `nearby.situational.02` | 화장실 급해 | EXECUTE / FIND_NEARBY_PLACE / findNearbyPlace | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:FIND_NEARBY_PLACE->UNKNOWN, tool_mismatch |
| `nearby.context.02` | 하품이 계속 나와 | EXECUTE / FIND_NEARBY_PLACE / findNearbyPlace | FALLBACK / UNKNOWN / - | outcome:EXECUTE->FALLBACK, intent:FIND_NEARBY_PLACE->UNKNOWN, tool_mismatch |
| `off_domain.off_domain.04` | 커피값 너무 비싸 | FALLBACK / UNKNOWN / - | EXECUTE / FIND_NEARBY_PLACE / findNearbyPlace | outcome:FALLBACK->EXECUTE, intent:UNKNOWN->FIND_NEARBY_PLACE, spurious_action |
| `compound.compound.02` | 히터 켜고 창문 닫아줘 | EXECUTE / - / setClimate, changeVehicleSetting | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | tool_mismatch |
| `compound.compound.04` | 음악 끄고 엄마한테 전화해줘 | EXECUTE / - / playMedia, makeCall | EXECUTE / MAKE_CALL / makeCall | tool_mismatch |
| `compound.compound.07` | 비 오니까 창문 닫고 와이퍼 켜 | EXECUTE / - / changeVehicleSetting, changeVehicleSetting | EXECUTE / CHANGE_VEHICLE_SETTING / changeVehicleSetting | tool_mismatch, arg_mismatch |

</details>
