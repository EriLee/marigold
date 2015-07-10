## getPresetPath ##

Retrieves a preset path based on MAYA\_SCRIPT\_PATH.

> @param **inPresetPath**: _String_. Preset path.

> @return: _String_. Preset path.

## getObjectShortName ##

Converts a long name to a short name.

> @param **inObjectName**: _String_. Full path name of object.

> @return: _String_. Short name of the object.

## writeModuleXML ##

Function for writing module xml.

> @param **inRootObjectName**: _String_. Name of module root object.

> @param **inModuleType**: _String_. Type of module. This determines which sub-folder the XML is saved.

> @param **inModuleName**: _String_. Name of the module XML file.

## readModuleXML ##

Processes an XML file to get the parts/settings for the module.

> @param **inFullPath**: _String_. Full directory path + filename + extension of the XML file.

> @return: _Dict_. Contents of XML file.

## loadModule ##

Loads a module into the scene.

> @param **inFolder**: _String_. Name for the sub-folder the module XML is located.

> @param **inFileName**: _String_. Name of the module XML.