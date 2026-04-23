$ErrorActionPreference = "Stop"

$container = "bank-robo-mysql"
$rootPw = "root_pw"
$dbName = "bank_robo"
$port = 3306

Write-Host ""
Write-Host "===== RESET MYSQL CONTAINER ====="

cmd /c "docker rm -f $container" 1>$null 2>$null

docker run -d `
  --name $container `
  -e MYSQL_ROOT_PASSWORD=$rootPw `
  -e MYSQL_DATABASE=$dbName `
  -p ${port}:3306 `
  mysql:8.4 | Out-Null

Write-Host "Container created: $container"
Write-Host ""

Write-Host "===== WAIT MYSQL READY ====="
$ready = $false
1..40 | ForEach-Object {
  Start-Sleep -Seconds 3
  docker exec -e MYSQL_PWD=$rootPw $container mysqladmin -h 127.0.0.1 -uroot ping --silent 1>$null 2>$null
  if ($LASTEXITCODE -eq 0) {
    $ready = $true
    break
  }
}

if (-not $ready) {
  Write-Host ""
  Write-Host "===== MYSQL NOT READY ====="
  docker ps -a --filter "name=$container"
  Write-Host ""
  docker logs --tail 120 $container
  throw "MySQL container not ready"
}

Write-Host ""
Write-Host "===== MYSQL READY ====="
docker ps --filter "name=$container"
Write-Host ""
Test-NetConnection -ComputerName localhost -Port $port | Select-Object ComputerName, RemotePort, TcpTestSucceeded
Write-Host ""

Write-Host "===== SQL PROBE ====="
docker exec -e MYSQL_PWD=$rootPw $container mysql -h 127.0.0.1 -P 3306 -uroot -D $dbName -e "SELECT DATABASE() AS db, NOW() AS now_ts;"
Write-Host ""
docker exec -e MYSQL_PWD=$rootPw $container mysql -h 127.0.0.1 -P 3306 -uroot -D $dbName -e "SHOW TABLES;"
Write-Host ""
docker exec -e MYSQL_PWD=$rootPw $container mysql -h 127.0.0.1 -P 3306 -uroot -D $dbName -e "SHOW TABLES LIKE 'transactions';"

Write-Host ""
Write-Host "===== MYSQL CLEAN READY ====="
Write-Host "Container : $container"
Write-Host "Database  : $dbName"
Write-Host "Port      : $port"
Write-Host ""