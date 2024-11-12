# It is hardcoded, so in order to integrate in to your test env 
# take care bout these variables
$testResultsPath = "C:\Users\WowSheCanPS\Desktop\tst"
$csvResultsPath = "C:\Users\WowSheCanPS\Desktop\tst\testDB.csv"
$trxName = "Test.trx"
$csvName = "testDB.csv"

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
    $testName = $val.testName
    $outcome = $val.outcome

    $mapTrxResults[$testName] = $outcome
}

$nArrSize = $arrLinesResult.Length
$nColumnsNum

if ($nArrSize -gt 0) # Case when CSV was read
{
    for ($i = 0; $i -lt $nArrSize; $i++)
    {
        $columns = $arrLinesResult[$i] -split ";"
        $nColumnsNum = $columns.Count
        $testName = $columns[0]

        if ($mapTrxResults.ContainsKey($testName))
        {
            $arrLinesResult[$i] += ";"
            $arrLinesResult[$i] += $mapTrxResults[$testName]
            $mapTrxResults.Remove($testName)
        }
        else
        {
            $arrLinesResult[$i] += ";null"
        }
    }
}

# Handle new added tests
if ($mapTrxResults.Count -gt 0)
{
    foreach ($ent in $mapTrxResults.GetEnumerator())
    {
        $testName = $ent.Key
        $testOutcome = $ent.Value

        if ($nArrSize -gt 0) # Align columns O(n^2) in this whole section
        {
            $newLine = $testName
        
            for ($i = 1; $i -lt $nColumnsNum - 1; $i++)
            {
                $newLine += ";null"
            }
            $newLine += ";"
            $newLine += $testOutcome

            $arrLinesResult += $newLine
        }
        else # The new CSV case
        {
            $newLine = $testName + ";" + "$testOutcome"
            $arrLinesResult += $newLine
        }
    }
}

# Write all updated lines back to the CSV
$arrLinesResult -join "`n" | Set-Content -Path $csvResultsPath