Param(
  [string]$API = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

Function Get-IdFromJson($json) {
  try {
    return ($json | ConvertFrom-Json).id
  } catch {
    return ""
  }
}

Write-Host "0) health"
$health = Invoke-RestMethod -Uri "$API/health" -Method GET
$health | ConvertTo-Json -Depth 5

Write-Host "1) default user"
$udoc = Invoke-WebRequest -UseBasicParsing -Uri "$API/api/v1/users/default" -Method GET
$uid = Get-IdFromJson $udoc.Content
if (-not $uid) {
  Write-Error "[ERR] users/default が不正"
  $udoc | Format-List *
  exit 1
}
Write-Host "uid=$uid"

Write-Host "2) assistant"
$abody = @{ name = "ConvBot" } | ConvertTo-Json
$adoc = Invoke-WebRequest -UseBasicParsing -Uri "$API/api/v1/assistants/" -Method POST -ContentType "application/json" -Body $abody
$aid = Get-IdFromJson $adoc.Content
if (-not $aid) { Write-Error "[ERR] assistants 作成が不正"; exit 1 }
Write-Host "aid=$aid"

Write-Host "3) conversation"
$cbody = @{ assistant_id = $aid; user_id = $uid; title = "Hello" } | ConvertTo-Json
$cdoc = Invoke-WebRequest -UseBasicParsing -Uri "$API/api/v1/conversations/" -Method POST -ContentType "application/json" -Body $cbody
$cid = Get-IdFromJson $cdoc.Content
if (-not $cid) { Write-Error "[ERR] conversations 作成が不正"; exit 1 }
Write-Host "cid=$cid"

Write-Host "4) message POST"
$mbody = @{ role = "user"; content = "hi" } | ConvertTo-Json
Invoke-WebRequest -UseBasicParsing -Uri "$API/api/v1/conversations/$cid/messages" -Method POST -ContentType "application/json" -Body $mbody | Out-Null

Write-Host "5) messages LIST"
$mlist = Invoke-RestMethod -Uri "$API/api/v1/conversations/$cid/messages" -Method GET
$mlist | ConvertTo-Json -Depth 6

