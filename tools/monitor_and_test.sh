#!/bin/bash
echo "=== STARK2.0 USB 장치 모니터링 및 자동 테스트 ==="
echo "USB 장치가 연결될 때까지 대기 중... (Ctrl+C로 종료)"
echo ""

# 30초마다 확인, 최대 10분 대기
for i in {1..20}; do
    if ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | grep -q .; then
        DEVICE=$(ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null | head -1)
        echo ""
        echo "✓ USB 장치 발견: $DEVICE"
        ls -la $DEVICE
        echo ""
        echo "자동 테스트 시작..."
        ./auto_detect_and_test.sh
        exit 0
    fi
    echo -n "."
    sleep 2
done

echo ""
echo "✗ 시간 내에 USB 장치를 찾을 수 없습니다."
echo ""
echo "Windows에서 USBIPD 연결이 필요합니다:"
echo "PowerShell (관리자 권한):"
echo "  wsl cat <이_저장소>/tools/connect_usb_auto.ps1 | powershell -ExecutionPolicy Bypass -"
