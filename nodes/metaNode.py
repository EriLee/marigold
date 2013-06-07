'''
*ABOUT*
    This file defines the meta classes used by the various rigging and tools.

*USAGE*
    import adam.nodes.metaNode as metaNode
    
    node = MetaNode()
    node = MetaCharacter()
    ...
    
*TODO*
    1. -
    
'''
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

VERSION = 1

#class MetaNode( OpenMayaMPx.MPxNode ):
class MetaNode( object ):
    '''
    Base class for all meta nodes.
    '''
    def __init__( self, inNodeName=None, inNodeMetaType=None ):
        '''
        @param inNodeName: Name of the new meta node.
        @param inNodeMetaType: Type of meta node to create.
        '''
        self.MFnDepNode = OpenMaya.MFnDependencyNode()
        self.MFnDagNode = OpenMaya.MFnDagNode()
        self.MDGMod = OpenMaya.MDGModifier()
        
        if not inNodeName:
            self.inNodeName = 'metaNode'
        if not inNodeMetaType:
            self.inNodeMetaType = 'base'
        
        # Set meta node type.
        self.node = cmds.createNode( 'network', name=self.inNodeName )
        cmds.addAttr( longName='metaType', dataType='string' )
        cmds.setAttr( '{0}.metaType'.format( self.node ), self.inNodeMetaType, type='string', lock=True )
        
        # Parent Attr
        cmds.addAttr( longName='metaParent', hidden=False, attributeType='message' )
        
        # Create attributes unique to the meta base node.
        self.createAttrs()
        
    def createAttrs( self ):
        cmds.addAttr( longName='version', attributeType='double' )
        cmds.setAttr( '{0}.version'.format( self.node ), VERSION, lock=True )

class MetaCharacter( MetaNode ):
    '''
    Creates a node of the MetaNode type. This node holds information about the character
    and is the top most meta node in a character hierarchy.
    '''
    #def __init__( self, *args, **kws ):
    def __init__( self, doModel=True ):
        self.inNodeMetaType = 'character'
        self.inNodeName = 'MetaCharacter'        
        super( MetaCharacter, self ).__init__( self.inNodeName, self.inNodeMetaType )
        if doModel:
            self.makeGroups()
    
    def createAttrs( self ):
        cmds.addAttr( longName='characterGroup', dataType='string' )
        cmds.addAttr( longName='frameGroup', dataType='string' )
        cmds.addAttr( longName='rigGroup', dataType='string' )
        cmds.addAttr( longName='skeletonGroup', dataType='string' )

    def makeGroups( self ):
        # Create character group.
        characterGroup = cmds.createNode( 'transform', name='character' )
        cmds.addAttr( characterGroup, longName='metaParent', dataType='string')
        connectNodes( self.inNodeName, 'characterGroup', 'character', 'metaParent' )
                
        # Create frame group.
        frameGroup = cmds.createNode( 'transform', name='frame', parent='character' )     
        cmds.addAttr( frameGroup, longName='metaParent', dataType='string' )
        connectNodes( self.inNodeName, 'frameGroup', 'frame', 'metaParent' )

        # Create rig group.
        rigGroup = cmds.createNode( 'transform', name='rig', parent='character' )
        cmds.addAttr( rigGroup, longName='metaParent', dataType='string' )
        connectNodes( self.inNodeName, 'rigGroup', 'rig', 'metaParent' )
        
        # Create skeleton group.
        skeletonGroup = cmds.createNode( 'transform', name='skeleton', parent='character' )
        cmds.addAttr( skeletonGroup, longName='metaParent', dataType='string' )
        connectNodes( self.inNodeName, 'skeletonGroup', 'skeleton', 'metaParent' )

class MetaMapper( MetaNode ):
    '''
    Creates a node of the MetaNode type. This node holds information about the character
    skeleton. Specifically it maps joints and joint chains to modules.
    '''
    def __init__( self ):
        self.inNodeMetaType = 'mapper'
        self.inNodeName = 'MetaMapper'        
        super( MetaMapper, self ).__init__( self.inNodeName, self.inNodeMetaType )
        
    def addMap( self ):
        pass
    
    def removeMap( self ):
        pass

# UTILITY
def getDependNode( inObj ):
    '''
    @param inObj: String.
    @return MObject.
    '''
    selList = OpenMaya.MSelectionList()
    selList.add( inObj )
    mObj = OpenMaya.MObject()
    selList.getDependNode( 0, mObj )
    return mObj

def getPlug( inObj, inPlugName ):
    '''
    @param inObj: Depend Node.
    @param inPlugName: String.
    @return MPlug.
    '''
    mObj = getDependNode( inObj )
    #print mObj.apiTypeStr()
    depFn = OpenMaya.MFnDependencyNode()
    depFn.setObject( mObj )
    plug = depFn.findPlug( inPlugName )
    return plug#.node()

def connectNodes( inParentObj, inParentPlug, inChildObj, inChildPlug ):
    '''
    @param inParentObj: String. Name of parent node.
    @param inParentPlug: String. Name of plug on parent node.
    @param inChildObj: String. Name of child node.
    @param inChildPlug: String. Name of plug on child node.
    '''
    parentPlug = getPlug( inParentObj, inParentPlug )
    childPlug = getPlug( inChildObj, inChildPlug )
    MDGMod = OpenMaya.MDGModifier()
    MDGMod.connect( childPlug, parentPlug )
    MDGMod.doIt()

def setupCharacterNodes( inDoModels=True ):
    '''
    @param inDoModels: Bool. Whether to build the groups or not.
    '''
    # Create the base meta node and organization groups for a character.
    MetaCharacter( inDoModels )

setupCharacterNodes( True )