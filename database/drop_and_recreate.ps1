# Drop and recreate SqlSecurityHUD database
# Update these with your SQL Server credentials from .env

$sqlServer = $env:SQL_SERVER -or "192.168.101.219"
$sqlUser = $env:SQL_USER -or "DATALYZER"
$sqlPassword = $env:SQL_PASSWORD

Write-Host "Dropping existing SqlSecurityHUD database..."
sqlcmd -S $sqlServer -U $sqlUser -P $sqlPassword -Q "DROP DATABASE IF EXISTS SqlSecurityHUD;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Running schema.sql to recreate database..."
    sqlcmd -S $sqlServer -U $sqlUser -P $sqlPassword -i "schema.sql"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database recreated successfully"
    } else {
        Write-Host "✗ Error running schema.sql"
    }
} else {
    Write-Host "✗ Error dropping database"
}
