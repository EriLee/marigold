import maya.cmds as cmds
import marigold.utility.FrameUtility as FrameUtility
import marigold.utility.NodeUtility as NodeUtility

class BaseComponent( object ):
    '''
    Base class for all meta nodes.
    '''
    nodeType = 'baseComponent'
    
    def __init__( self, node=None ):
        self.node = node
        
    @classmethod
    def createCompNode( cls, inNodeName, **kwargs ):
        '''
        Creates a meta node and adds the required attributes.
        
        @return: The newly created meta node.
        '''
        # Create the node.
        cls.newNode = cmds.createNode( 'network', name=inNodeName )
        #cmds.addAttr( newNode, hidden=False, dataType="string", shortName='classType' )
        #cls.setAttribute( cls(), 'classType', cls.nodeType, inNodeName=newNode )
        
        # Add the required attributes.
        cls.requiredAttributes( cls(), **kwargs )
         
        return cls( cls.newNode )
    
    def name( self ):
        return self.node
    
    @property
    def parentNode( self ):
        if cmds.attributeQuery( 'parentName', node=self.node, exists=True ):
            return NodeUtility.getNodeAttrSource( self.node, 'parentName' )
        
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
            cons[0]: String. Name of the component node.
            cons[1]: String. Name of the class type.
            cons[2]: Bool. Lock setting.
        '''
        cmds.setAttr( '{0}.classType'.format( cons[0] ), cons[1], type='string', lock=cons[2] )
    
    def requiredAttributes( self, *args, **kwargs ):
        FrameUtility.addPlug( self.newNode, 'parentName', 'attributeType', 'message' )
        #cmds.addAttr( newNode, longName='parentName', attributeType='message', storable=True )
        #self.setAttribute( cls(), 'parentName', self.newNode, inNodeName=self.newNode )
        self.setAttribute( 'parentName', self.newNode, self.newNode )
        
        FrameUtility.addPlug( self.newNode, 'classType', 'dataType', 'string' )
        #cls( self.newNode ).classType = [ self.newNode, self.nodeType, True ]
        self.classType = [ self.newNode, self.nodeType, True ]
        
    @classmethod
    def addComponentToObject( cls, inObjectName ):
        '''
        Add the component to the object and link their plugs.
        '''
        print 'addCompToObj: {0}'.format( inObjectName )
        #print 'addCompToObj: {0}'.format( cls.node )
        
    @classmethod
    def buildNode( cls ):
        '''
        Override this classmethod if a component must build assets.
        '''
        print 'building node stuff!'
        
    @classmethod
    def deleteComponentFromObject( cls, inCompNode ):
        '''
        Deletes the selected component from the object. Used in right-click menu
        for components GUI.
        '''
        obj = NodeUtility.getNodeAttrSource( inCompNode, 'parentName' )
        cmds.deleteAttr( '{0}.{1}'.format( obj[0], obj[1] ) )
        cmds.delete( inCompNode )
        cmds.select( obj[0] )
    
    def setComponentAttributeFromQT( self, inPlugName, inQTType, inPlugValue, inNodeName ):
        if inQTType == 'QLineEdit':
            # Get the text from a QLineEdit.
            plugValue = inPlugValue.text()
        self.setAttribute( inPlugName, plugValue, inNodeName )
        
    def setAttribute( self, inPlugName, inPlugValue, inNodeName, inLock=False ):
        #print inPlugName, inPlugValue, inNodeName
        #print type( inPlugValue )
        '''
        if isinstance( inPlugValue, unicode ):
            # This is a unicode string. Likely a node name.
            print 'UNICODE'
            plugValue = inPlugValue
        elif isinstance( inPlugValue, str ):
            print 'STRING'
            plugValue = inPlugValue
        else:
            # This is likely coming from a QT object.
            print 'PASS'
            plugValue = inPlugValue.text()
        '''
        plug = NodeUtility.getPlug( inNodeName, inPlugName )
        NodeUtility.setPlugValue( plug, inPlugValue )
        cmds.setAttr( '{0}.{1}'.format( inNodeName, inPlugName ), lock=inLock )