#!/bin/bash

# 제조사 예제 폴더 위치. 환경변수 STARK_SDK_DIR 로 덮어쓸 수 있다.
# 미설정 시 참조 설치 위치를 사용한다.
SDK_DIR="${STARK_SDK_DIR:-$HOME/1/brainco/src/stark-serialport-example}"

echo "=== STARK2.0 USB 장치 자동 감지 및 테스트 ==="
echo ""

# USB 장치 감지 함수
detect_usb_device() {
    local max_attempts=30
    local attempt=0
    
    echo "USB 장치 감지 중..."
    while [ $attempt -lt $max_attempts ]; do
        if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
            local device=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
            echo "✓ USB 장치 발견: $device"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    echo ""
    return 1
}

# USB 장치 감지
if detect_usb_device; then
    DEVICE=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
    echo ""
    echo "장치 정보:"
    ls -la $DEVICE
    echo ""
    
    # 권한 확인 및 설정
    if [ ! -r "$DEVICE" ] || [ ! -w "$DEVICE" ]; then
        echo "권한 설정 중..."
        sudo chmod 666 $DEVICE 2>/dev/null || echo "권한 설정 실패 (수동으로 실행: sudo chmod 666 $DEVICE)"
    fi
    
    # Python 테스트
    echo ""
    echo "STARK2.0 연결 테스트 시작..."
    cd $SDK_DIR/python/revo2
    
    # 의존성 확인
    if ! python3 -c "import bc_stark_sdk" 2>/dev/null; then
        echo "bc_stark_sdk 설치 중..."
        cd $SDK_DIR/python
        pip3 install -r requirements.txt 2>/dev/null || echo "의존성 설치 실패"
        cd revo2
    fi
    
    # 간단한 연결 테스트
    echo "오른손 장치 (slave_id: 0x7f) 연결 테스트..."
    python3 -c "
import asyncio
import sys
sys.path.insert(0, '$SDK_DIR/python')
from revo2.revo2_utils import open_modbus_revo2

async def test():
    try:
        print('장치 연결 중...')
        (client, slave_id) = await open_modbus_revo2(port_name='$DEVICE', quick=True)
        print(f'✓ 연결 성공! Slave ID: {hex(slave_id)}')
        
        # 장치 정보 가져오기
        device_info = await client.get_device_info(slave_id)
        print(f'✓ 장치 정보: {device_info.description}')
        
        libstark.modbus_close(client)
        print('✓ 테스트 완료!')
        return True
    except Exception as e:
        print(f'✗ 연결 실패: {e}')
        return False

result = asyncio.run(test())
sys.exit(0 if result else 1)
" 2>&1

else
    echo ""
    echo "✗ USB 장치를 찾을 수 없습니다."
    echo ""
    echo "Windows에서 다음을 실행해주세요:"
    echo "  1. PowerShell을 관리자 권한으로 실행"
    echo "  2. usbipd list  # USB 장치 확인"
    echo "  3. usbipd attach --wsl --busid <BUSID>  # WSL2로 연결"
    echo ""
    echo "또는 Windows에서 다음 스크립트 실행:"
    echo "  PowerShell (관리자): .\\connect_usb_to_wsl.ps1"
    exit 1
fi

