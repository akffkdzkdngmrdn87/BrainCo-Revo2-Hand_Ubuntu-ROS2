# tests — 손가락 배열 인덱스 실측 스크립트

6개 액추에이터의 배열 인덱스가 어느 손가락에 대응하는지 **하드웨어로 직접 확인**하기 위한
스크립트입니다. 자료에 따라 배열 순서가 다르게 기술되어 있어 실측이 필요했습니다.

| 파일 | 하드웨어 필요 | 내용 |
|---|:--:|---|
| `test_finger_index.py` | 불필요 | SDK의 `FingerId` 열거형 정수값을 조회해 배열 매핑을 출력 |
| `test_finger_array.py` | **필요** | 3초 간격으로 한 손가락씩 구부려 인덱스를 눈으로 확정 |
| `test_fingers.py` | 불필요 | `FingerId` 열거형 출력. **구버전 API**(`from bc_stark_sdk import libstark`) 사용 — `0.9.5` 에서는 동작하지 않을 수 있으며 참고용으로만 보존 |

```bash
export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example
python3 test_finger_index.py
python3 test_finger_array.py    # 24 V 전원 및 실제 하드웨어 연결 상태에서 실행
```

> `test_finger_array.py` 는 손가락을 실제로 구부립니다. 손 주변에 이물이나 손가락이 없는지
> 확인한 뒤 실행하십시오.
