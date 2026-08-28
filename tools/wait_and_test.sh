#!/bin/bash

echo "=== RS232 USB 연결 대기 및 자동 테스트 ==="
echo "Windows에서 USBIPD 연결을 완료하면 자동으로 감지합니다"
echo ""

MAX_WAIT=60  # 최대 60초 대기
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
        echo ""
        echo "✓ USB Serial 장치 발견!"
        DEVICE=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
        echo "장치: $DEVICE"
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
echo "Windows에서 USBIPD 연결을 확인해주세요:"
echo "  PowerShell (관리자): usbipd list"
echo "  PowerShell (관리자): usbipd attach --wsl --busid <BUSID>"
