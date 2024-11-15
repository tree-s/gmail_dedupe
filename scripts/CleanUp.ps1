param (
    [string]$venvPath = "../venv"
)

deactivate

# Get the directory of the script
$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

$fullVenvPath = Join-Path -Path $scriptDir -ChildPath $venvPath

if (Test-Path $fullVenvPath) {
    Write-Output "Removing virtual environment directory: $fullVenvPath"
    Remove-Item -Recurse -Force $fullVenvPath
    Write-Output "Virtual environment directory removed."
} else {
    Write-Output "The specified path does not exist: $fullVenvPath"
}
