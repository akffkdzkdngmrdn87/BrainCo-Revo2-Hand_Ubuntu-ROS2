# STARK2.0 USB 연결 및 동작 가이드

> **경로 표기 안내** — 아래 `$STARK_SDK_DIR` 는 제조사 예제(`stark-serialport-example`)를 내려받은 폴더입니다.
> 터미널에서 먼저 지정하십시오. 예)
> `export STARK_SDK_DIR=~/1/brainco/src/stark-serialport-example`


## 1단계: USB 장치 확인

STARK2.0을 USB로 연결한 후, 다음 명령어로 장치가 인식되었는지 확인하세요:

```bash
# USB 장치 확인
ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null

# 또는 dmesg로 최근 연결 확인
dmesg | tail -30 | grep -i usb
```

일반적으로 `/dev/ttyUSB0` 또는 `/dev/ttyACM0` 같은 포트로 인식됩니다.

## 2단계: Python으로 간단히 테스트하기

### 2.1 의존성 설치

```bash
cd $STARK_SDK_DIR/python

# Python 가상환경이 있다면 활성화
# pip3 install -r requirements.txt
```

### 2.2 간단한 제어 예제 실행

```bash
cd revo2
python3 revo2_ctrl.py
```

이 스크립트는:
- 자동으로 USB 포트를 감지합니다
- STARK2.0 장치에 연결합니다
- 기본적인 제어 동작을 수행합니다

## 3단계: ROS2로 실행하기 (ROS2 환경이 있는 경우)

### 3.1 환경 설정

```bash
cd $STARK_SDK_DIR/ros2_stark_ws

# ROS2 환경 소스
source /opt/ros/humble/setup.bash  # 또는 설치된 ROS2 버전에 맞게

# 워크스페이스 빌드
./stark_serial_manager.sh build build

# 워크스페이스 소스
source install/setup.bash
```

### 3.2 설정 파일 확인 및 수정

`ros2_stark_ws/src/ros2_stark_controller/config/params_revo2.yaml` 파일을 열어서 포트가 맞는지 확인:

```yaml
stark_node:
  ros__parameters:
    port: "/dev/ttyUSB0"  # 실제 USB 포트로 변경 필요
    baudrate: 460800      # STARK2.0 기본波特率
    slave_id: 0x7e        # 左手: 0x7e, 右手: 0x7f
    protocol_type: 1      # 1: Modbus RTU
    log_level: 2          # Info
```

### 3.3 ROS2 노드 실행

```bash
# STARK 노드 실행
./stark_serial_manager.sh launch build

# 또는 직접 실행
ros2 run ros2_stark_controller stark_node --ros-args \
  --params-file src/ros2_stark_controller/config/params_revo2.yaml
```

### 3.4 모니터링 및 제어

```bash
# 모터 상태 모니터링
ros2 topic echo /motor_status

# 클라이언트로 제어 테스트
ros2 run ros2_stark_controller stark_node_client.py 0x7e  # 左手
# 또는
ros2 run ros2_stark_controller stark_node_client.py 0x7f  # 右手
```

## 문제 해결

### USB 장치가 인식되지 않는 경우

1. **WSL2 환경인 경우**: USB 장치를 WSL2에 전달해야 합니다
   - Windows에서 USB 장치를 USBIPD로 공유해야 할 수 있습니다

2. **권한 문제**: USB 장치에 접근 권한이 없을 수 있습니다
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   # 또는 사용자를 dialout 그룹에 추가
   sudo usermod -a -G dialout $USER
   ```

3. **포트 확인**: 다른 포트로 인식되었을 수 있습니다
   ```bash
   ls -la /dev/tty* | grep USB
   ```

### 연결 실패 시

1. 포트 번호 확인: `/dev/ttyUSB0` 대신 실제 포트 번호 사용
2. Baudrate 확인: STARK2.0의 기본 baudrate는 460800입니다
3. Slave ID 확인: 
   - 左手 (왼손): 0x7e
   - 右手 (오른손): 0x7f

## 참고 문서

- [공식 문서](https://www.brainco-hz.com/docs/revolimb-hand/index.html)
- Python 예제: `python/revo2/README.md`
- ROS2 예제: `ros2_stark_ws/README.md`

