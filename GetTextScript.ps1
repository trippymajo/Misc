# Root path to source directory
$g_srcRoot = 'C:\Users\RisingLionOperation\Desktop\App\sources'

# Extensions to parse
$g_extensions = @('*.cpp','*.h','*.hpp','*.CPP','*.H')

# Path to xgettext.exe
$g_xgettext = 'C:\Program Files (x86)\GnuWin32\bin\xgettext.exe'

# xgettext.exe function flags (Functions to get strings from)
#, '-kSupp_Translate'
$g_gettextFlags = @('-kSupp_Translate')

# Temp dir for .po and .txt files
$g_tmpDir = 'C:\Users\RisingLionOperation\Desktop\gettext_tmp'

# Output result path
$g_outputFile = 'C:\Users\RisingLionOperation\Desktop\gettext_tmp\all_modules_strings.txt'


function createFilesToParseTxt()
{
    param 
    (
        [string]$ModuleDir,
        [string]$Module
    )

    # Params checks
    if ([string]::IsNullOrWhiteSpace($ModuleDir) -or !(Test-Path $ModuleDir)) 
    {
        Write-Host "ERROR: Module directory not found: $ModuleDir"
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($Module)) 
    {
        Write-Host "ERROR: Module name is empty."
        return $null
    }


    try
    {
        # Gathering all .cpp, .h and .hpp in module recursevily
        $files = Get-ChildItem -Path $ModuleDir -Recurse -Include $g_extensions -File | Select-Object -ExpandProperty FullName

        # Check if there any files in submodule
        if ($files.Count -eq 0) 
        {
            Write-Host "No source files found for module $Module"
            return $null
        }

        # Save subpath files list as .txt
        $fileListPath = Join-Path $g_tmpDir "${Module}_files.txt"
        Set-Content -Path $fileListPath -Value $files -Encoding UTF8 #Dunno lets stay safe with UTF8

        Write-Host "List of files in subfolder was saved to: $fileListPath"
        return $fileListPath
    }
    catch
    {
        Write-Host "ERROR: Exception occured while creating list (.txt) file to parse for module: $Module. Exception: $_"
        return $null
    }
}

function xgettextScan()
{
    param 
    (
        [string]$ModuleDir,
        [string]$Module,
        [string]$FileListPath
    )

    # Params checks
    if ([string]::IsNullOrWhiteSpace($ModuleDir) -or !(Test-Path $ModuleDir)) 
    {
        Write-Host "ERROR: Module directory not found: $ModuleDir"
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($Module)) 
    {
        Write-Host "ERROR: Module name is empty."
        return $null
    }
    if ([string]::IsNullOrWhiteSpace($FileListPath) -or !(Test-Path $FileListPath))
    {
        Write-Host "ERROR: List (.txt) with subfolder items was not found: $FileListPath"
        return $null
    }

    try
    {
        $files = @(Get-Content $FileListPath)
        $batchSize = 20
        $counter = 0
        $poFiles = @()

        for ($i = 0; $i -lt $files.Count; $i += $batchSize) 
        {
            $batch = $files[$i..([Math]::Min($i + $batchSize - 1, $files.Count - 1))]
            $poBatchPath = Join-Path $g_tmpDir "${Module}_batch$counter.po"

            & $g_xgettext @g_gettextFlags --language=c++ -o $poBatchPath $batch

            if (Test-Path $poBatchPath) 
            {
                # If batch was read and .po created all good!
                $poFiles += $poBatchPath
                $counter++
            } 
            else  # try line by line these file
            {
                foreach ($file in $batch)
                {
                    $poFilePath = Join-Path $g_tmpDir "${Module}_batch${counter}.po"
                    & $g_xgettext @g_gettextFlags --language=c++ -o $poFilePath $file

                    if (Test-Path $poFilePath) 
                    {
                        $poFiles += $poFilePath
                        $counter++
                    } 
                    else 
                    {
                        Write-Host "Problem scanning with gettext $file" -ForegroundColor Yellow
                    }
                }
            }
        }

        # Check how many .po has been created
        if ($poFiles.Count -eq 0) 
        {
            return $null
        }

        return $poFiles
    }
    catch
    {
        Write-Host "ERROR: .po file was not created, an exception occured. Exception: $_"
        return $null
    }
}

function makeWldFile()
{
    param 
    (
        [string]$Module,
        [array]$PoFiles
    )

    # Params checks
    if ([string]::IsNullOrWhiteSpace($Module)) 
    {
        Write-Host "ERROR: Module name is empty."
        return @(), 0
    }
    if ($PoFiles.Count -eq 0) 
    {
        Write-Host "ERROR: poFiles array is empty!"
        return @(), 0
    }

    try
    {
        # Aggregate all msgid strings from ALL batch po files
        $msgids = @()
        foreach ($poFile in $PoFiles) 
        {
            if (Test-Path $poFile) 
            {
                # Reading .po file lines
                $lines = Get-Content $poFile

                # Getting msgid lines with actual strings
                foreach ($line in $lines) 
                {
                    if ($line -match '^msgid "(.*)"$') 
                    {
                        $str = $Matches[1]
                        if ($str -ne "") { $msgids += $str }
                    }
                }
            }
        }

        # Output creating
        $out = @()
        $out += "### StartSubPath($Module) ###"
        $out += ""
        foreach ($s in $msgids) 
        { 
            $out += '"{0}"' -f $s
        }
        $out += ""
        $out += "### EndSubPath($Module)"
        $out += ""

        return $out, $($msgids.Count)
    }
    catch
    {
        Write-Host "ERROR: Exceptions occured while writing module to the output file. Exception: $_"
        return @(), 0
    }
}

#########################################################
# MAIN

# Create temp directory
if (!(Test-Path $g_tmpDir)) 
{ 
    New-Item -ItemType Directory -Path $g_tmpDir
}

# Clear Previous result file
if (Test-Path $g_outputFile) 
{ 
    Remove-Item $g_outputFile
}


# Parsing all sub-folders as modules
Get-ChildItem -Path $g_srcRoot -Directory | ForEach-Object {

    $moduleDir = $_.FullName
    $module = $_.Name

    $fileListPath = createFilesToParseTxt -ModuleDir $moduleDir -Module $module
    if ($null -eq $fileListPath) 
    { 
        Write-Host "Skip $module due createFilesToParseTxt returned null."; 
        return 
    }

    $poFiles = xgettextScan -ModuleDir $moduleDir -Module $module -FileListPath $fileListPath
    if ($null -eq $poFiles) 
    { 
        Write-Host "Skip $module due xgettextScan returned null."; 
        return 
    }

    $out, $nNumStrings = makeWldFile -Module $module -PoFiles $poFiles

    # Adding module to the output wld file
    if ($nNumStrings -gt 0)
    {
        Add-Content -Path $g_outputFile -Value $out -Encoding UTF8
    }
    Write-Host "Module $module processed: $nNumStrings strings."
}