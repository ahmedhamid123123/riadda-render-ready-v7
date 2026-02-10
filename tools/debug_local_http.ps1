try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000' -UseBasicParsing -TimeoutSec 5
    Write-Host "STATUS: $($r.StatusCode)"
    Write-Host "LENGTH: $($r.Content.Length)"
    $s = $r.Content
    if ($s.Length -gt 400) { $s = $s.Substring(0,400) }
    Write-Host "PREVIEW:`n$s"
} catch {
    Write-Host "Request failed:" 
    Write-Host $_.Exception.Message
}
