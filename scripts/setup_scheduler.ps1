# FishNET Windows Task Scheduler Setup
# This script sets up a scheduled task to run the FishNET Sync Pipeline automatically.

param (
    [string]$Frequency = "DAILY", # Options: DAILY, HOURLY, ONLOGON
    [string]$Time = "08:00",      # Start time (HH:mm)
    [int]$IntervalHours = 1       # For HOURLY frequency
)

$TaskName = "FishNET_AutoSync_Pipeline"
$BatchPath = "C:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\scripts\run_sync.bat"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host " FishNET Automated Task Scheduler Setup" -ForegroundColor Yellow
Write-Host "=================================================" -ForegroundColor Cyan

# Unregister existing task if present
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing previous schedule for '$TaskName'..." -ForegroundColor Gray
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$Action = New-ScheduledTaskAction -Execute $BatchPath
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

switch ($Frequency.ToUpper()) {
    "DAILY" {
        $Trigger = New-ScheduledTaskTrigger -Daily -At $Time
        Write-Host "Configuring task to run DAILY at $Time." -ForegroundColor Green
    }
    "HOURLY" {
        $Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).ToString("HH:mm") -RepetitionInterval (New-TimeSpan -Hours $IntervalHours)
        Write-Host "Configuring task to run every $IntervalHours hour(s)." -ForegroundColor Green
    }
    "ONLOGON" {
        $Trigger = New-ScheduledTaskTrigger -AtLogOn
        Write-Host "Configuring task to run automatically at user LOGON." -ForegroundColor Green
    }
    default {
        $Trigger = New-ScheduledTaskTrigger -Daily -At $Time
        Write-Host "Configuring task to run DAILY at $Time." -ForegroundColor Green
    }
}

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Automated synchronization pipeline for Zebrafish FishNET Colony and Booking records."

Write-Host "`n[SUCCESS] Scheduled task '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "You can manage it anytime in Windows 'Task Scheduler'." -ForegroundColor Gray
