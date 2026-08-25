$target = 50
Write-Host "Fetching following list for Shubh2-0..."
$following = gh api users/Shubh2-0/following --paginate --jq ".[].login"

$currentCount = $following.Count
Write-Host "Current Total Following: $currentCount"
Write-Host "Target Following: $target"

$needed = $currentCount - $target
if ($needed -le 0) {
    Write-Host "Already at or below 50. Done!"
    exit 0
}

$toUnfollow = $following | Select-Object -First $needed
Write-Host "Trimming $($toUnfollow.Count) accounts to reach exactly 50 following..."

$count = 0
foreach ($user in $toUnfollow) {
    gh api -X DELETE "user/following/$user" | Out-Null
    $count++
    $rem = $currentCount - $count
    Write-Host "[$count/$($toUnfollow.Count)] Unfollowed: $user (Remaining following: $rem)"
    Start-Sleep -Milliseconds 200
}

$finalCount = gh api users/Shubh2-0/following --paginate --jq ".[].login" | Measure-Object | Select-Object -ExpandProperty Count
Write-Host "Complete! Final total following: $finalCount"
