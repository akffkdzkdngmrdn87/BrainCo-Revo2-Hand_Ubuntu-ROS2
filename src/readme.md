# src — 제어 소스 코드 (Control Sources)

BrainCo Revo2 로봇 손을 구동하는 사용자 응용 코드입니다.
제어 경로가 두 가지이며 **동시에 실행할 수 없습니다**(같은 시리얼 포트를 점유).

## 경로 A — Python SDK 직접 (ROS 2 불필요, 터미널 1개)

| 파일 | 역할 | 비고 |
|---|---|---|
| `hand_keyboard.py` | **메인.** 키보드 실시간 제어. 프리셋 제스처 9종 + 손가락 3단계 순환 + 손가락별 미세조정(±100) | `HandController` 클래스가 상태 배열을 보유 |
| `hand_demo_play.py` | 전체 동작 7구간 자동 시연. `--loop` 로 무한 반복 | `hand_keyboard.HandController` 를 import 하여 재사용 |

```bash
export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example   # 설치 위치가 기본값과 다를 때만
python3 hand_keyboard.py
python3 hand_demo_play.py --loop
```

## 경로 B — ROS 2 토픽 (터미널 2개, 컨트롤러 노드 선행 기동 필요)

| 파일 | 역할 | 발행 토픽 |
|---|---|---|
| `keyboard_control.py` | 키보드 제어(ROS 2 판). 초기 버전으로 키 배치가 경로 A와 다르다 | `/set_motor_multi_127` |
| `gesture_demo.py` | 제스처 순차 시연 | 같음 |
| `wave_demo.py` | 손 흔들기 애니메이션 | 같음 |
| `ros2_test_control.py` | 토픽 발행 최소 동작 확인(개폐 1회) | 같음 |
| `hand_tracking_control.py` | 웹캠 손추적 추종. `opencv-python`·`mediapipe` 추가 필요. **미검증** | 같음 |

메시지 타입 `ros2_stark_msgs/msg/SetMotorMulti` 는 제조사 예제 워크스페이스에서 직접 빌드해야 생성됩니다.

## 손가락 배열 규격

```text
인덱스: [ 0     1        2     3     4     5   ]
손가락: [ 엄지  엄지보조  검지  중지  약지  소지 ]
값    :   0 = 완전히 폄  ~  1000 = 완전히 쥠
```

배열 순서는 `tests/` 의 실측 스크립트로 확정한 값입니다. 자료에 따라 다르게 기술된 경우가 있어,
보유 기기에서 한 번 확인할 것을 권장합니다([`../필독.md`](../필독.md) §8).

## SDK 경로 결정 규칙

경로 A의 두 스크립트는 `revo2_utils.py` 를 제조사 예제 폴더에서 import 합니다.

1. 환경변수 `STARK_SDK_DIR` 이 설정되어 있으면 그 값을 사용합니다.
2. 없으면 기본값 `~/1/brainco/src/stark-serialport-example` 를 사용합니다.
3. 두 경우 모두 폴더가 없으면 **ImportError 대신 안내 메시지를 출력하고 종료코드 1로 중단**합니다.
