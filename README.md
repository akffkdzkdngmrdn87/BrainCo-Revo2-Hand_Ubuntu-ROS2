# BrainCo Revo2 Robotic Hand Control (Ubuntu · ROS 2 Humble)

**Modbus RTU 기반 6자유도 의수(Revo2 Basic)의 키보드 실시간 제어 및 ROS 2 토픽 제어 이중 경로 구현**

[![Platform](https://img.shields.io/badge/platform-BrainCo_Revo2_Basic-red.svg)](https://www.brainco-hz.com/docs/revolimb-hand/index.html)
[![OS](https://img.shields.io/badge/Ubuntu-22.04_LTS-orange.svg)](https://releases.ubuntu.com/22.04/)
[![ROS 2](https://img.shields.io/badge/ROS_2-Humble-blue.svg)](https://docs.ros.org/en/humble/)
[![Python](https://img.shields.io/badge/python-3.10%2B-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache_2.0-lightgrey.svg)](./LICENSE)

## 🎬 로봇손 실시간 제어 실증 데모 (Robotic Hand in Action)

<div align="center">
  <video src="https://github.com/user-attachments/assets/23737593-fa2b-4247-a8a7-7e8792eb345a"
         autoplay loop muted playsinline controls width="800"></video>
  <p><em>🎬 로봇손 실시간 제어 실증 데모 (40.8초 · 키보드 제어 및 프리셋 제스처 시연)</em></p>
</div>

## 1. 프로젝트 개요 (Project Overview)

* **연구 목적:** 본 프로젝트는 BrainCo Revo2 Basic 로봇 손(6자유도 의수형 그리퍼)을 대상으로, **동일한 하드웨어를 두 개의 서로 다른 제어 계층에서 구동**하고 그 특성을 비교·검증하기 위해 진행되었습니다. 첫째는 Python SDK를 통해 Modbus RTU 프레임을 직접 송신하는 **단일 프로세스 경로**이며, 둘째는 ROS 2 노드를 통해 토픽으로 명령을 발행하는 **분산 미들웨어 경로**입니다.
* **연구 범위:** 제조사가 제공하는 공식 예제(`stark-serialport-example`)는 개별 기능의 최소 호출 예시만을 제공하므로, 실제 시연 및 교육 현장에서 요구되는 **연속적 제스처 조합·손가락 단위 미세조정·전체 동작 자동 시연**을 수행할 수 없습니다. 본 저장소는 그 상위 계층을 구현한 사용자 응용 코드 일체를 담습니다.
* **손가락 배열 규격의 실측 확정:** 6개 액추에이터의 배열 인덱스는 공식 문서만으로 확정되지 않아, 개별 액추에이터를 하나씩 구동하는 시험 스크립트(`src/tests/`)로 실측하여 `[엄지, 엄지보조, 검지, 중지, 약지, 소지]` 순서임을 확정하였습니다. 값의 범위는 `0`(완전히 폄) ~ `1000`(완전히 쥠)의 천분비(Normalized)입니다.
* **개발 방법론:** 본 시스템의 제어 로직 및 문서화는 대형 언어 모델(LLM)을 활용한 AI-Assisted 프로그래밍 방식으로 진행되었으며, 각 동작은 실제 하드웨어로 개폐 동작을 확인한 뒤 확정하였습니다.
* **라이선스:** 본 저장소의 코드는 Apache License 2.0 을 따릅니다. 단, **제조사 SDK 및 공식 예제는 본 저장소에 포함되지 않습니다**(§4.1 및 §6 참조).

## 2. 시스템 개발 환경 (System Environment)

| 구분 | 규격 |
|---|---|
| 대상 하드웨어 | BrainCo Revo2 **Basic**(표준판, 비촉각) · 오른손(MediumRight) |
| 자유도 | 6 (엄지 2축 + 검지·중지·약지·소지) |
| 통신 규격 | Modbus RTU over RS-485, **460800 bps** |
| 장치 노드 | `/dev/ttyUSB0` (FTDI USB-UART 브리지) |
| 장치 ID | `127` (0x7F, 오른손) |
| 전원 | **24 V DC 외부 어댑터 필수** (USB는 통신 전용) |
| 호스트 OS | Ubuntu Linux 22.04.5 LTS (64-bit) |
| 미들웨어 | ROS 2 Humble Hawksbill |
| 런타임 | Python 3.10, `bc-stark-sdk` 0.9.5, `colorlog` |
| 검증 완료 환경 | Intel Core i7 계열 · 실제 하드웨어 개폐 동작 및 ROS 2 파이프라인 |

## 3. 핵심 아키텍처 (Core Architecture)

### 3.1 이중 제어 경로 (Dual Control Path)

동일한 액추에이터를 두 경로로 제어하며, 두 경로는 **동일한 시리얼 포트를 점유**하므로 **동시에 실행할 수 없습니다.**

```text
[경로 A · 단일 프로세스]
  hand_keyboard.py ──► bc_stark_sdk ──► Modbus RTU(460800) ──► /dev/ttyUSB0 ──► 로봇 손
                        (파이썬 프로세스 1개, ROS 2 불필요)

[경로 B · ROS 2 미들웨어]
  keyboard_control.py ──► /set_motor_multi_127 ──► stark_node ──► /dev/ttyUSB0 ──► 로봇 손
     (터미널 ②)          (SetMotorMulti 메시지)   (터미널 ①)
                        ◄── /motor_status ──────
```

| 항목 | 경로 A (SDK 직접) | 경로 B (ROS 2) |
|---|---|---|
| 필요 터미널 수 | **1개** | **2개** (컨트롤러 노드 + 제어기) |
| ROS 2 의존성 | 없음 | Humble + `ros2_stark_msgs` 빌드 필요 |
| 상태 피드백 | SDK 직접 조회 (`get_motor_status`) | `/motor_status` 토픽 구독 |
| 타 노드 연동 | 불가 | 가능 (카메라 손추적 등) |
| 권장 용도 | **첫 동작 확인, 시연, 교육** | 다중 노드 통합, 센서 연동 |

### 3.2 상태 배열 기반 제어 모델 (Stateful Position Array)

`hand_keyboard.py` 의 `HandController` 는 6개 액추에이터의 목표 위치를 파이썬 리스트로 **호스트 측에 유지**하고, 키 입력마다 해당 인덱스만 갱신한 뒤 전체 배열을 한 프레임으로 송신합니다. 이 설계에 따라 다음이 성립합니다.

1. **제스처와 미세조정의 자유 조합** — 프리셋 제스처를 적용한 뒤 특정 손가락만 100 단위로 보정할 수 있습니다. 상태를 호스트가 알고 있으므로 직전 값에 대한 상대 조정이 가능합니다.
2. **범위 강제(Clamping)** — 송신 직전 `0 ~ 1000` 으로 절단하므로, 미세조정 누적으로 규격 범위를 벗어나는 명령이 하드웨어에 전달되지 않습니다.
3. **3단계 순환(Cycle)** — 손가락별로 `폄(0) → 반쯤(500) → 쥠(1000)` 을 순환하며, 미세조정으로 만들어진 중간값에서는 방향에 맞는 끝값으로 수렴시켜 순환 상태를 복원합니다.

명령은 **위치 + 도달시간(ms)** 방식(`set_finger_positions_and_durations`)으로 발행됩니다. 속도 지정 방식과 달리 6개 손가락의 도달 시각이 일치하므로, 제스처 형성 과정에서 손가락 간 위상 차가 발생하지 않습니다.

### 3.3 원자적 키 입력 처리 (Raw-mode Key Handling)

시연 중 엔터 입력 없이 즉시 반응해야 하므로, 터미널을 `tty.setraw()` 로 전환하여 1바이트 단위로 키를 수신합니다. 종료 시 `termios.tcsetattr(..., TCSADRAIN)` 로 원래 속성을 복원하며, 이 복원은 `finally` 블록에 배치되어 예외 발생 시에도 터미널이 raw 모드로 남지 않습니다.

키 배치는 **미세조정 키(`q w e r t y`)와 프리셋 제스처 키가 충돌하지 않도록** 재배치되었습니다(엄지 척 `t` → `u`, 러브 `l` 유지). 물리 키보드에서 숫자열(1~6, 손가락 순환)과 그 아래열(q~y, 같은 손가락 미세조정)이 **수직으로 대응**하도록 배치하여, 손가락 번호와 키 위치의 대응을 암기하지 않고 조작할 수 있습니다.

### 3.4 안전 설계 (Safety by Default)

* **초기화는 항상 펴기:** 기동 직후 `[0,0,0,0,0,0]`(완전히 폄)을 송신합니다. 급작스러운 주먹 동작은 손가락 사이 끼임 위험이 있어 초기 상태로 사용하지 않습니다.
* **종료 시 펴기:** `Esc`·`Ctrl+C`·데모 종료·예외 종료 모든 경로에서 손을 편 뒤 `modbus_close()` 로 포트를 반환합니다.
* **경로 충돌 차단 안내:** 경로 A와 B를 동시 실행하면 `/dev/ttyUSB0` 를 양쪽이 열어 통신이 붕괴합니다. 본 저장소의 문서는 모든 실행 절차에서 이 제약을 명시합니다.

### 3.5 전체 동작 자동 시연 (Demo Play)

`hand_demo_play.py` 는 `hand_keyboard.py` 의 `HandController` 를 그대로 재사용(import)하여 제어 로직을 중복 구현하지 않으며, 7개 구간(프리셋 제스처 → 손가락 웨이브 → 3단계 순환 → 미세조정 → 숫자 세기 → 전체 쥐기 레벨 → 피날레)을 순차 재생합니다. `--loop` 지정 시 무한 반복하므로 전시·상설 시연에 사용할 수 있습니다.

## 4. 퀵 스타트 (Quick Start)

### 4.1 [사전 준비 ①] 제조사 공식 SDK 예제 확보

> **본 저장소에는 제조사 SDK 및 공식 예제가 포함되어 있지 않습니다.**
> 해당 저장소에는 라이선스 파일이 명시되어 있지 않아 재배포 근거가 없으며, 사전 컴파일된 바이너리 라이브러리를 포함하고 있습니다. 따라서 **직접 내려받아** 사용하십시오.

```bash
# 1) 공식 예제 저장소 확보 (위치는 자유롭게 지정 가능)
mkdir -p ~/1/brainco/src && cd ~/1/brainco/src
git clone https://github.com/BrainCoTech/stark-serialport-example.git

# 2) 본 저장소의 스크립트에 그 위치를 알려준다
#    (아래 기본 경로에 두었다면 이 설정은 생략 가능)
export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example
```

### 4.2 [사전 준비 ②] 런타임 및 포트 권한

```bash
# Python SDK 및 로깅 의존성
pip3 install bc-stark-sdk==0.9.5 colorlog

# 시리얼 포트 접근 권한 (최초 1회, 재로그인 후 영구 적용)
sudo usermod -aG dialout $USER

# 재로그인 전 임시 해결 (Permission denied 발생 시)
sudo chmod a+rw /dev/ttyUSB0
```

### 4.3 [필수 확인] 24 V 전원

로봇 손은 **24 V DC 어댑터가 연결되어 있어야 동작합니다.** USB는 통신만 담당하므로, 전원이 없으면 포트는 열리지만 손이 응답하지 않습니다. 장치 탐색 실패(`Failed to detect device on port`)의 가장 빈번한 원인입니다.

### 4.4 [경로 A] 키보드 실시간 제어 — 터미널 1개, 권장

```bash
# 실시간 키보드 제어
python3 src/hand_keyboard.py

# 프리셋 제스처만 빠르게 순회
python3 src/hand_keyboard.py --demo
```

| 분류 | 키 | 동작 |
|---|---|---|
| **프리셋 제스처** | `p` `f` `v` `o` | 보 · 주먹 · 브이 · OK |
| | `u` `g` `l` `c` `n` | 엄지 척 · 총 · 러브(ILY) · 하트 · 숫자 3 |
| **손가락 3단계 순환** | `1`~`6` | 폄 → 반쯤 → 쥠 (1엄지 2엄지보조 3검지 4중지 5약지 6소지) |
| | `!` `@` `#` `$` `%` `^` | 역방향 순환 (Shift + 숫자) |
| **손가락 미세조정** | `q` `w` `e` `r` `t` `y` | 쥐는 방향 (+100), 숫자키와 같은 손가락 순서 |
| | `Q` `W` `E` `R` `T` `Y` | 펴는 방향 (−100) |
| **전체 조절** | `Space` / `0` | 전체 펴기 / 전체 주먹 |
| | `+`(`=`) / `-`(`_`) | 전체 조금 쥐기 / 조금 펴기 (±200) |
| **기타** | `i` / `?` / `Esc` | 실제 위치 읽기 / 도움말 / 종료 |

### 4.5 [경로 A] 전체 동작 자동 시연

```bash
python3 src/hand_demo_play.py          # 1회 재생
python3 src/hand_demo_play.py --loop   # 무한 반복 (Ctrl+C 종료)
```

### 4.6 [경로 B] ROS 2 토픽 제어 — 터미널 2개

먼저 공식 예제에 포함된 ROS 2 워크스페이스를 빌드하여 `ros2_stark_msgs` 를 생성해야 합니다(빌드 절차는 공식 예제의 `ros2_stark_ws/README.md` 참조).

```bash
# [터미널 ①] 컨트롤러 노드 — 시리얼 ↔ ROS 2 브리지. 켜 둔 채로 유지한다.
cd $STARK_SDK_DIR/ros2_stark_ws && ./stark_serial_manager.sh launch

# [터미널 ②] 키보드 제어기
source /opt/ros/humble/setup.bash
source $STARK_SDK_DIR/ros2_stark_ws/install/setup.bash
python3 src/keyboard_control.py
```

토픽으로 직접 명령을 발행하려면 다음과 같습니다(브이 자세).

```bash
ros2 topic pub --once /set_motor_multi_127 ros2_stark_msgs/msg/SetMotorMulti \
"{slave_id: 127, mode: 5, positions: [1000,1000,0,0,1000,1000], speeds: [0,0,0,0,0,0], \
currents: [0,0,0,0,0,0], pwms: [0,0,0,0,0,0], durations: [500,500,500,500,500,500]}"
```

### 4.7 [선택] 카메라 손추적 연동

`src/hand_tracking_control.py` 는 웹캠으로 사람의 손 관절을 추정하여 로봇 손이 추종하도록 합니다. 별도 의존성이 필요하며, **본 환경에서는 미검증 상태**입니다.

```bash
pip3 install opencv-python mediapipe
python3 src/hand_tracking_control.py   # 경로 B(컨트롤러 노드) 기동 상태에서 실행
```

## 5. 저장소 구성 (Repository Structure)

```text
.
├─ README.md                       본 문서
├─ 사용법.md                        비전문가용 한글 실행 설명서 (키 조작표 포함)
├─ 필독.md                          트러블슈팅 — 증상 / 원인 / 해결책
├─ LICENSE                         Apache License 2.0
├─ src/
│   ├─ hand_keyboard.py            ★ 경로 A 메인 — 키보드 실시간 제어 (SDK 직접)
│   ├─ hand_demo_play.py           ★ 경로 A — 전체 동작 7구간 자동 시연
│   ├─ keyboard_control.py         경로 B — ROS 2 토픽 기반 키보드 제어
│   ├─ gesture_demo.py             경로 B — 제스처 순차 시연
│   ├─ wave_demo.py                경로 B — 손 흔들기 애니메이션
│   ├─ ros2_test_control.py        경로 B — 토픽 발행 최소 동작 확인
│   ├─ hand_tracking_control.py    경로 B — MediaPipe 손추적 추종 (미검증)
│   └─ tests/                      손가락 배열 인덱스 실측 스크립트
├─ docs/
│   ├─ 운영가이드.md                 장치 규격 · 실행법 A/B · 안전 수칙 전문
│   ├─ STARK2.0_USB_연결_가이드.md    USB 인식 및 포트 권한 점검 절차
│   └─ WSL2_USB_연결_가이드.md        Windows WSL2 에서 USBIPD 로 장치 전달
├─ tools/                          USB·시리얼 포트 진단 셸/PowerShell 스크립트
└─ media/
    ├─ 로봇손_키보드제어_시연.mp4       시연 영상 (H.264 · 40.8초 · 7.0 MB)
    ├─ 로봇손_키보드제어_시연_무음.mp4   음성 제외판 (6.5 MB)
    └─ 로봇손_시연_썸네일.jpg           README 정지컷
```

## 6. 라이선스 정합성 및 보안 (License & Security Notice)

* **본 저장소 코드:** Apache License 2.0.
* **제조사 SDK (`bc-stark-sdk`) 및 공식 예제 (`stark-serialport-example`):** 본 저장소에 **포함하지 않았습니다.** 공식 예제 저장소에는 라이선스 파일이 존재하지 않아 재배포 조건을 확정할 수 없으며, 플랫폼별 사전 컴파일 바이너리(`.so` / `.dll`)를 포함합니다. 이용자는 제조사 저장소에서 직접 확보하여야 하며, 그 이용 조건은 제조사 정책을 따릅니다.
* **`src/hand_tracking_control.py` 의 의존성:** MediaPipe 및 OpenCV의 라이선스 조건은 각 프로젝트 규정을 따릅니다.
* **자격증명 부재:** 본 저장소에는 암호·토큰·API 키가 포함되어 있지 않습니다. 로봇 손은 로컬 시리얼 포트로만 통신하며 네트워크 자격증명을 사용하지 않습니다.
* **시연 영상:** `media/` 의 영상에는 로봇 손과 이를 든 손만 촬영되어 있으며 인물의 얼굴은
  포함되지 않습니다. 음성이 포함된 판과 제외된 판을 함께 제공합니다.
* **개별 기기 식별자:** 문서 내 장치 시리얼 번호는 `BCXRR2147J25XXXXX` 형태로 가렸습니다. 실제 로그에는 보유 기기의 고유 번호가 출력됩니다.

## 7. 안전 수칙 (Safety Precautions)

1. 첫 동작은 반드시 **펴기**(`p` 키 또는 공식 예제의 `open_hand.py`)로 시작합니다. 주먹 동작을 초기 상태로 사용하면 손가락 사이 끼임이 발생할 수 있습니다.
2. 손가락이 물체에 걸려 액추에이터가 정지하면 과전류 보호가 작동합니다. 물린 상태를 지속하지 마십시오.
3. **경로 A와 B를 동시에 실행하지 마십시오.** 시리얼 포트 충돌로 통신이 붕괴합니다.
4. 24 V 전원을 분리한 상태에서는 소프트웨어가 정상 동작해도 손이 움직이지 않습니다. 소프트웨어 결함으로 오판하지 않도록 전원을 먼저 확인합니다.

## 8. 참조 문헌 (References)

1. **BrainCo RevoLimb Hand 공식 문서** — Revo2 장치 규격, FingerId 정의, Modbus 레지스터 맵. https://www.brainco-hz.com/docs/revolimb-hand/index.html
2. **BrainCoTech / stark-serialport-example** — 제조사 공식 Python · C++ · ROS 2 예제. https://github.com/BrainCoTech/stark-serialport-example
3. **ROS 2 Humble Documentation** — 사용자 정의 메시지 빌드 및 토픽 발행 규격. https://docs.ros.org/en/humble/
4. **Modbus Application Protocol Specification V1.1b3** — RTU 프레이밍 및 슬레이브 주소 규격. https://www.modbus.org/specs.php
5. **Python `termios` / `tty` 표준 라이브러리 문서** — POSIX 터미널 raw 모드 전환 및 속성 복원. https://docs.python.org/3/library/termios.html
6. **Google MediaPipe Hands** — 21개 손 관절 추정 모델(선택 기능 근거). https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
