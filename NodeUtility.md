# Introduction #

This module contains useful functions for manipulating dag nodes.

# Functions #

## connectPlugs ##

Connects one plug to another.

> @param **inSourcePlug**: _String_. Name of the source plug formatted as Nodename.Plugname.

> @param **inDestinationPlug**: _String_. Name of the destination plug formatted as Nodename.Plugname.

## attributeCheck ##

Check an object for a given attribute.

> @param **inObj**: _String_. Name of an object.

> @param **inAttribute**: _String_. Name of an attribute.

> @return: True if the attribute exists. Otherwise False.

## connectNodes ##

Connect two nodes using the API.

> @param **inParentObj**: _String_. Name of parent node.

> @param **inParentPlug**: _String_. Name of plug on parent node.

> @param **inChildObj**: _String_. Name of child node.

> @param **inChildPlug**: _String_. Name of plug on child node.

## disconnectNodes ##

Disconnects two nodes using the API.

> @param **inParentObj**: _String_. Name of the parent node.

> @param **inParentPlug**: _String_. Name of plug on the parent node.

> @param **inChildObj**: _String_. Name of child node.

> @param **inChildPlug**: _String_. Name of plug on the child node.

## getNodeAttrDestination ##

Gets the destination of an attribute on the given node.

> @param **inNode**: _String_. Node with the desired attribute.

> @param **inAttr**: _String_. Name of source attribute.

> @return: Returns list containing the destination attribute and it's node.

## getNodeAttrSource ##

Gets the source of an attribute on the given node.

> @param **inNode**: _String_. Node with the desired attribute.

> @param **inAttr**: _String_. Name of source attribute.

> @return: Returns list containing the source attribute and it's node.

## getDependNode ##

Gets an object's MObject by it's string name.

> @param **inObj**: _String_. Name of object.

> @return: MObject.

## getDagPath ##

Takes an object name as a string and returns its dag path.

> @param **inObjName**: _String_. Name of object.

> @return: Dag path.

## isValidMPlug ##

Checks to see if the passed in object is an instance of MPlug.

> @param **inObj**: _MObject_. Maya object.

> @return: Bool.

## addPlug ##

Adds a plug to an object.

> @param **inBit**: _String_. Name of the bit to add the attribute to.

> @param **inPlugName**: _String_. Name of the plug to add.

> @param **inAttrType**: _String_. Type of attribute to add.

> @param **inAttrDataType**: _String_. The attribute data type.

## convertAttrString ##

Converts a string into the appropriate type.

> @param **inAttrDataType**: _String_. The attribute data type.

> @param **inValue**: _String_. Value to convert.

> @return: Correct value.

## setPlug ##

Sets the value of the plug.

> @param **inBit**: _String_. Name of the bit with the plug.

> @param **inPlugName**: _String_. Name of the plug to add.

> @param **inPlugValue**: _String_. The value of the plug.

> @param **inAttrDataType**: _String_. The attribute data type.

## getPlug ##

Gets an MPlug from a node.

> @param **inObj**: _String_. Name of object/node.

> @param **inPlugName**: _String_. Name of plug on object/node.

> @return MPlug.

## getPlugValue ##

Gets the value of a given plug.

> @param **inPlug**: _MPlug_. The node plug.

> @return: The value of the passed in node plug.

## setPlugValue ##

Sets the given plug's value to the passed in value.

> @param **inPlug**: _MPlug_. The node plug.

> @param **inValue**: _Type_. Any value of any data type.

## getMetaNodesInScene ##

Finds all nodes of a given type that exist in the active scene.

> @param **inNodeType**: _String_. Meta type to search for in the scene.

> @return: _List of Strings_. All meta nodes in the scene of the given meta type.

## getFrameBitSettings ##

Retrieves the settings for the frame bit.

> @param **inFrameBit**: _String_. Name of frame bit.

> @return: _Dictionary_. All the custom attributes on the frame bit.

## copyBitSettings ##

Copies the bit shape settings (OpenGL stuff) from the second object to the first (in selection order). Assumes two OpenGL bit objects are selected.

## setBitChild ##

Connects the child object's matrix plug to the parent object's targetWorldMatrix array plug. This plug's data is used by the parent's draw() to render the hierarchy arrows.

> @param **inParent**: _String_. Name of the parent object.

> @param **inChild**: _String_. Name of the child object.

## deleteBitChild ##

Disconnects the child bit from it's parent bit.

## getFrameRootAllChildren ##

Gets all descendants of an object.

> @param **inFrameRootName**: _String_. Name of frame root object.

> @return: _List_. Children of object ordered from highest to lowest in the hierarchy.

## cleanParentFullName ##

Removes the first | and the group name from a bit's parent's full path name.

> @param **inBitName**: _String_. Name of the bit to get the parent full path name.

> @return: _String_. Cleaned up parent full path name.

## getAttrTypes ##

Gets the attribute's attr type and data type. These are needed for adding attributes to a node.

> @param **inNode**: _String_. Name of node.

> @param **inAttr**: _String_. Name of attribute.

> @return: _List_. Attribute Type and Attribute Data Type.

## getModuleComponentSettings ##

Gets an object's component settings.

> @param **inModuleBit**: _String_. Name of the bit from which to get the components.

> @return: _List_. List of components.

## getCharactersInScene ##

Retrieve a list of all character components in a scene.

> @return: _List of Strings_

## getModulesInScenes ##

Finds all module roots in the active scene.

## sortModules ##

Sorts module roots by priority.

> @param **inModules**: _Dict_. Dict of modulename:priorty.

> @param **inOrder**: _String_. Ascending or descending.

> @return: _Dict_. Module names sorted by priority

## getModulePriorities ##

Gets all the priorities for a list of module roots.

> @param **inModules**: _List_. List of module roots.

## getModulesByPriority ##

Gets modules in a scene based on their priority.

> @param **inOrder**: _String_. Ascending or descending.

## getModuleName ##

Gets a module name from it's node name.

> @param **inNodeName**: _String_. Name of a module root node.

## getModulePriority ##

Gets the priority number of a module.

> @param **inNodeName**: _String_. Module node name.

## componentCheck ##

Checks a list of components for the passed in component type.

> @param **inComponentList**: _List of Strings_. Names of all the components on a rigging bit.

> @param **inComponentType**: _String_. Name of component class to search for.

> @return: _String_. Name of the component node if found. Otherwise None.

## checkBitForComponent ##

Checks a rigging bit for the passed in component type.

> @param **inBitName**: _String_. Bit name.

> @param **inComponentName**: _String_. Name of the component class.

> @returns: _String_. Component node name. Otherwise None.