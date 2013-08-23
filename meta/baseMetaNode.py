'''
*ABOUT*
    This file defines the meta classes used by the various rigging and tools.

*USAGE*
    import marigold.meta.baseMetaNode as baseMetaNode
    
    To create a new node:
        test = baseMetaNode.createMeta( 'test' )
        
    To access class properties:
        sel = cmds.ls( selection=True )
        node = baseMetaNode(sel[0])
        print node.classType
'''

class baseMetaNode( object ):
    '''
    Base class for all meta nodes.
    '''
    nodeType = 'baseMetaNode'
    
    def __init__( self, node ):
        self.node = node
    
    @classmethod
    def createMeta(cls, inNodeName ):
        '''
        Creates a meta node and adds the required attributes.
        
        @return: The newly created meta node.
        '''
        newNode = cmds.createNode( 'network', name=inNodeName )
        cmds.addAttr( newNode, hidden=True, dataType='string', shortName='classType' )
        cls.classType = [ newNode, cls.nodeType ]
        return newNode

    @property
    def classType( self ):
        '''
        @return: String. Class type of the meta node.
        '''
        if cmds.attributeQuery( 'classType', node=self.node, exists=True ):
            return cmds.getAttr( '{0}.classType'.format( self.node ) )
        
    @classType.setter
    def classType( self, cons ):
        '''
        Sets the class type of a meta node.
        
        @param cons: List. List of each variable needed to set the attribute.
            cons[0]: String. Name of the bit.
            cons[1]: String. Name of the class type.
        '''
        cmds.setAttr( '{0}.classType'.format( cons[0] ), cons[1], type='string' )