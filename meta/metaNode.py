'''
*ABOUT*
    This file defines the meta classes used by the various rigging and tools.

*USAGE*
    import marigold.nodes.metaNode as metaNode
    
    node = MetaNode()
    node = MetaCharacter()
    ...
    
*TODO*
    1. -
    
'''
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

VERSION = 1

#class MetaNode( OpenMayaMPx.MPxNode ):
class MetaNode( object ):
    '''
    Base class for all meta nodes.
    '''
    def __init__( self, inNodeName='metaNode', inNodeMetaType='base' ):
        '''
        @param inNodeName: Name of the new meta node.
        @param inNodeMetaType: Type of meta node to create.
        '''
        self.MFnDepNode = OpenMaya.MFnDependencyNode()
        self.MFnDagNode = OpenMaya.MFnDagNode()
        self.MDGMod = OpenMaya.MDGModifier()
        
        # Set meta node type.
        self.node = cmds.createNode( 'network', name=self.inNodeName )
        cmds.addAttr( longName='metaType', dataType='string' )
        cmds.setAttr( '{0}.metaType'.format( self.node ), self.inNodeMetaType, type='string', lock=True )
        
        # Create meta class attr.
        cmds.addAttr( longName='metaClass', dataType='string' )
        
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
        NodeUtility.connectNodes( self.inNodeName, 'characterGroup', 'character', 'metaParent' )
                
        # Create frame group.
        frameGroup = cmds.createNode( 'transform', name='frame', parent='character' )     
        cmds.addAttr( frameGroup, longName='metaParent', dataType='string' )
        NodeUtility.connectNodes( self.inNodeName, 'frameGroup', 'frame', 'metaParent' )

        # Create rig group.
        rigGroup = cmds.createNode( 'transform', name='rig', parent='character' )
        cmds.addAttr( rigGroup, longName='metaParent', dataType='string' )
        NodeUtility.connectNodes( self.inNodeName, 'rigGroup', 'rig', 'metaParent' )
        
        # Create skeleton group.
        skeletonGroup = cmds.createNode( 'transform', name='skeleton', parent='character' )
        cmds.addAttr( skeletonGroup, longName='metaParent', dataType='string' )
        NodeUtility.connectNodes( self.inNodeName, 'skeletonGroup', 'skeleton', 'metaParent' )

def setupCharacterNodes( inDoModels=True ):
    '''
    @param inDoModels: Bool. Whether to build the groups or not.
    '''
    # Create the base meta node and organization groups for a character.
    MetaCharacter( inDoModels )
