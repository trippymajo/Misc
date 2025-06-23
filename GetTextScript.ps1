# Root for source files
$g_SourcesRootPath = 'C:\Users\RisingLion\Desktop\sources'

# Full file path to .txt file with list of pathes to scan with xgetext
$g_SavePathesFile = 'C:\Users\RisingLion\Desktop\PathsToScan.txt'

# Path to xgettext application 
$g_XgettextPath = 'C:\Program Files (x86)\GnuWin32\bin\xgettext.exe'

# Path to save output from xgettext
$g_XgettextOutput = 'C:\Users\RisingLion\Desktop\strings.po'


# Get items as list and save in text file
if (![string]::IsNullOrWhiteSpace($g_SourcesRootPath))
{
    $filePath = Get-ChildItem -Path $g_SourcesRootPath -Recurse -Include *.cpp,*.h -File 
    $fullFileNames = $filePath | Select-Object -ExpandProperty FullName
    Set-Content -Path $g_SavePathesFile -Value $fullFileNames

    Write-Host 'Full file paths were saved in: ' $g_SavePathesFile
}
else
{
    Write-Host 'RootPath is incorrect: ' $g_SavePathesFile
}

# Scan via XGetPath
if (![string]::IsNullOrWhiteSpace($g_XgettextPath))
{
    $txtFile = Get-Content $g_SavePathesFile
    # Here path functions to parse
    & $g_XgettextPath -ktr -kSupp_Translate -o $g_XgettextOutput $txtFile

    Write-Host 'Strngs were saved in: ' $g_SavePathesFile
}
else
{
    Write-Host 'xgettext path is incorrect ' $g_XgettextPath
}