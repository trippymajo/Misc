# Root for source files
$g_SourcesRootPath = 'C:\Users\RisingLion\Desktop\sources'

# Full file path to .txt file with list of pathes to scan with xgetext
$g_SavePathesFile = 'C:\Users\RisingLion\Desktop\PathsToScan.txt'

# Path to xgettext application 
$g_XgettextPath = 'C:\Program Files (x86)\GnuWin32\bin\xgettext.exe'

# Path to save output from xgettext
$g_XgettextOutput = 'C:\Users\RisingLion\Desktop\strings.po'

# Path checks
if (!(Test-Path $g_SourcesRootPath)) 
{
    Write-Host "ERROR: Source root path does not exist: $g_SourcesRootPath"
    exit 1
}
if (!(Test-Path $g_XgettextPath)) 
{
    Write-Host "ERROR: xgettext.exe not found: $g_XgettextPath"
    exit 2
}

# Get items as list and save in text file
try
{
    # Here define extensions of the files to parse
    $filePath = Get-ChildItem -Path $g_SourcesRootPath -Recurse -Include *.cpp,*.h -File 
    $fullFileNames = $filePath | Select-Object -ExpandProperty FullName

    if (!$fullFileNames -or $fullFileNames.Count -eq 0) 
    {
        Write-Host "WARNING: No source files were found in $g_SourcesRootPath"
        exit 3
    }

    Set-Content -Path $g_SavePathesFile -Value $fullFileNames -Encoding UTF8

    Write-Host "Full file paths were saved in: $g_SavePathesFile"
}
catch
{
    Write-Host "ERROR: Cannot write to $g_SavePathesFile. Exception: $_"
    exit 4
}

# Scan via XGetPath
try
{
    $txtFile = Get-Content $g_SavePathesFile
    # Here define functions to parse from code
    & $g_XgettextPath -ktr -kSupp_Translate -o $g_XgettextOutput $txtFile

    # Check if file was created
    if (!(Test-Path $g_XgettextOutput)) 
    {
        Write-Host "ERROR: xgettext haven't created output file: $g_XgettextOutput"
        exit 5
    }

    Write-Host "Strngs were saved in: $g_XgettextOutput"
}
catch
{
    Write-Host "ERROR: Failed to run xgettext.exe. Exception: $_"
    exit 6
}

