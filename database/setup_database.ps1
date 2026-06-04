# SQL Server Database Setup - PowerShell Script

param(
    [string]$ServerName = "localhost",
    [string]$UserName = "sa",
    [string]$Password = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SQL Server Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SQL Server is reachable
try {
    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=$ServerName;Integrated Security=false;User ID=$UserName;Password=$Password"
    $conn.Open()
    $conn.Close()
    Write-Host "✓ Connected to SQL Server: $ServerName" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to connect to SQL Server: $ServerName" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Verify SQL Server is running"
    Write-Host "2. Check server name: $ServerName"
    Write-Host "3. Verify credentials"
    Write-Host "4. Check firewall settings"
    exit 1
}

# Read schema file
$schemaPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$sqlFile = Join-Path $schemaPath "schema.sql"

if (-not (Test-Path $sqlFile)) {
    Write-Host "✗ schema.sql not found at: $sqlFile" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Found schema.sql" -ForegroundColor Green
Write-Host ""

# Execute schema
Write-Host "Creating database tables..." -ForegroundColor Yellow

try {
    $sqlScript = Get-Content $sqlFile -Raw

    $conn = New-Object System.Data.SqlClient.SqlConnection
    $conn.ConnectionString = "Server=$ServerName;Integrated Security=false;User ID=$UserName;Password=$Password"
    $conn.Open()

    $cmd = New-Object System.Data.SqlClient.SqlCommand
    $cmd.Connection = $conn
    $cmd.CommandTimeout = 300

    # Split by GO statements and execute each batch
    $batches = $sqlScript -split "GO\s*`n"

    foreach ($batch in $batches) {
        if ($batch.Trim() -ne "") {
            $cmd.CommandText = $batch
            [void]$cmd.ExecuteNonQuery()
        }
    }

    $conn.Close()

    Write-Host "✓ Database tables created successfully" -ForegroundColor Green
}
catch {
    Write-Host "✗ Error executing schema: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ Setup completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Demo Users:" -ForegroundColor Yellow
Write-Host "  Username: admin       Password: admin123"
Write-Host "  Username: dbadmin     Password: password123"
Write-Host "  Username: operator    Password: operator123"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Configure backend/.env with SQL Server credentials"
Write-Host "2. Install Python dependencies: pip install -r requirements.txt"
Write-Host "3. Start the application: python app.py"
Write-Host "4. Open browser: http://localhost:5000"
