$ErrorActionPreference = "Stop"

$Repo = if ($env:OPENFDE_SCHOOL_REPO) {
    $env:OPENFDE_SCHOOL_REPO
} else {
    "https://github.com/Alan-Youngzhe/OpenFDE-School.git"
}

$Target = if ($env:OPENFDE_SCHOOL_DIR) {
    $env:OPENFDE_SCHOOL_DIR
} else {
    Join-Path $HOME ".claude\skills\fde"
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "OpenFDE School needs Git. Open Claude Code and ask: 帮我检查并安装 Git，安装后运行 git --version 验证。"
}

$Parent = Split-Path -Parent $Target
New-Item -ItemType Directory -Force -Path $Parent | Out-Null

if (-not (Test-Path $Target)) {
    & git clone --depth 1 $Repo $Target
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
} elseif (Test-Path (Join-Path $Target ".git")) {
    $Dirty = & git -C $Target status --porcelain
    if ($LASTEXITCODE -ne 0) { throw "git status failed" }
    if ($Dirty) {
        throw "Refusing to overwrite local changes in $Target. Review or commit them before updating."
    }
    & git -C $Target pull --ff-only
    if ($LASTEXITCODE -ne 0) { throw "git pull --ff-only failed" }
} else {
    throw "Target exists but is not a Git checkout: $Target. Move it to a backup location and retry."
}

if (-not (Test-Path (Join-Path $Target "SKILL.md"))) {
    throw "Install verification failed: SKILL.md is missing"
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & python (Join-Path $Target "scripts\validate_school.py")
    if ($LASTEXITCODE -ne 0) { throw "OpenFDE School validation failed" }
}

Write-Host ""
Write-Host "OpenFDE School is ready at: $Target"
Write-Host "Open a new Claude Code session and type: /fde"
