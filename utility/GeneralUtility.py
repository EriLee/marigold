import sys
import maya.OpenMaya as OpenMaya
import maya.cmds as cmds

import shiboken
from PySide import QtGui, QtCore

import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.NodeUtility as NodeUtility

def wrapinstance(ptr, base=None):
    """
    Utility to convert a pointer to a Qt class instance (PySide/PyQt compatible)

    :param ptr: Pointer to QObject in memory
    :type ptr: long or Swig instance
    :param base: (Optional) Base class to wrap with (Defaults to QObject, which should handle anything)
    :type base: QtGui.QWidget
    :return: QWidget or subclass instance
    :rtype: QtGui.QWidget
    """
    if ptr is None:
        return None
    ptr = long(ptr) #Ensure type
    if globals().has_key('shiboken'):
        if base is None:
            qObj = shiboken.wrapInstance(long(ptr), QtCore.QObject)
            metaObj = qObj.metaObject()
            cls = metaObj.className()
            superCls = metaObj.superClass().className()
            if hasattr(QtGui, cls):
                base = getattr(QtGui, cls)
            elif hasattr(QtGui, superCls):
                base = getattr(QtGui, superCls)
            else:
                base = QtGui.QWidget
        return shiboken.wrapInstance(long(ptr), base)
    elif globals().has_key('sip'):
        base = QtCore.QObject
        return sip.wrapinstance(long(ptr), base)
    else:
        return None
    
def importModule( inModuleName ):
    '''
    Imports a module using a string for the path.
    
    @param inModuleName: String. Full path of the module, separated by "."
    @return: The module!
    '''
    __import__( inModuleName )
    return sys.modules[ inModuleName ]

def getMObjectName( inMObject ):
    '''
    Returns the name of an MObject.
    @param inMObject: MObject.
    @return: String. Name of MObject.
    '''
    depFn = OpenMaya.MFnDependencyNode( inMObject )
    return depFn.name()
    
def searchSceneByName( inSearchString=None ):
    '''
    Finds all objects with inSearchString in their name. Can use wildcard (*) in
    search.
    
    Example: Searching frame_root* will return a list of all frame root objects.
    
    @param inSearchString: String. Name to search for. 
    @return: A list of frame root names in string format.
    '''
    # Build a selection list of all frame roots in the scene.
    selList = OpenMaya.MSelectionList()
    
    try:
        OpenMaya.MGlobal.getSelectionListByName( inSearchString, selList )
    except:
        print '{0} doesn\'t exist'.format( inSearchString )
        return
    
    # Get an iterable list of the frame roots.
    iter = OpenMaya.MItSelectionList( selList )
    depFn = OpenMaya.MFnDependencyNode()
    mObj = OpenMaya.MObject()
    
    # Loop through them.
    tempList = []
    while not iter.isDone():
        iter.getDependNode( mObj )
        depFn.setObject( mObj )
        #print depFn.name()
        tempList.append( depFn.name() )
        iter.next()
    return tempList

def setUserColor( inObjName, userColor=None ):
    '''
    @param inObjName: String. Name of object.
    @param userColor: Int. 1-8. User defined color to use.
    '''
    if userColor is not None:
        cmds.color( inObjName, userDefined=userColor )
    else:
        cmds.color( inObjName )
        
def convertRGB( inRGB, inType=1 ):
    '''
    @param inRGB: List. Three values representing RGB.
    @param inType: Int. 1 is 0-1 to 0-255. 2 is 0-255 to 0-1.
    @return: List. New RGB values.
    '''
    tempList = []
    if inType == 1:
        # Convert 0-1 to 0-255
        for item in inRGB:
            tempList.append( item * 255 )
    elif inType == 2:
        # Convert 0-255 to 0-1
        for item in inRGB:
            tempList.append( item / 255 )
    return tempList

def getUserDefinedColors( inType=1 ):
    '''
    @param inType: Int. 1 is RGB. 2 is HSV.
    @return: List. User defined colors 1-8.
    '''
    tempList = []
    for color in xrange( 1, 9 ):
        userString = 'userDefined{0}'.format( color )
        if inType == 1:         
            colorSetting = cmds.displayRGBColor( userString, query=True )
        elif inType == 2:
            colorSetting = cmds.displayRGBColor( userString, query=True, hueSaturationValue=True )
        tempList.append( colorSetting )
    return tempList

def createSpacer( inBitName, inGroupName='newGroup', inTargetObject=None, inDoParent=False, inPrefix=None ):
    '''
    Creates an empty group. Optionally, the group's transforms can be matched to
    another object.
    
    @param inGroupName: String. Name to give the new group.
    @param inTargetObject: String. Name of object to match the group's transforms
    to.
    @return: The newly created group.
    '''
    # Create empty group.
    if inPrefix is not None:
        groupName = inPrefix+'_'+inGroupName
    else:
        groupName = inGroupName
        
    newGroup = cmds.group( em=True, name=groupName )

    # Set its transforms.
    if inTargetObject is not None:
        # Get target objects matrix.
        targetMatrix = TransformUtility.getMatrix( inTargetObject, 'worldMatrix' )
        
        # Get groups transform.
        MFnTrans = OpenMaya.MFnTransform()
        groupDagPath = NodeUtility.getDagPath( newGroup )
        MFnTrans.setObject( groupDagPath )
        
        # Apply the targets translation to the group.
        targetTranslation = TransformUtility.getMatrixTranslation( targetMatrix, OpenMaya.MSpace.kWorld )
        MFnTrans.setTranslation( targetTranslation, OpenMaya.MSpace.kWorld )
        
        # Apply the targets rotation to the group.         
        targetRotation = TransformUtility.getMatrixRotation( targetMatrix, 'quat' )
        MFnTrans.setRotation( targetRotation, OpenMaya.MSpace.kWorld )
        
        # Parent the spacer.
        if inDoParent:
            parent = cmds.listRelatives( inBitName, parent=True )
            if NodeUtility.attributeCheck( parent[0], 'controlName' ):
                parentControl = NodeUtility.getFrameBitSettings( parent[0] )[ 'controlName' ]
                cmds.parent( newGroup, parentControl, absolute=True )
                
    return newGroup