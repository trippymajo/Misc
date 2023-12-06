#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <regex>

using namespace std;

//Make out full file name
//string makeOutName(const string &sFilePath)
//{
//  string sRetVal(sFilePath);
//  int iSize = sRetVal.size();
//  sRetVal.replace(iSize - 3, iSize, "wld");
//  return sRetVal;
//}

//Makes a wld structure for the file
void startModuleStruct(ofstream &out, const string &sModuleName)
{
  out << ";{{Module(" << sModuleName << "){{Path()}}\n";
  out << ";{{Strings\n\n";
}

//Ends a wld structure for the file
void endModuleStruct(ofstream& out, const string &sModuleName)
{
  out << ";}}Strings\n";
  out << ";}}Module(" << sModuleName << ")\n";
}

//Makes string pairs like in wld
void stringStruct(ofstream &out, string &sWrite)
{
  if (sWrite.empty())
    return;

  sWrite[0] = '"';
  sWrite[sWrite.size() - 1] = '"';

  out << sWrite << "\n";
  out << sWrite << "\n\n";
}

string getModuleName(const string& sFilePath)
{
  string sRetVal = sFilePath.substr(sFilePath.find_last_of("/\\") + 1);
  sRetVal.resize(sRetVal.size() - 4);
  return sRetVal;
}

//Parse the file to find strings which are need to be taken to out file
void proceedFile(string sFilePath, ofstream &out)
{
  string sLine;
  string sModuleName(getModuleName(sFilePath));
  
  ifstream in(sFilePath);


  if (!(in.is_open() && out.is_open()))
    return;

  startModuleStruct(out, sModuleName);

  while (getline(in, sLine))
  {
    if (sLine.find("source xml:space=\"preserve\"") != string::npos)
    {
      string sWrite;
      smatch searchMatch;
      regex_search(sLine, searchMatch, (regex)R"(>(.*?)<)");
      sWrite = searchMatch[0];
      stringStruct(out, sWrite);
    }
  }
  endModuleStruct(out, sModuleName);
  
  in.close();
}

int main()
{
  namespace fs = std::filesystem;

  string sFilePath;

  cout << "Type in file path. i.e. C:\\Users\\elya.shafeeva\\Desktop\\150complect\n";
  cin >> sFilePath;

  ofstream out(sFilePath + "\\OutPut.wld", ios::app);

  for (const auto& entry : fs::directory_iterator(sFilePath))
  {
    proceedFile(entry.path().string(), out);
  }
  out.close();

  return 1;
}

// Run program: Ctrl + F5 or Debug > Start Without Debugging menu
// Debug program: F5 or Debug > Start Debugging menu

// Tips for Getting Started: 
//   1. Use the Solution Explorer window to add/manage files
//   2. Use the Team Explorer window to connect to source control
//   3. Use the Output window to see build output and other messages
//   4. Use the Error List window to view errors
//   5. Go to Project > Add New Item to create new code files, or Project > Add Existing Item to add existing code files to the project
//   6. In the future, to open this project again, go to File > Open > Project and select the .sln file
