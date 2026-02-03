# PowerShell script to create Render Postgres DB and Web Service using your Render API key.
# USAGE:
# 1) Set the API key in your shell (recommended):
  $env:RENDER_API_KEY = "rnd_KTYV8iIJuOnIOEZSOwSd2aznsDYO"
# 2) Run this script from the repo root (where render.yaml / Procfile exist):
#    powershell -ExecutionPolicy Bypass -File .\scripts\create_render_resources.ps1
#
# SECURITY: Do NOT paste your API key in chat. Keep it in the environment.

param()

function ExitWith($msg) {
    Write-Error $msg
    exit 1
}

if (-not $env:RENDER_API_KEY) {
    Write-Host "RENDER_API_KEY not found in environment. You can paste it now (it will not be stored):"
    $secureKey = Read-Host -AsSecureString "Render API Key"
    if (-not $secureKey) { ExitWith "No API key provided." }
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    $env:RENDER_API_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
}

$ApiBase = "https://api.render.com/v1"
$headers = @{ Authorization = "Bearer $env:RENDER_API_KEY"; "Content-Type" = "application/json" }

# Config (edit if you want different names/region)
$dbName = "academyproject-db"
$serviceName = "academyproject-web"
$repoUrl = "https://github.com/xkoderfx13/AcademyProject"
$branch = "main"
$region = "oregon"
$plan = "starter"

Write-Host "Creating Postgres database '$dbName' on Render..."
$dbPayload = @{
    name = $dbName
    region = $region
    plan = $plan
    # Render's API may expect slightly different keys; if this call fails,
    # inspect the returned error and adjust fields accordingly.
} | ConvertTo-Json

try {
    $dbResp = Invoke-RestMethod -Uri "$ApiBase/databases" -Method Post -Headers $headers -Body $dbPayload -ErrorAction Stop
    Write-Host "Database creation response:`n" ($dbResp | ConvertTo-Json -Depth 5)
} catch {
    Write-Error "Database creation failed: $_.Exception.Response.Content"; 
    Write-Host "If this fails, please open the Render dashboard and create the managed Postgres database manually, then set the DATABASE_URL environment variable for the service."
}

Write-Host "Creating Web Service '$serviceName' linking repo $repoUrl ..."
$servicePayload = @{
    name = $serviceName
    repo = $repoUrl
    branch = $branch
    env = "python"
    plan = $plan
    buildCommand = "pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput"
    startCommand = "gunicorn myproject.wsgi --bind 0.0.0.0:\$PORT"
    envVars = @(
        @{ key = "DEBUG"; value = "False" },
        @{ key = "DJANGO_SECRET_KEY"; value = [guid]::NewGuid().ToString() }
    )
} | ConvertTo-Json -Depth 6

try {
    $svcResp = Invoke-RestMethod -Uri "$ApiBase/services" -Method Post -Headers $headers -Body $servicePayload -ErrorAction Stop
    Write-Host "Service creation response:`n" ($svcResp | ConvertTo-Json -Depth 5)
    Write-Host "
If the API created the service successfully you should see it in your Render dashboard."
} catch {
    Write-Error "Service creation failed: $_.Exception.Response.Content"
    Write-Host "Common reasons: repository not authorized for Render, missing GitHub integration, or payload fields mismatch."
    Write-Host "If service creation fails due to repo authorization, go to https://dashboard.render.com and connect your GitHub account and the repository, then re-run this script."
}

Write-Host "Done. Please go to your Render dashboard to verify the Web Service and Database."
Write-Host "IMPORTANT: If you pasted your API key interactively, consider unsetting it now: Remove-Item Env:\RENDER_API_KEY"
