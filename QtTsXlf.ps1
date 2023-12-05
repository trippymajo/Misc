$Qt_Path = Read-Host "Please enter QT Path i.e. C:\Qt\5.15.2\msvc2019_64\bin" #cin
$Sources_Path = Read-Host "Please enter Sources Path i.e. C:\Users\elya.shafeeva\Desktop\nCadC\Version7\sources" #cin
$Save_Path = Read-Host "Please enter Save Path i.e. C:\Users\elya.shafeeva\Desktop\Qt" #cin

$Files = Get-ChildItem $Sources_Path #Get all files from directory
foreach ($var in $Files)
{
    $Module_Name = $var.Name #Get Name of the Module
    $OutTs_Name = $Save_Path + "\" + $Module_Name + ".ts" # Output .TS full file name

    $Lupdate = $QT_Path + "\lupdate.exe" #For Lupdate.exe call
    $Lupdate_Params = $var.FullName + " -ts " + $OutTs_Name #Params for lupdate.exe call
    Start-Process -NoNewWindow -FilePath $Lupdate -ArgumentList $Lupdate_Params -Wait #Here it parses the directory with source files and saving .ts files

    $Lconvert = $QT_Path + "\lconvert.exe" #For Lconvert.exe call
    $Lconvert_Params = $OutTs_Name + " -o " + $Save_Path + "\" + $Module_Name + ".xlf" #Params for lconvert.exe call
    Start-Process -NoNewWindow -FilePath $Lconvert -ArgumentList $Lconvert_Params -Wait #Here it saves .ts file as .xlf file
    $Module_Name
}
"Phew! Done, now I tired ZzZ..."