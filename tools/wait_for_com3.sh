#!/bin/bash

echo "=== COM3 USB Serial 장치 대기 중 ==="
echo "Windows에서 'usbipd attach --wsl --busid 2-3' 실행 후 자동 감지"
echo ""

MAX_WAIT=60
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
        DEVICE=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
        echo ""
        echo "✓ USB Serial 장치 발견: $DEVICE"
        echo ""
        ./check_rs232_usb.sh
        exit 0
    fi
    echo -n "."
    sleep 1
    WAITED=$((WAITED + 1))
done

echo ""
echo "✗ 시간 내에 USB 장치를 찾을 수 없습니다."
echo ""
echo "Windows에서 연결 확인:"
echo "  usbipd attach --wsl --busid 2-3"
