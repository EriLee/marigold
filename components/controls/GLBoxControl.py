import maya.cmds as cmds
from marigold.components.BaseComponent import BaseComponent
import marigold.utility.NodeUtility as NodeUtility

class GLBoxControlComponent( BaseComponent ):
    nodeType = 'GLBoxControlComponent'
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( GLBoxControlComponent, self ).__init__( node=self.node )
        
    '''
    -basic component setup
    -create gui
    -edit mode
        -create control
        -create gui for editing gl control
            -apply to gl control
            -button for turning on mesh editing
    -save information about gl control on the node
        -should have all the properties of the gl control
    '''
    def requiredAttributes( self ):
        super( GLBoxControlComponent, self ).requiredAttributes()
        NodeUtility.addPlug( self.newNode, 'controlName', 'dataType', 'string' )
        
        # Add the GLBox attributes.
        #kLongName = '-name' SKIPPING
        #kLongPosition = '-position'
        NodeUtility.addPlug( self.newNode, 'position', 'attributeType', '' )
        #kLongLineWidth = '-lineWidth'
        NodeUtility.addPlug( self.newNode, 'lineWidth', 'attributeType', 'float' )
        #kLongRotate = '-rotate'
        NodeUtility.addPlug( self.newNode, 'rotate', '', '' )
        #kLongTransparency = '-alpha'
        NodeUtility.addPlug( self.newNode, 'alpha', 'attributeType', 'float' )
        #kLongBackAlpha = '-backAlpha'
        NodeUtility.addPlug( self.newNode, 'backAlpha', 'attributeType', 'float' )
        #kLongColor = '-color'
        NodeUtility.addPlug( self.newNode, 'color', '', '' )
        #kLongDrawType = '-drawType'
        NodeUtility.addPlug( self.newNode, 'drawType', '', '' )
        #kLongWidth = '-width'
        NodeUtility.addPlug( self.newNode, 'width', 'attributeType', 'float' )
        #kLongHeight = '-height'
        NodeUtility.addPlug( self.newNode, 'height', 'attributeType', 'float' )
        #kLongDepth = '-depth'
        NodeUtility.addPlug( self.newNode, 'depth', 'attributeType', 'float' )
        #kLongTopFrontRight = '-topFrontRight'
        NodeUtility.addPlug( self.newNode, 'topFrontRight', '', '' )
        #kLongTopFrontLeft = '-topFrontLeft'
        NodeUtility.addPlug( self.newNode, 'topFrontLeft', '', '' )
        #kLongTopBackRight = '-topBackRight'
        NodeUtility.addPlug( self.newNode, 'topBackRight', '', '' )
        #kLongTopBackLeft = '-topBackLeft'
        NodeUtility.addPlug( self.newNode, 'topBackLeft', '', '' )
        #kLongBotFrontRight = '-botFrontRight'
        NodeUtility.addPlug( self.newNode, 'botFrontRight', '', '' )
        #kLongBotFrontLeft = '-botFrontLeft'
        NodeUtility.addPlug( self.newNode, 'botFrontLeft', '', '' )
        #kLongBotBackRight = '-botBackRight'
        NodeUtility.addPlug( self.newNode, 'botBackRight', '', '' )
        #kLongBotBackLeft = '-botBackLeft'
        NodeUtility.addPlug( self.newNode, 'botBackLeft', '', '' )
    
    @classmethod
    def buildNode( cls, nodeName ):
        '''
        Builds a GL Box control.
        
        @param nodeName: String. Name of the node.
        '''
        jointName = cmds.getAttr( '{0}.jointName'.format( nodeName ) )
        transReference = NodeUtility.getNodeAttrSource( nodeName, 'parentName' )