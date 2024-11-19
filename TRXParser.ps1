# It is hardcoded, so in order to integrate in to your test env 
# take care bout these variables
$testResultsPath = "C:\Users\WowSheCanPS\Desktop\tst"
$csvResultsPath = "C:\Users\WowSheCanPS\Desktop\tst\testDB.csv"
$trxName = "Test.trx"
$csvName = "testDB.csv"
# Those two vars are what you need to feed in to this script:
$version = "verHeader"
$timestamp = "timeHeader"

$arrLinesResult = @()

# If CSV exists open it and read into array
# with strict array casting to avoid type problems
if (Test-Path -Path $csvResultsPath) 
{
    $arrLinesResult = @(Get-Content -Path $csvResultsPath)
}

# Load TRX file
$mapTrxResults = @{}
[xml]$trxXml = Get-Content -Path "$($testResultsPath)\$($trxName)"

# Read all TRX lines into map
foreach ($val in $trxXml.TestRun.Results.UnitTestResult) 
{
    $mapTrxResults[$val.testName] = $val.outcome
}

$nArrSize = $arrLinesResult.Count

# Write first lines info for the CSV table
if ($nArrSize -gt 0) 
{
    $arrLinesResult[0] += ";$version"
    $arrLinesResult[1] += ";$timestamp"
}
else
{
    $arrLinesResult += ";$version"
    $arrLinesResult += ";$timestamp"
}

$nColumnsNum
$arrUpdLines = @()

# Read CSV, compare with map, update array for the future write in to file operation
for ($i = 2; $i -lt $nArrSize; $i++)
{
    $columns = $arrLinesResult[$i] -split ";"
    $nColumnsNum = $columns.Count
    $testName = $columns[0]

    if ($mapTrxResults.ContainsKey($testName))
    {
        $arrUpdLines += "$($arrLinesResult[$i]);$($mapTrxResults[$testName])" # Concat optimization here. Thats why the line overhelming
        $mapTrxResults.Remove($testName)
    }
    else
    {
        $arrUpdLines += "$($arrLinesResult[$i]);null"
    }
}

# Handle new added tests
foreach ($key in $mapTrxResults.Keys)
{
    $newLine = "$key"

    if ($nArrSize -gt 0) # Align columns with null & write new test results
    {
        $newLine += ((";" + "null") * ($nColumnsNum - 1)) + ";$($mapTrxResults[$key])"
    }
    else # The new CSV case
    {
        $newLine += ";$($mapTrxResults[$key])"
    }
    $arrUpdLines += $newLine
}

# Skip headers and write all updated lines back to the CSV
($arrLinesResult[0..1] + $arrUpdLines) -join "`n" | Set-Content -Path $csvResultsPath