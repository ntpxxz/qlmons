# Drop and recreate SqlSecurityHUD database

# Load .env file
$envFile = "../backend/.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

$sqlServer = [Environment]::GetEnvironmentVariable("SQL_SERVER")
$sqlUser = [Environment]::GetEnvironmentVariable("SQL_USER")
$sqlPassword = [Environment]::GetEnvironmentVariable("SQL_PASSWORD")

Write-Host "Dropping existing SqlSecurityHUD database..."
sqlcmd -S $sqlServer -U $sqlUser -P $sqlPassword -Q @"
ALTER DATABASE SqlSecurityHUD SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
DROP DATABASE IF EXISTS SqlSecurityHUD;
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "Running schema.sql to recreate database..."
    sqlcmd -S $sqlServer -U $sqlUser -P $sqlPassword -i "schema.sql"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Database recreated successfully"
    } else {
        Write-Host "[ERROR] Error running schema.sql"
    }
} else {
    Write-Host "[ERROR] Error dropping database"
}
