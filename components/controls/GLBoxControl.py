import maya.cmds as cmds
from marigold.components.BaseComponent import BaseComponent
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.FrameUtility as FrameUtility

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
        FrameUtility.addPlug( self.newNode, 'controlName', 'dataType', 'string' )
        
        # Add the GLBox attributes.
        #kLongName = '-name' SKIPPING
        #kLongPosition = '-position'
        FrameUtility.addPlug( self.newNode, 'position', 'attributeType', '' )
        #kLongLineWidth = '-lineWidth'
        FrameUtility.addPlug( self.newNode, 'lineWidth', 'attributeType', 'float' )
        #kLongRotate = '-rotate'
        FrameUtility.addPlug( self.newNode, 'rotate', '', '' )
        #kLongTransparency = '-alpha'
        FrameUtility.addPlug( self.newNode, 'alpha', 'attributeType', 'float' )
        #kLongBackAlpha = '-backAlpha'
        FrameUtility.addPlug( self.newNode, 'backAlpha', 'attributeType', 'float' )
        #kLongColor = '-color'
        FrameUtility.addPlug( self.newNode, 'color', '', '' )
        #kLongDrawType = '-drawType'
        FrameUtility.addPlug( self.newNode, 'drawType', '', '' )
        #kLongWidth = '-width'
        FrameUtility.addPlug( self.newNode, 'width', 'attributeType', 'float' )
        #kLongHeight = '-height'
        FrameUtility.addPlug( self.newNode, 'height', 'attributeType', 'float' )
        #kLongDepth = '-depth'
        FrameUtility.addPlug( self.newNode, 'depth', 'attributeType', 'float' )
        #kLongTopFrontRight = '-topFrontRight'
        FrameUtility.addPlug( self.newNode, 'topFrontRight', '', '' )
        #kLongTopFrontLeft = '-topFrontLeft'
        FrameUtility.addPlug( self.newNode, 'topFrontLeft', '', '' )
        #kLongTopBackRight = '-topBackRight'
        FrameUtility.addPlug( self.newNode, 'topBackRight', '', '' )
        #kLongTopBackLeft = '-topBackLeft'
        FrameUtility.addPlug( self.newNode, 'topBackLeft', '', '' )
        #kLongBotFrontRight = '-botFrontRight'
        FrameUtility.addPlug( self.newNode, 'botFrontRight', '', '' )
        #kLongBotFrontLeft = '-botFrontLeft'
        FrameUtility.addPlug( self.newNode, 'botFrontLeft', '', '' )
        #kLongBotBackRight = '-botBackRight'
        FrameUtility.addPlug( self.newNode, 'botBackRight', '', '' )
        #kLongBotBackLeft = '-botBackLeft'
        FrameUtility.addPlug( self.newNode, 'botBackLeft', '', '' )
    
    @classmethod
    def buildNode( cls, nodeName ):
        '''
        Builds a GL Box control.
        
        @param nodeName: String. Name of the node.
        '''
        jointName = cmds.getAttr( '{0}.jointName'.format( nodeName ) )
        transReference = NodeUtility.getNodeAttrSource( nodeName, 'parentName' )