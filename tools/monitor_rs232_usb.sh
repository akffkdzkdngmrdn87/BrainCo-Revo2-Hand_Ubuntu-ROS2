#!/bin/bash

echo "=== RS232 USB 연결 모니터링 ==="
echo "RS232를 USB로 연결하면 /dev/ttyUSB0 또는 /dev/ttyACM0으로 인식됩니다"
echo ""
echo "연결 상태 확인 중... (Ctrl+C로 종료)"
echo ""

while true; do
    if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
        echo ""
        echo "✓ USB Serial 장치 발견!"
        ./check_rs232_usb.sh
        exit 0
    fi
    echo -n "."
    sleep 2
done
