using System;
using System.Xml;

namespace XMLAttributeChanger
{
	class Program
	{
		static void Main(string[] args)
		{
			// Paths to the original XML file and importing XML file
			string originalXmlFilePath;
			string importingXmlFilePath;

			Console.WriteLine("Input original file path:");
			originalXmlFilePath = Console.ReadLine();
			Console.WriteLine("Input original file path:");
			importingXmlFilePath = Console.ReadLine();


			// Load XML files
			XmlDocument originalXml = new XmlDocument();
			XmlDocument importingXml = new XmlDocument();
			originalXml.Load(originalXmlFilePath);
			importingXml.Load(importingXmlFilePath);

			ProcessXmlNodes(originalXml.DocumentElement, importingXml.DocumentElement);

			// Save the modified XML to a new file
			string modifiedXmlFilePath = "merged.xml";
			originalXml.Save(modifiedXmlFilePath);

			// Show success message
			Console.WriteLine("Attribute 'Text' updated successfully!");
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
					
					if (uidAttribute != null && uidAttribute.Value.Length != 0)
					{
						importingMatchingNode = FindImportingNode(importingNode, uidAttribute.Value);
					}
					else if (menuMacroIdAtt != null && menuMacroIdAtt.Value.Length !=0)
					{
						importingMatchingNode = FindImportingNode(importingNode, menuMacroIdAtt.Value);
					}
					else
					{
						importingMatchingNode= null;
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