param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-CommandExists {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-PythonInvocation {
    param(
        [string]$Command,
        [string[]]$PrefixArguments = @()
    )

    try {
        if ($Command -like "* *" -and -not (Test-Path $Command)) {
            $parts = $Command.Split(" ", 2)
            & $parts[0] $parts[1] @PrefixArguments --version | Out-Null
        } else {
            & $Command @PrefixArguments --version | Out-Null
        }
        return $true
    } catch {
        return $false
    }
}

function Install-WithWinget {
    param(
        [string]$PackageId,
        [string]$Label
    )

    if (-not (Test-CommandExists "winget")) {
        throw "$Label is missing and winget is not available. Install $Label manually, then run setup again."
    }

    Write-Step "Installing $Label with winget"
    & winget install --id $PackageId --exact --accept-package-agreements --accept-source-agreements
}

function Resolve-PythonExecutable {
    $projectPath = (Resolve-Path $ProjectRoot).Path
    $venvPython = Join-Path $projectPath ".venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        if (Test-PythonInvocation -Command $venvPython) {
            return $venvPython
        }
    }

    if (Test-CommandExists "py") {
        if (Test-PythonInvocation -Command "py" -PrefixArguments @("-3")) {
            return "py -3"
        }
    }

    if (Test-CommandExists "python") {
        if (Test-PythonInvocation -Command "python") {
            return "python"
        }
    }

    Install-WithWinget -PackageId "Python.Python.3.12" -Label "Python 3"

    if (Test-CommandExists "py") {
        if (Test-PythonInvocation -Command "py" -PrefixArguments @("-3")) {
            return "py -3"
        }
    }

    if (Test-CommandExists "python") {
        if (Test-PythonInvocation -Command "python") {
            return "python"
        }
    }

    $pythonExe = Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -Recurse -Filter python.exe -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending |
        Select-Object -First 1 -ExpandProperty FullName

    if ($pythonExe) {
        if (Test-PythonInvocation -Command $pythonExe) {
            return $pythonExe
        }
    }

    throw "Python was installed, but the executable was not found on PATH. Reopen the terminal and run setup again."
}

function Invoke-ExternalCommand {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    if ($Command -like "* *" -and -not (Test-Path $Command)) {
        $parts = $Command.Split(" ", 2)
        & $parts[0] $parts[1] @Arguments
        return
    }

    & $Command @Arguments
}

$projectPath = (Resolve-Path $ProjectRoot).Path
$venvPath = Join-Path $projectPath ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$requirementsPath = Join-Path $projectPath "requirements.txt"
$packageJsonPath = Join-Path $projectPath "package.json"

Write-Step "Project root: $projectPath"

$pythonCommand = Resolve-PythonExecutable
Write-Step "Using Python: $pythonCommand"

if (-not (Test-Path $venvPython)) {
    Write-Step "Creating virtual environment"
    Invoke-ExternalCommand -Command $pythonCommand -Arguments @("-m", "venv", $venvPath)
} else {
    Write-Step "Virtual environment already exists"
}

Write-Step "Installing Python dependencies"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r $requirementsPath

if (Test-Path $packageJsonPath) {
    if (-not (Test-CommandExists "npm")) {
        Install-WithWinget -PackageId "OpenJS.NodeJS.LTS" -Label "Node.js LTS"
    }

    if (-not (Test-CommandExists "npm")) {
        throw "Node.js was installed, but npm is still not available on PATH. Reopen the terminal and run setup again."
    }

    Write-Step "Installing Node dependencies"
    Push-Location $projectPath
    try {
        & npm install
    } finally {
        Pop-Location
    }
}

Write-Step "Setup complete"
Write-Host "Use START_PROMPT_GENERATOR_WEB.bat to launch the app." -ForegroundColor Green
