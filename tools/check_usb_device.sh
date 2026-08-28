#!/bin/bash

echo "=== STARK2.0 USB 장치 확인 ==="
echo ""

echo "1. USB/Serial 포트 확인:"
ls -la /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "   USB 장치가 인식되지 않았습니다."
echo ""

echo "2. 시스템 tty 장치 확인:"
ls -la /dev/tty* 2>/dev/null | grep -E "USB|ACM|S[0-9]" | head -10 || echo "   관련 장치를 찾을 수 없습니다."
echo ""

echo "3. USB 장치 목록 (lsusb):"
if command -v lsusb &> /dev/null; then
    lsusb | head -10
else
    echo "   lsusb 명령어를 사용할 수 없습니다."
fi
echo ""

echo "4. 최근 USB 연결 로그:"
dmesg | tail -50 | grep -i -E "usb|tty|serial" | tail -10 || echo "   최근 USB 연결 로그가 없습니다."
echo ""

echo "5. WSL2 환경 확인:"
if uname -r | grep -q "WSL2\|microsoft"; then
    echo "   WSL2 환경입니다."
    echo "   Windows에서 USBIPD를 사용하여 USB 장치를 WSL2로 전달해야 합니다."
    echo ""
    echo "   Windows PowerShell(관리자 권한)에서 실행:"
    echo "   1. usbipd list  # USB 장치 목록 확인"
    echo "   2. usbipd attach --wsl --busid <BUSID>  # WSL2로 연결"
else
    echo "   일반 Linux 환경입니다."
fi
echo ""

echo "=== 확인 완료 ==="

