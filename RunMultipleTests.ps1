Param(
    [string]$inputFile = "mapname_g1t1_tc.txt",
    [int]$numRuns = 5
)

# Strip "_tc.txt" from the input filename for log and results files
$baseFileName = $inputFile -replace "_tc.txt", ""
$logFile = "$PWD\$baseFileName`_log.txt"
$resultsFile = "$PWD\$baseFileName`_results.txt"

# Clear the log and results files
Set-Content -Path $logFile -Value ""
Set-Content -Path $resultsFile -Value ""

# Function to check if the results are defective
function Is-Result-Defective {
    param (
        [string]$filePath
    )
    try {
        # Read the file content
        $fileContent = Get-Content -Path $filePath -ErrorAction Stop
        # Check if the third-to-last line contains "Lap time: "
        $lineToCheck = $fileContent[-3]  # Safely access the third-to-last line
        if ($lineToCheck -notmatch "Lap time: ") {
            return $true
        }
    } catch {
        Write-Host "Error reading file $filePath : $_"
        return $true
    }
    return $false
}

# Run the specified number of tests
for ($i = 1; $i -le $numRuns; $i++) {
    # Add a blank line for readability
    Add-Content -Path $logFile -Value "`n"
    Add-Content -Path $resultsFile -Value "`n"

    # Append run info to the log and results files
    $runInfo = "Run $i of $numRuns"
    Add-Content -Path $logFile -Value $runInfo
    Add-Content -Path $resultsFile -Value $runInfo

    # Run the test using RunAirSim.ps1
    Write-Host "Starting test $i of $numRuns..."
    .\RunAirSim.ps1 -f $inputFile

    # Check if the results are defective
    if (Is-Result-Defective -filePath $resultsFile) {
        $defectiveMessage = "This PID combination is defective"
        Write-Host $defectiveMessage

        # Prepend the defective message to both files
        $logContent = Get-Content -Path $logFile
        $resultsContent = Get-Content -Path $resultsFile

        Set-Content -Path $logFile -Value "$defectiveMessage`n$logContent"
        Set-Content -Path $resultsFile -Value "$defectiveMessage`n$resultsContent"

        break
    }
}

# Remove the first three lines from the log file
$logContent = Get-Content -Path $logFile
$trimmedLogContent = $logContent[3..($logContent.Length - 1)]  # Skip the first three lines
Set-Content -Path $logFile -Value ($trimmedLogContent -join "`n")

# Call the FindBestRun.py script
Write-Host "Calling FindBestRun.py to analyze results..."
python FindBestRun.py $resultsFile

Write-Host "All tests completed or stopped due to defective PID combination."
