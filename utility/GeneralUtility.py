import maya.OpenMaya as OpenMaya

def importModule( inModuleName ):
    '''
    Imports a module using a string for the path.
    
    @param inModuleName: String. Full path of the module, separated by "."
    @return: The module!
    '''
    import sys
    __import__( inModuleName )
    return sys.modules[ inModuleName ]

def getMObjectName( inMObject ):
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