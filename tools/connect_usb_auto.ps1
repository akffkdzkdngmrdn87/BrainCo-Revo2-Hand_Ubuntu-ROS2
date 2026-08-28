# STARK2.0 USB 장치 자동 연결 스크립트
# 관리자 권한으로 실행해야 합니다

Write-Host "=== STARK2.0 USB 장치 자동 연결 ===" -ForegroundColor Cyan

# USBIPD 설치 확인
if (-not (Get-Command usbipd -ErrorAction SilentlyContinue)) {
    Write-Host "USBIPD가 설치되어 있지 않습니다. 설치를 시작합니다..." -ForegroundColor Yellow
    winget install --interactive --exact dorssel.usbipd-win
    if ($LASTEXITCODE -ne 0) {
        Write-Host "USBIPD 설치 실패." -ForegroundColor Red
        exit 1
    }
    Write-Host "USBIPD 설치 완료. PowerShell을 다시 시작해주세요." -ForegroundColor Green
    exit 0
}

# USB 장치 목록 가져오기
Write-Host "`n연결된 USB 장치 목록:" -ForegroundColor Cyan
$devices = usbipd list | Out-String
Write-Host $devices

# STARK2.0 관련 장치 찾기 (Serial, FTDI, CH340, CP210 등)
$serialDevices = $devices -split "`n" | Where-Object { 
    $_ -match "(Serial|FTDI|CH340|CP210|USB.*Serial|STARK|BrainCo)" -or 
    $_ -match "VID_[0-9A-F]{4}" 
}

if ($serialDevices.Count -eq 0) {
    Write-Host "`nSTARK2.0 관련 USB 장치를 찾을 수 없습니다." -ForegroundColor Yellow
    Write-Host "수동으로 BUSID를 입력해주세요:" -ForegroundColor Yellow
    $busid = Read-Host "BUSID"
} else {
    Write-Host "`n발견된 Serial 장치:" -ForegroundColor Green
    $serialDevices | ForEach-Object { Write-Host $_ -ForegroundColor Gray }
    
    # 첫 번째 장치의 BUSID 추출
    $firstLine = $serialDevices[0]
    if ($firstLine -match "(\d+-\d+)") {
        $busid = $matches[1]
        Write-Host "`n자동으로 BUSID 선택: $busid" -ForegroundColor Green
        $confirm = Read-Host "이 장치를 연결하시겠습니까? (Y/N)"
        if ($confirm -ne "Y" -and $confirm -ne "y") {
            Write-Host "취소되었습니다." -ForegroundColor Yellow
            exit 0
        }
    } else {
        Write-Host "`nBUSID를 자동으로 찾을 수 없습니다. 수동으로 입력해주세요:" -ForegroundColor Yellow
        $busid = Read-Host "BUSID"
    }
}

if ([string]::IsNullOrWhiteSpace($busid)) {
    Write-Host "BUSID가 입력되지 않았습니다." -ForegroundColor Red
    exit 1
}

# 기존 연결 해제
Write-Host "`n기존 연결 해제 중..." -ForegroundColor Cyan
usbipd detach --busid $busid 2>$null

# USB 장치 바인딩 및 연결
Write-Host "USB 장치 바인딩 중..." -ForegroundColor Cyan
usbipd bind --busid $busid

Write-Host "WSL2로 연결 중..." -ForegroundColor Cyan
usbipd attach --wsl --busid $busid

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ 연결 성공!" -ForegroundColor Green
    Write-Host "`nWSL2에서 다음 명령어로 확인하세요:" -ForegroundColor Cyan
    Write-Host "  ls -la /dev/ttyUSB* /dev/ttyACM*" -ForegroundColor Gray
    Write-Host "  cd <이_저장소>/tools && ./auto_detect_and_test.sh" -ForegroundColor Gray
} else {
    Write-Host "`n✗ 연결 실패. 오류를 확인해주세요." -ForegroundColor Red
    Write-Host "수동으로 시도:" -ForegroundColor Yellow
    Write-Host "  usbipd list" -ForegroundColor Gray
    Write-Host "  usbipd attach --wsl --busid $busid" -ForegroundColor Gray
}

