# STARK2.0 USB 장치를 WSL2로 연결하는 PowerShell 스크립트
# 관리자 권한으로 실행해야 합니다

Write-Host "=== STARK2.0 USB 장치 연결 ===" -ForegroundColor Cyan

# USBIPD 설치 확인
if (-not (Get-Command usbipd -ErrorAction SilentlyContinue)) {
    Write-Host "USBIPD가 설치되어 있지 않습니다. 설치를 시작합니다..." -ForegroundColor Yellow
    winget install --interactive --exact dorssel.usbipd-win
    if ($LASTEXITCODE -ne 0) {
        Write-Host "USBIPD 설치 실패. 수동으로 설치해주세요." -ForegroundColor Red
        exit 1
    }
    Write-Host "USBIPD 설치 완료. PowerShell을 다시 시작해주세요." -ForegroundColor Green
    exit 0
}

Write-Host "`n연결된 USB 장치 목록:" -ForegroundColor Cyan
usbipd list

Write-Host "`nSTARK2.0 USB 장치를 찾아서 BUSID를 입력해주세요:" -ForegroundColor Yellow
Write-Host "(예: 1-2, 1-3 등)" -ForegroundColor Gray
$busid = Read-Host "BUSID"

if ([string]::IsNullOrWhiteSpace($busid)) {
    Write-Host "BUSID가 입력되지 않았습니다." -ForegroundColor Red
    exit 1
}

Write-Host "`nUSB 장치를 WSL2로 연결하는 중..." -ForegroundColor Cyan
usbipd bind --busid $busid
usbipd attach --wsl --busid $busid

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n연결 성공! WSL2에서 장치를 확인해주세요." -ForegroundColor Green
    Write-Host "WSL2에서 실행: ls -la /dev/ttyUSB* /dev/ttyACM*" -ForegroundColor Gray
} else {
    Write-Host "`n연결 실패. 오류를 확인해주세요." -ForegroundColor Red
}

