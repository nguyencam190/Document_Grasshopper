# ==========================================================================
#  Cai Python cho cac MCP server. Khong dung file nay de sua Python cua Maya
#  (Maya co Python rieng ben trong, khong cai de len duoc).
#
#  Chay qua cai_python.bat, dung goi thang file nay.
# ==========================================================================
$ErrorActionPreference = "Stop"
$ProgressPreference    = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$MIN = [version]"3.10"
$MUON = "3.12"          # ban muon cai neu chua co

function Doc-Version($exe, $tuychon) {
    try {
        $out = & $exe @tuychon --version 2>&1
        if ($out -match "Python (\d+\.\d+\.\d+)") { return [version]$Matches[1] }
    } catch { }
    return $null
}

function Python-Dang-Co {
    foreach ($ung in @(@{e="py";a=@("-3")}, @{e="python";a=@()})) {
        if (Get-Command $ung.e -ErrorAction SilentlyContinue) {
            $v = Doc-Version $ung.e $ung.a
            if ($v -and $v -ge $MIN) { return $v }
        }
    }
    return $null
}

# ---------------------------------------------------------------- da co chua
$co = Python-Dang-Co
if ($co) {
    Write-Host ""
    Write-Host "Da co Python $co (>= $MIN). Khong can cai gi them." -ForegroundColor Green
    exit 0
}
Write-Host "Chua thay Python $MIN tro len. Bat dau cai $MUON..." -ForegroundColor Yellow

# ------------------------------------------------------------ cach 1: winget
$xong = $false
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "`n[1/2] Thu cai bang winget (co san tren Windows 10/11)..."
    try {
        winget install -e --id "Python.Python.$MUON" --scope user `
               --accept-package-agreements --accept-source-agreements
        if ($LASTEXITCODE -eq 0) { $xong = $true }
        else { Write-Host "winget tra ve ma loi $LASTEXITCODE - chuyen sang cach 2." -ForegroundColor Yellow }
    } catch {
        Write-Host "winget that bai: $($_.Exception.Message) - chuyen sang cach 2." -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[1/2] May khong co winget - chuyen sang cach 2."
}

# ------------------------------------------- cach 2: tai thang tu python.org
if (-not $xong) {
    Write-Host "`n[2/2] Tai bo cai tu python.org..."
    $goc = "https://www.python.org/ftp/python/"
    $trang = Invoke-WebRequest -UseBasicParsing -Uri $goc
    $pat = 'href="' + [regex]::Escape($MUON) + '\.(\d+)/"'
    $so = [regex]::Matches($trang.Content, $pat) |
          ForEach-Object { [int]$_.Groups[1].Value } |
          Sort-Object -Unique -Descending
    if (-not $so) { throw "Khong tim thay ban $MUON nao tren python.org" }

    $tai = $null
    foreach ($n in $so) {
        $ver = "$MUON.$n"
        $url = "$goc$ver/python-$ver-amd64.exe"
        try {
            Invoke-WebRequest -UseBasicParsing -Method Head -Uri $url | Out-Null
            $tai = @{ ver = $ver; url = $url }
            break
        } catch { }        # ban do khong co file amd64, thu ban thap hon
    }
    if (-not $tai) {
        # May chu tu choi HEAD chu chua han la khong co file. Lay ban cao nhat
        # roi de buoc tai that bao loi, thay vi dung lai o day.
        $ver = "$MUON.$($so[0])"
        Write-Host "    (khong kiem tra truoc duoc, thu thang ban $ver)"
        $tai = @{ ver = $ver; url = "$goc$ver/python-$ver-amd64.exe" }
    }

    $dich = Join-Path $env:TEMP "python-$($tai.ver)-amd64.exe"
    Write-Host "    Ban moi nhat: $($tai.ver)"
    Write-Host "    Dang tai ve $dich ..."
    Invoke-WebRequest -UseBasicParsing -Uri $tai.url -OutFile $dich

    Write-Host "    Dang cai (im lang, khoang 1-2 phut)..."
    $p = Start-Process -FilePath $dich -Wait -PassThru -ArgumentList @(
        "/quiet", "InstallAllUsers=0", "PrependPath=1", "Include_pip=1", "Include_test=0")
    if ($p.ExitCode -ne 0) { throw "Bo cai Python tra ve ma loi $($p.ExitCode)" }
    Remove-Item $dich -ErrorAction SilentlyContinue
}

# --------------------------------------------------------------- kiem tra lai
# PATH cua cua so nay khong tu cap nhat sau khi cai -> nap lai tu registry
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "User")

$co = Python-Dang-Co
Write-Host ""
if ($co) {
    Write-Host ("=" * 56) -ForegroundColor Green
    Write-Host "XONG. Da cai Python $co" -ForegroundColor Green
    Write-Host "Buoc tiep theo: bam dup cai_dat_mcp.bat" -ForegroundColor Green
    Write-Host ("=" * 56) -ForegroundColor Green
    exit 0
} else {
    Write-Host ("=" * 56) -ForegroundColor Yellow
    Write-Host "Da cai xong nhung cua so nay chua thay Python." -ForegroundColor Yellow
    Write-Host "Dong het cua so CMD/PowerShell, mo lai cai moi roi go:" -ForegroundColor Yellow
    Write-Host "    python --version" -ForegroundColor Yellow
    Write-Host "Van khong ra thi khoi dong lai may." -ForegroundColor Yellow
    Write-Host ("=" * 56) -ForegroundColor Yellow
    exit 1
}
