using System;
using System.IO;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Xml;
using static System.Net.Mime.MediaTypeNames;

namespace XMLAttributeChanger
{
	class Program
	{
		//Goddamn why do I used all static... May be I was a lazy ass here...
		static string originalXmlFilePath = null;
		static string importingXmlFilePath = null;

		static void Main(string[] args)
		{
			// Paths to the original XML file and importing XML file
			Console.WriteLine("Input original file path:");
			Program.originalXmlFilePath = Console.ReadLine();
			Console.WriteLine("Input translated file path:");
			importingXmlFilePath = Console.ReadLine();


			// Load XML files
			XmlDocument originalXml = new XmlDocument();
			XmlDocument importingXml = new XmlDocument();
			originalXml.Load(originalXmlFilePath);
			importingXml.Load(importingXmlFilePath);

			ProcessXmlNodes(originalXml.DocumentElement, importingXml.DocumentElement);

			// Save the modified XML to a new file
			
			
			originalXml.Save(GetSavingFileName(importingXmlFilePath, "merged.xml"));

			// Show success message
			Console.WriteLine("Attribute 'Text' updated successfully!");
		}

		static string GetSavingFileName(string importingXmlFilePath, string newFileName)
		{
			string retVal;
			string[] pathPiece = importingXmlFilePath.Split('\\');

			pathPiece[pathPiece.Length - 1] = newFileName;
			retVal = string.Join("\\",pathPiece);

			return retVal;
		}

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

				if (textAttribute != null)
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

					if (importingMatchingNode != null)
					{
						// Update the 'Text' attribute of the original node with importing node's 'Text' attribute value
						textAttribute = originalNode.Attributes["Text"];
						if (textAttribute != null)
						{
							textAttribute.Value = importingMatchingNode.Attributes["Text"].Value;
						}
					}
					else
					{
						//Here we are writening the delta of the two files (or untranslated lines)
						int i = 0;
						string appendText = null;
						while (originalNode.OuterXml[i] != '>')
						{
							appendText += originalNode.OuterXml[i];
							i++;
						}
						File.AppendAllText(GetSavingFileName(importingXmlFilePath, "delta.txt"), appendText + ">\n");
					}
				}
			}

			// Process all child nodes recursively
			foreach (XmlNode originalChildNode in originalNode.ChildNodes)
			{
					ProcessXmlNodes(originalChildNode, importingNode);
			}
		}

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