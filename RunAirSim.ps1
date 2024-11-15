# Param(
#     [string]$f = "mapname_g1t1_tc.txt"
# )

# # Start AirSimExe.exe with the -windowed argument
# $airSimProcess = Start-Process -FilePath ".\AirSimExe.exe" -ArgumentList "-windowed" -PassThru

# # Wait for one second
# Start-Sleep -Seconds 1

# # Define the maximum wait time in seconds
# $maxWaitTime = 120

# # Start the Python script and pass the parameters file as an argument
# $startTime = Get-Date
# $pythonProcess = Start-Process -FilePath "python" -ArgumentList ".\flighttest.py $f" -NoNewWindow -PassThru

# # Monitor the Python script's execution
# while (-not $pythonProcess.HasExited) {
#     $elapsedTime = (Get-Date) - $startTime
#     if ($elapsedTime.TotalSeconds -ge $maxWaitTime) {
#         Write-Host "Python script exceeded $maxWaitTime seconds. Terminating the script."
#         # Optionally, kill the Python process if it exceeds the timeout
#         $pythonProcess | Stop-Process -Force
#         break
#     }
#     Start-Sleep -Seconds 1
# }

# # After the Python script completes or times out, force close AirSimExe.exe
# Write-Host "Closing AirSimExe.exe..."
# Get-Process -Name "AirSimExe" -ErrorAction SilentlyContinue | ForEach-Object { $_.Kill() }

Param(
    [string]$f = "mapname_g1t1_tc.txt"
)

# Define paths for output redirection
$stdoutPath = "$PWD\python_stdout.txt"
$stderrPath = "$PWD\python_stderr.txt"

# Start AirSimExe.exe with the -windowed argument
$airSimProcess = Start-Process -FilePath ".\AirSimExe.exe" -ArgumentList "-windowed" -PassThru

# Wait for one second
Start-Sleep -Seconds 1

# Define the maximum wait time in seconds
$maxWaitTime = 120

# Start the Python script and pass the parameters file as an argument
$startTime = Get-Date

# Ensure working directory is set correctly
$workingDir = $PWD

# Start Python script and redirect outputs
$pythonProcess = Start-Process -FilePath "python" `
    -ArgumentList ".\flighttest.py $f" `
    -NoNewWindow -PassThru `
    -WorkingDirectory $workingDir `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath

# Monitor the Python script's execution
while (-not $pythonProcess.HasExited) {
    $elapsedTime = (Get-Date) - $startTime
    if ($elapsedTime.TotalSeconds -ge $maxWaitTime) {
        Write-Host "Python script exceeded $maxWaitTime seconds. Terminating the script."
        # Kill the Python process if it exceeds the timeout
        $pythonProcess | Stop-Process -Force
        break
    }
    Start-Sleep -Seconds 1
}

# After the Python script completes or times out, force close AirSimExe.exe
Write-Host "Closing AirSimExe.exe..."
Get-Process -Name "AirSimExe" -ErrorAction SilentlyContinue | ForEach-Object { $_.Kill() }
