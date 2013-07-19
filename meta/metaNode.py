'''
*ABOUT*
    This file defines the meta classes used by the various rigging and tools.

*USAGE*
    import marigold.meta.metaNode as metaNode
    
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
        
        self.metaType = inNodeMetaType
        
        # Create the meta node.
        self.node = cmds.createNode( 'network', name=inNodeName )
        
        # Create the attributes.
        self.createAttrs()
        
    def createAttrs( self ):
        # Generic attributes contained by all meta nodes.
        # metaType: Type of meta node.
        cmds.addAttr( longName='metaType', dataType='string' )
        cmds.setAttr( '{0}.metaType'.format( self.node ), self.metaType, type='string', lock=True )
        
        # metaClass: This is the name of the custom class to call when creating
        # anything related to this node and it's children.
        cmds.addAttr( longName='metaClass', dataType='string' )
        
        # Version: What version of the meta system was used to create the network.
        cmds.addAttr( longName='version', attributeType='double' )
        cmds.setAttr( '{0}.version'.format( self.node ), VERSION, lock=True )
        
        if self.metaType == 'character':
            # Attributes for the metaRoot node. This is the top most meta node in
            # the network.
            cmds.addAttr( longName='metaChildren', dataType='string' )
            
        elif self.metaType == 'frameModule':
            # rootBit: The frame root of the frame module associated with the meta
            # node.
            cmds.addAttr( longName='rootBit', dataType='string' )
            
        if self.metaType is not 'character':
            # metaParent: Parent of this meta node in the network. Should point
            # meta node. 
            cmds.addAttr( longName='metaParent', hidden=False, attributeType='message' )

class MetaCharacter( MetaNode ):
    '''
    Creates a node of the MetaNode type. This node holds information about the character
    and is the top most meta node in a character hierarchy.
    '''
    #def __init__( self, *args, **kws ):
    def __init__( self, doModel=True ):
        self.inNodeMetaType = 'character'
        self.inNodeName = 'metaCharacter'  
        super( MetaCharacter, self ).__init__( self.inNodeName, self.inNodeMetaType )
        if doModel:
            self.makeGroups()
    
    def createAttrs( self ):
        super( MetaCharacter, self ).createAttrs()
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
