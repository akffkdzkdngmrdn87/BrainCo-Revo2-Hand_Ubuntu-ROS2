# tools — USB · 시리얼 포트 진단 도구

로봇 손이 응답하지 않을 때 **하드웨어 인식 단계부터** 확인하기 위한 보조 스크립트입니다.
제어 기능은 포함하지 않으며, 장치 탐색과 상태 출력만 수행합니다.

## Linux (Bash)

| 파일 | 용도 |
|---|---|
| `check_usb_device.sh` | `/dev/ttyUSB*`·`/dev/ttyACM*` 존재 여부와 `lsusb` 목록 확인 |
| `check_rs232_usb.sh` | RS-232/RS-485 변환기(FTDI 등) 인식 상태 상세 점검 |
| `auto_detect_and_test.sh` | 장치 자동 탐색 후 통신 시험까지 연속 수행 |
| `monitor_and_test.sh` | 장치 연결을 감시하다 인식되는 순간 시험을 실행 |
| `monitor_rs232_usb.sh` | RS-232 변환기 연결/해제 이벤트 감시 |
| `wait_and_test.sh` | 장치가 나타날 때까지 대기한 뒤 시험 실행 |
| `wait_for_com3.sh` | 특정 포트(COM3 대응)가 준비될 때까지 대기 |

```bash
chmod +x *.sh          # 최초 1회
./check_usb_device.sh
```

## Windows (PowerShell, WSL2 전용)

| 파일 | 용도 |
|---|---|
| `connect_usb_auto.ps1` | `usbipd-win` 으로 USB 장치를 WSL2 에 자동 attach |
| `connect_usb_to_wsl.ps1` | 대상 장치를 지정해 WSL2 로 전달 |

**관리자 권한 PowerShell** 에서 실행해야 하며, `usbipd-win` 이 먼저 설치되어 있어야 합니다.
절차는 [`../docs/WSL2_USB_연결_가이드.md`](../docs/WSL2_USB_연결_가이드.md) 를 참조하십시오.
