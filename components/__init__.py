import sys, types
import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.FrameUtility as FrameUtility

# IMPORT COMPONENTS
#from BaseComponent import BaseComponent
from joints.BasicJoint import BasicJointComponent
from controls.GLBoxControl import GLBoxControlComponent
from controls.CurveControl import CurveControlComponent

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

def getComponents( inObj ):
    '''
    Creates the components GUI.
    '''
    if inObj is not None:
        components_list = FrameUtility.getFrameBitSettings( inObj )
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
                meta_properties = FrameUtility.getFrameBitSettings( metaNode[0] )
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
    selList = cmds.ls( selection=True, long=True )
    if len( selList ) is 1:
        prevSel = selList[0]
        component_class = str_to_class( inClassType )
        newNode = component_class.createCompNode( inClassType, **kwargs )
        
        # Add the component attribute to the object.
        FrameUtility.addPlug( selList[0], newNode.name(), 'attributeType', 'message' )
        nodePlug = '{0}.parentName'.format( newNode.name() )
        objectPlug = '{0}.{1}'.format( selList[0], newNode.name() )
        NodeUtility.connectPlugs( objectPlug, nodePlug )
        cmds.select( prevSel )