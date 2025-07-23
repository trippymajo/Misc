# Misc
 Miscellaneous small scripts/programs

## Python Scripts

### GetStringsScript
The script allows to parse C++, C functions and Qt's .ui files. Retrieves strings, and saves them in .txt near the script.
Quick start: python GetStringsScript.py C:\Dir --funcs "tr:str=1" 'translate:str=2,ctx=1' 'tr:str=1'

## PowerShell Scripts

### QtTsXlf
The script basicly allow you to retrive all strings in Qt which were used under translate(), save it as .ts file and after saving it as .xlf file.
This is useful in case you want strict module separation

### TRXParser
The script parses .trx file (MSTest resilt file) and outputs information in to the .csv file. With columns such as: Test Name, Result0, Result1 ... It also adds results and new tests automatically when another trx is fed to the same .csv file.

### GetTextScript
This script extracts string resources from any function that takes a const wchar_t* or const char* parameter, enabling easier localization of legacy Windows applications that use wchar or char routines.
It works with xgettext.exe from [GNU page official](https://www.gnu.org/software/gettext/gettext.html)

## C/C++ Console
### OwnRegExp
Compile with C++17!
I ve been tired of even thinking doing this manually so made this for taking xlf files and read strings to another file with diffrent code structure (Not XML-like code structure). May be later will be moved to job's project.

## C# Console
### MergeTranslations
.Net Framework 4.8
Could merge translations from import file to original one. Works with XML, read/write all the nodes of the XML-like file. Could be useful if you change hardcoded Attributes and its a good start for making your rules of merging the XMLs.

### MergeTranslationsv2
.Net Framework 4.8
A little changes to the MergeTranslations, which are aimed to 1) Make WLD file from XML 2) Get tanslations on XML from WLD. Here used no arguments, but a dialog-like console, for common people to understand what to do with this program.
