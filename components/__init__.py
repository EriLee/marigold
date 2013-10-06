import sys, types
import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility

# IMPORT COMPONENTS
from BaseComponent import BaseComponent
from joints.BasicJoint import BasicJointComponent
from controls.GLBoxControl import GLBoxControlComponent
from controls.CurveControl import CurveControlComponent
from roots.ModuleRoot import ModuleRootComponent
from roots.CharacterRoot import CharacterRootComponent

def str_to_class( field ):
    '''
    Converts a string to a class.
    @param field: String. Name of a class.
    @return: Instance of class.
    '''
    try:
        identifier = getattr(sys.modules[__name__], field)
    except AttributeError:
        raise NameError("%s doesn't exist." % field)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % field)

def findComponent( inObjectName, inComponentType ):
    '''
    Searches a given object for a component that matches the passed in type.
    
    @param inObjectName: String. Name of object.
    @param inComponentType: String. Name of component class.
    '''
    objComponents = getComponents( inObjectName )
    compMatch = None
    for comp in objComponents:
        if comp == inComponentType:
            compMatch = comp
    return compMatch

def getComponents( inObj ):
    '''
    Creates the components GUI.
    '''    
    if inObj is not None:
        components_list = NodeUtility.getFrameBitSettings( inObj )
    else:
        components_list = None
    
    # If the newly selected bit has components then update the UI to show them.
    # Check to see if any of the components are connected to a meta node.
    # We do this check so that we don't create a bunch of UI elements
    # unnecessarily.
    if components_list is not None and metaNodeCheck( inObj, components_list ):            
        # Loop through each component on the bit.
        components_class_list = {}
        for node_name in components_list:
            # Check to see if the component is connected to a meta node.
            metaNode = NodeUtility.getNodeAttrDestination( inObj, node_name )
            if metaNode:
                # It has a meta node.
                # Get the meta node properties. This returns a dict.
                meta_properties = NodeUtility.getFrameBitSettings( metaNode[0] )
                component_class = meta_properties[ 'classType' ]
                # test hack!!!
                components_class_list[ node_name ] = component_class
        return components_class_list
    else:
        return None

def metaNodeCheck( inObj, inComponents ):
    '''
    Checks if the component plug of an object has a meta node connected.
    @param inObj: String. Name of the selected object.
    @param inComponents: List of connected components to the selected object.
    '''    
    for comName in inComponents:
        metaNode = NodeUtility.getNodeAttrDestination( inObj, comName )
        if metaNode:
            return True
    return False

def addComponentToObject( inClassType, **kwargs ):    
    if kwargs.has_key('inObject'):
        targetObj = kwargs['inObject']
        print 'targetObj: {0}'.format( targetObj )
        del kwargs['inObject']
        prevSel = None
    else:
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) is 1:
            targetObj = selList[0]
            prevSel = selList[0]
    
    if targetObj is not None:
        component_class = str_to_class( inClassType )
        newNode = component_class.createCompNode( inClassType, **kwargs )
        
        # Add the component attribute to the object.
        NodeUtility.addPlug( targetObj, newNode.name(), 'attributeType', 'message' )
        nodePlug = '{0}.parentName'.format( newNode.name() )
        objectPlug = '{0}.{1}'.format( targetObj, newNode.name() )
        NodeUtility.connectPlugs( objectPlug, nodePlug )
        if prevSel is not None:
            cmds.select( prevSel )
            
        return newNode
    
def searchModule( inObjectName, inComponentType ):
    '''
    Recursively searches a module for the component that matches the passed in type.
    This is an upward search.
    
    @param inObjectName: String. Name of object.
    @param inComponentType: String. Name of component class.
    @return: List. Name of object with the module meta component and the name of the meta
                    component node.
    '''    
    objSearch = findComponent( inObjectName, inComponentType )
    
    if objSearch is not None:
        return inObjectName, objSearch
    
    if objSearch is None:
        objParent = cmds.listRelatives( inObjectName, parent=True, fullPath=True )
        return searchModule( objParent[0], inComponentType )