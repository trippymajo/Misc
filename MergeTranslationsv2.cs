using System;
using System.IO;
using System.Xml;
using System.Text;
using System.Xml.Linq;
using System.Text.RegularExpressions;
using System.Web;
using System.Runtime.InteropServices.WindowsRuntime;

namespace XMLAttributeChanger
{
	class Program
	{
		//Goddamn why do I used all static... May be I was a lazy ass here...
		static string originalFilePath = null;
		static string importingFilePath = null;
    static StreamWriter wldWriter = null;

		static void Main(string[] args)
    {
      Console.WriteLine("-xml - port translations 2XMLs2WLD and write a WLD file\n-wld - port translations WLD2XML in a new XML file");
      string option = Console.ReadLine();
      switch (option)
      {
        case "-xml" : 
          PortTranslationsXML();
          break;
        case "-wld":
          PortTranslationsWLD();
          break;
        default:
          Console.WriteLine("Wrong option!!!");
          break;
      }
		}

    //Importing translations from WLD file on XML file. WLD->XML. String-by-String comparision
    static void PortTranslationsWLD()
    {
      // Paths to the original XML file and importing WLD file
      Console.WriteLine("Input XML file to put translations on:");
      originalFilePath = Console.ReadLine();
      Console.WriteLine("Input translated WLD path:");
      importingFilePath = Console.ReadLine();

      //new XML file creating
      string newXMLFilePath = GetSavingFileName(originalFilePath, "RibbonTabsAndPanels(Translated).xml");
      File.Copy(originalFilePath, newXMLFilePath, true);

      //For reading and changing nodes of the XML
      XmlDocument newXml = new XmlDocument();
      try
      {
        newXml.Load(newXMLFilePath);
      }
      catch (Exception ex)
      {
        Console.WriteLine(ex.Message);
        Console.ReadLine();
      }

      ProcessXmlNodes(newXml.DocumentElement);

      newXml.Save(newXMLFilePath);
      Console.WriteLine("Translations ported successfully!");
      Console.ReadLine();
    }

    //Processes all the xmlNodes in the xml file WLD2XML
    static void ProcessXmlNodes(XmlNode originalNode)
    {
      if (originalNode == null)
        return;
      // Check if the current original node has 'UID' attribute
      if (originalNode.Attributes != null)
      {
        XmlAttribute textAttribute = originalNode.Attributes["Text"];
        if (textAttribute != null || (originalNode.FirstChild != null && originalNode.FirstChild.NodeType == XmlNodeType.Text))
        {
          if (textAttribute != null)
          {
            textAttribute.Value = FindTranslation(textAttribute.Value);
          }
          else
          {
            originalNode.FirstChild.InnerText = FindTranslation(originalNode.InnerText);
          }
        }
      }

      // Process all child nodes recursively
      foreach (XmlNode originalChildNode in originalNode.ChildNodes)
      {
        ProcessXmlNodes(originalChildNode);
      }
    }

    //Find translation for the Attribute
    static string FindTranslation(string value)
    {
      bool bFound = false;
      string retVal = value;
      string wld1stString = null;

      //Open WLD file
      Stream wldStream = File.OpenRead(importingFilePath);
      StreamReader wldReader = new StreamReader(wldStream, new UTF8Encoding(true));

      while (!wldReader.EndOfStream && !bFound)
      {
        wld1stString = wldReader.ReadLine();
        if (wld1stString.Contains(value))
        {
          retVal = wldReader.ReadLine();
          if (retVal.Length > 2)
          {
            retVal = retVal.Substring(1, retVal.Length - 2);
            bFound = true;
          }
        }
      }

      wldReader.Close();
      wldStream.Close();

      return retVal;
    }

    //Importing translations from XML file on WLD file. 2XML->WLD.
    static void PortTranslationsXML()
    {
      // Paths to the original XML file and importing XML file
      Console.WriteLine("Input original file XML path:");
      originalFilePath = Console.ReadLine();
      Console.WriteLine("Input translated file XML path:");
      importingFilePath = Console.ReadLine();

      // Load XML files
      XmlDocument originalXml = new XmlDocument();
      XmlDocument importingXml = new XmlDocument();
      try
      {
        originalXml.Load(originalFilePath);
        importingXml.Load(importingFilePath);
      }
      catch (Exception ex)
      {
        Console.WriteLine(ex.Message);
        Console.ReadLine();
      }

      Stream wldStream = File.OpenWrite(GetSavingFileName(importingFilePath, "RibbonTabsAndPanels.wld"));
      wldWriter = new StreamWriter(wldStream, new UTF8Encoding(true));
      MakeWLDStructure(true);

      ProcessXmlNodes(originalXml.DocumentElement, importingXml.DocumentElement);

      MakeWLDStructure(false);
      //originalXml.Save(GetSavingFileName(importingXmlFilePath, "merged.xml"));

      wldWriter.Close();
      wldStream.Close();
      // Show success message
      Console.WriteLine("A wild WLD file has appeared!");
      Console.ReadLine();
    }

    //Making WLD Structure for the outputWldFile.
    //Params bool isStartModule: 1-Module start structure 2-Module end structure
    static void MakeWLDStructure (bool isStartModule)
    {
      string appendText;
      if (isStartModule)
      {
        appendText = ";{{Module(\\RibbonTabsAndPanels){{Path()}}\r\n;{{Strings\r\n";
      }
      else
      {
        appendText = ";}}Strings\r\n;}}Module(\\RibbonTabsAndPanels)";
      }
      wldWriter.WriteLine(appendText);
    }

    //Returns new full file path based on importingXmlFilePath
		static string GetSavingFileName(string filePath, string newFileName)
		{
			string retVal;
			string[] pathPiece = filePath.Split('\\');

			pathPiece[pathPiece.Length - 1] = newFileName;
			retVal = string.Join("\\",pathPiece);

			return retVal;
		}

    //Processes all the xmlNodes in the xml file XML2XML
    static void ProcessXmlNodes(XmlNode originalNode, XmlNode importingNode)
		{
			if (originalNode == null)
				return;
			// Check if the current original node has 'UID' attribute
			if (originalNode.Attributes != null)
			{
				XmlAttribute textAttribute = originalNode.Attributes["Text"];
				XmlAttribute uidAttribute = originalNode.Attributes["UID"];
				XmlAttribute menuMacroIdAtt = originalNode.Attributes["MenuMacroID"];

				if (textAttribute != null || (originalNode.FirstChild != null && originalNode.FirstChild.NodeType == XmlNodeType.Text))
				{
					XmlNode importingMatchingNode;

					if (menuMacroIdAtt != null && menuMacroIdAtt.Value.Length != 0)
					{
						importingMatchingNode = FindImportingNode(importingNode, menuMacroIdAtt.Value);
					}
					else if (uidAttribute != null && uidAttribute.Value.Length != 0)
					{
						importingMatchingNode = FindImportingNode(importingNode, uidAttribute.Value);
					}
					else
					{
						importingMatchingNode = null;
					}

          string originalString;
          if (textAttribute != null)
          {
            originalString = textAttribute.Value;
          }
          else
          {
            originalString = originalNode.FirstChild.InnerText;
          }
          wldWriter.WriteLine("\"" + originalString + "\"");
          if (importingMatchingNode != null)
					{
						if (textAttribute != null)
						{
							 // Update the 'Text' attribute of the original node with importing node's 'Text' attribute value
							textAttribute.Value = importingMatchingNode.Attributes["Text"].Value;
              wldWriter.WriteLine("\"" + textAttribute.Value + "\"\r\n");
            }
						else
						{
							// Update the Child Node which has a XmlNodeType.Text
							originalNode.FirstChild.InnerText = importingMatchingNode.FirstChild.InnerText;
              wldWriter.WriteLine("\"" + importingMatchingNode.FirstChild.InnerText + "\"\r\n");
            }
					}
          else
          {
            wldWriter.WriteLine("\"" + originalString + "\"\r\n");
          }
				}
			}

			// Process all child nodes recursively
			foreach (XmlNode originalChildNode in originalNode.ChildNodes)
			{
					ProcessXmlNodes(originalChildNode, importingNode);
			}
		}

    //Finds the exact xmlNode that has indentifiers such as UID or MenuMacroID
    static XmlNode FindImportingNode(XmlNode importingNode, string value)
		{
			if (importingNode == null)
				return null;

			if (importingNode.Attributes != null)
			{
				XmlAttribute uidAttribute = importingNode.Attributes["UID"];
				XmlAttribute menuMacroIdAtt = importingNode.Attributes["MenuMacroID"];

				if (uidAttribute != null && uidAttribute.Value == value)
				{
					return importingNode;
				}
				if (menuMacroIdAtt != null && menuMacroIdAtt.Value == value)
				{
					return importingNode;
				}
			}

				// Recursively search for the importing node with matching 'UID' attribute
				foreach (XmlNode importingChildNode in importingNode.ChildNodes)
				{
					XmlNode matchingNode = FindImportingNode(importingChildNode, value);
					if (matchingNode != null)
					{
						return matchingNode;
					}
				}
			return null;
		}
	}
}