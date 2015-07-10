## wrapinstance ##

Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)

> @param **ptr**: Pointer to QObject in memory

> @return: _QWidget_ or subclass instance

## importModule ##

Imports a module using a string for the path.

> @param **inModuleName**: _String_. Full path of the module, separated by "."

> @return: The module!

## getMObjectName ##

Returns the name of an MObject.

> @param **inMObject**: _MObject_.

> @return: _String_. Name of MObject.

## searchSceneByName ##

Finds all objects with inSearchString in their name. Can use wildcard (**) in search.**

Example: Searching frame\_root**will return a list of all frame root objects.**

> @param **inSearchString**: _String_. Name to search for.

> @return: _List_. List of frame root names in string format.

## setUserColor ##

Sets the color of an object to the passed in user color.

> @param **inObjName**: _String_. Name of object.

> @param **userColor**: _Int_. 1-8. User defined color to use.

## convertRGB ##

Converts RGB values from 0-1 to 0-255 or back.

> @param **inRGB**: _List_. Three values representing RGB.

> @param **inType**: _Int_. 1 is 0-1 to 0-255. 2 is 0-255 to 0-1.

> @return: _List_. New RGB values.

## getUserDefinedColors ##

Get user defined colors.

> @param **inType**: _Int_. 1 is RGB. 2 is HSV.

> @return: _List_. User defined colors 1-8.

## createSpacer ##

Creates an empty group. Optionally, the group's transforms can be matched to another object.

> @param **inGroupName**: _String_. Name to give the new group.

> @param **inTargetObject**: _String_. Name of object to match the group's transforms to.

> @return: The newly created group.