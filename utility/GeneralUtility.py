import sys
import maya.OpenMaya as OpenMaya

import shiboken
from PySide import QtGui, QtCore

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
        print depFn.name()
        tempList.append( depFn.name() )
        iter.next()
    return tempList