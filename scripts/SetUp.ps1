param (
    [string]$requirementsPath = "../scripts/requirements.txt",
    [string]$activatePath = "../venv/Scripts/Activate.ps1"
)

# Get the directory of the script
$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

$fullRequirementsPath = Join-Path -Path $scriptDir -ChildPath $requirementsPath
$fullActivatePath = Join-Path -Path $scriptDir -ChildPath $activatePath

python -m venv venv
& $fullActivatePath
python -m pip install --upgrade pip
python -m pip install -r $fullRequirementsPath
