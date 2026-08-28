#!/bin/bash

# 제조사 예제 폴더 위치. 환경변수 STARK_SDK_DIR 로 덮어쓸 수 있다.
# 미설정 시 참조 설치 위치를 사용한다.
SDK_DIR="${STARK_SDK_DIR:-$HOME/1/brainco/src/stark-serialport-example}"

echo "=== RS232 USB 연결 확인 및 STARK2.0 테스트 ==="
echo ""

# USB Serial 장치 확인
USB_DEVICES=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null)

if [ -z "$USB_DEVICES" ]; then
    echo "✗ USB Serial 장치가 인식되지 않았습니다."
    echo ""
    echo "RS232를 USB로 연결했을 때:"
    echo "  - 일반적으로 /dev/ttyUSB0 또는 /dev/ttyUSB1로 인식됩니다"
    echo "  - CH340, FTDI, CP2102 등의 USB-to-Serial 칩이 사용됩니다"
    echo ""
    echo "확인 방법:"
    echo "  1. USB 케이블이 제대로 연결되었는지 확인"
    echo "  2. Windows에서 장치가 인식되는지 확인 (장치 관리자)"
    echo "  3. WSL2 환경이면 USBIPD로 연결 필요"
    echo ""
    echo "WSL2에서 USBIPD 연결:"
    echo "  Windows PowerShell (관리자):"
    echo "    usbipd list"
    echo "    usbipd attach --wsl --busid <BUSID>"
    exit 1
fi

echo "✓ USB Serial 장치 발견:"
for device in $USB_DEVICES; do
    echo "  - $device"
    ls -la $device
done
echo ""

# 첫 번째 장치 선택
DEVICE=$(echo $USB_DEVICES | cut -d' ' -f1)
echo "사용할 장치: $DEVICE"
echo ""

# 권한 확인
if [ ! -r "$DEVICE" ] || [ ! -w "$DEVICE" ]; then
    echo "권한 설정 중..."
    sudo chmod 666 $DEVICE 2>/dev/null || {
        echo "권한 설정 실패. 다음 명령어를 실행하세요:"
        echo "  sudo chmod 666 $DEVICE"
        echo "  sudo usermod -a -G dialout $USER"
        exit 1
    }
    echo "✓ 권한 설정 완료"
fi

echo ""
echo "=== STARK2.0 오른손 장치 연결 테스트 ==="
echo "포트: $DEVICE"
echo "Baudrate: 460800 (STARK2.0 기본값)"
echo "Slave ID: 0x7f (오른손)"
echo ""

# Python 테스트
cd $SDK_DIR/python/revo2

# 의존성 확인
if ! python3 -c "import bc_stark_sdk" 2>/dev/null; then
    echo "의존성 설치 중..."
    cd $SDK_DIR/python
    pip3 install -r requirements.txt 2>/dev/null || {
        echo "의존성 설치 실패"
        exit 1
    }
    cd revo2
fi

# 연결 테스트
python3 << EOF
import asyncio
import sys
sys.path.insert(0, '$SDK_DIR/python')

from revo2.revo2_utils import open_modbus_revo2

async def test():
    try:
        print(f'장치 연결 중: $DEVICE')
        (client, slave_id) = await open_modbus_revo2(port_name='$DEVICE', quick=True)
        print(f'✓ 연결 성공!')
        print(f'  Slave ID: {hex(slave_id)}')
        
        # 장치 정보 가져오기
        device_info = await client.get_device_info(slave_id)
        print(f'✓ 장치 정보:')
        print(f'  {device_info.description}')
        
        if device_info.is_revo2():
            print(f'✓ STARK2.0 장치 확인됨')
            if hex(slave_id) == '0x7f':
                print(f'✓ 오른손 장치 확인됨')
            elif hex(slave_id) == '0x7e':
                print(f'⚠ 왼손 장치입니다 (오른손은 0x7f)')
        
        libstark.modbus_close(client)
        print('')
        print('✓ 테스트 완료!')
        return True
    except Exception as e:
        print(f'✗ 연결 실패: {e}')
        import traceback
        traceback.print_exc()
        return False

result = asyncio.run(test())
sys.exit(0 if result else 1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "=== 다음 단계 ==="
    echo "제어 예제 실행:"
    echo "  cd $SDK_DIR/python/revo2"
    echo "  python3 revo2_ctrl.py"
    echo ""
    echo "ROS2 사용:"
    echo "  설정 파일에서 port를 '$DEVICE'로 변경"
    echo "  cd $SDK_DIR/ros2_stark_ws"
    echo "  ./stark_serial_manager.sh launch build"
fi

