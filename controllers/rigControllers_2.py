'''
Plug-in: Rig Controller Primitive
Author: Austin Baker
Date Started: May 2013

*ABOUT*
    This plug-in creates a primitive rig controller and is an extension
    of the MPxLocatorNode. It draws an OpenGL cube whose shape can be tweaked to fit
    most rigging requirements.
    
    name: Name of the shape node.
    position: Offset position amount of the shape node. Takes three floats.
    lineWidth: Width of the wireframe drawing. Takes an int.
    rotate: Offset rotation of the OpenGL drawing. Takes three floats.
    alpha: Transparency of the OpenGL drawing. Takes a float.
    backAlpha: Changes the brightness of the wireframe drawing. Takes a float.
    color: Sets the color of the controller when not selected.
    drawType: OpenGl drawing override. Can force the drawing into wireframe or shaded regardless
            of viewport setting. Takes an int.
    width: Width of cube on the X. Takes a float.
    height: Width of cube on the Y. Takes a float.
    depth: Width of cube on the Z. Takes a float.
    opTopFrontRight: Offset of the point. Takes three floats.
    opTopFrontLeft: Offset of the point. Takes three floats.
    opTopBackRight: Offset of the point. Takes three floats.
    opTopBackLeft: Offset of the point. Takes three floats.
    opBotFrontRight: Offset of the point. Takes three floats.
    opBotFrontLeft: Offset of the point. Takes three floats.
    opBotBackRight: Offset of the point. Takes three floats.
    opBotBackLeft: Offset of the point. Takes three floats.    

*SAMPLE USAGE*
    Create the node directly:
        import maya.cmds as cmds
        cmds.loadPlugin( 'constrainObjectAim.py' )
        cmds.createNode( 'ControlBox' )
    Create the node through the command:
        cmds.rigController( name='bob',
                            position=( 10.0,2.0,6.0 ),
                            lineWidth=2,
                            rotate=( 10,30,50 ),
                            alpha=0.3,
                            backAlpha=0.2,
                            color=( 0.1,1.0,0.5 ),
                            drawType=2,
                            width=10,
                            height=5,
                            depth=2,
                            opTopFrontRight=( 1.0, -2.0, 0.2 ),
                            opTopFrontLeft=( 1.0, -2.0, 0.2 ),
                            opTopBackRight=( 1.0, -2.0, 0.2 ),
                            opTopBackLeft=( 1.0, -2.0, 0.2 ),
                            opBotFrontRight=( 1.0, -2.0, 0.2 ),
                            opBotFrontLeft=( 1.0, -2.0, 0.2 ),
                            opBotBackRight=( 1.0, -2.0, 0.2 ),
                            opBotBackLeft=( 1.0, -2.0, 0.2 ) )
'''
# ==
# GLOBALS
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI
import adam.utility.NodeUtility as NodeUtility
import adam.utility.TransformUtility as TransformUtility

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

# Node name.
nodeName = 'ControlBox'
nodeID = OpenMaya.MTypeId( 0x1000B )
manipNodeName = 'ControlBoxManip'
manipNodeID = OpenMaya.MTypeId( 0x1000C )

# Command flags.
cmdName = 'rigController'
kShortName = '-n'
kLongName = '-name'
kShortPosition = '-pos'
kLongPosition = '-position'
kShortLineWidth = '-lw'
kLongLineWidth = '-lineWidth'
kShortRotate = '-rot'
kLongRotate = '-rotate'
kShortTransparency = '-a'
kLongTransparency = '-alpha'
kShortBackAlpha = '-ba'
kLongBackAlpha = '-backAlpha'
kShortColor = '-cl'
kLongColor = '-color'
kShortDrawType = '-dt'
kLongDrawType = '-drawType'
kShortWidth = '-w'
kLongWidth = '-width'
kShortHeight = '-h'
kLongHeight = '-height'
kShortDepth = '-d'
kLongDepth = '-depth'
kShortTopFrontRight = '-tfr'
kLongTopFrontRight = '-topFrontRight'
kShortTopFrontLeft = '-tfl'
kLongTopFrontLeft = '-topFrontLeft'
kShortTopBackRight = '-tbr'
kLongTopBackRight = '-topBackRight'
kShortTopBackLeft = '-tbl'
kLongTopBackLeft = '-topBackLeft'
kShortBotFrontRight = '-bfr'
kLongBotFrontRight = '-botFrontRight'
kShortBotFrontLeft = '-bfl'
kLongBotFrontLeft = '-botFrontLeft'
kShortBotBackRight = '-bbr'
kLongBotBackRight = '-botBackRight'
kShortBotBackLeft = '-bbl'
kLongBotBackLeft = '-botBackLeft'

def statusColor( r, g, b, a, status ):
    # Change color of the controller based on it's active state.
    if status == OpenMayaUI.M3dView.kLead:
        glFT.glColor4f( 0, 1, 1, a )
    elif status == OpenMayaUI.M3dView.kActive:
        glFT.glColor4f( 0, 1, 0, a )
    elif status == OpenMayaUI.M3dView.kActiveAffected:
        glFT.glColor4f( r, g, b, a )
    elif status == OpenMayaUI.M3dView.kDormant:
        glFT.glColor4f( r, g, b, a )
    elif status == OpenMayaUI.M3dView.kHilite:
        glFT.glColor4f( r, g, b, a )

# ==
# NODE
class ControlBox( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        # Declare the min and max points for the bounding box. The math for the points
        # is done in draw().
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        
    def compute( self, plug, dataBlock ):
        return OpenMaya.kUnknownParameter

    def draw( self, view, path, style, status ):
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        trX= OpenMaya.MPlug( self.thisMObject(), self.localPositionX ).asFloat()
        trY= OpenMaya.MPlug( self.thisMObject(), self.localPositionY ).asFloat()
        trZ= OpenMaya.MPlug( self.thisMObject(), self.localPositionZ ).asFloat()
        lw = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'lineWidth' ) ).asInt()
        rt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'rotate' ) )
        a = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'transparency' ) ).asFloat()
        ba = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'backAlpha' ) ).asFloat()
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'color' ))
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        width = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'width' ) ).asFloat()#X
        height = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'height' ) ).asFloat()#Y
        depth = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'depth' ) ).asFloat()#Z
        rotation = NodeUtility.getPlugValue( rt )
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Get the point attributes used to offset each corner of the cube.
        tfr = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'topFrontRight' ) )
        tfl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'topFrontLeft' ) )
        tbr = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'topBackRight' ) )
        tbl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'topBackLeft' ) )
        bfr = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'botFrontRight' ) )
        bfl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'botFrontLeft' ) )
        bbr = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'botBackRight' ) )
        bbl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'botBackLeft' ) )
        # Get the values of each point plug.
        vTFR = NodeUtility.getPlugValue( tfr )
        vTFL = NodeUtility.getPlugValue( tfl )
        vTBR = NodeUtility.getPlugValue( tbr )
        vTBL = NodeUtility.getPlugValue( tbl )
        vBFR = NodeUtility.getPlugValue( bfr )
        vBFL = NodeUtility.getPlugValue( bfl )
        vBBR = NodeUtility.getPlugValue( bbr )
        vBBL = NodeUtility.getPlugValue( bbl )
        
        # Do the maths! For each point we factor in the width/height/depth, the point tweak value and the offset object offset position.
        drawPoints = []
        drawPoints.append( [ ( width/2 + vBFL[0] ) + trX, ( -height/2+vBFL[1] ) + trY, ( depth/2+vBFL[2] ) + trZ ] ) #bottomFrontLeft
        drawPoints.append( [ ( -width/2 + vBFR[0] ) + trX, ( -height/2+vBFR[1] ) + trY, ( depth/2+vBFR[2] ) + trZ ] ) #bottomFrontRight
        drawPoints.append( [ ( width/2+vBBL[0] ) + trX, ( -height/2+vBBL[1] ) + trY, ( -depth/2+vBBL[2] ) + trZ ] ) #bottomBackLeft
        drawPoints.append( [ ( -width/2+vBBR[0] ) + trX, ( -height/2+vBBR[1] ) + trY, ( -depth/2+vBBR[2] ) + trZ ] ) #bottomBackRight
        drawPoints.append( [ ( width/2 + vTFL[0] ) + trX, ( height/2+vTFL[1] ) + trY, ( depth/2+vTFL[2] ) + trZ ] ) #topFrontLeft
        drawPoints.append( [ ( -width/2 + vTFR[0] ) + trX, ( height/2+vTFR[1] ) + trY, ( depth/2+vTFR[2] ) + trZ ] ) #topFrontRight
        drawPoints.append( [ ( width/2+vTBL[0] ) + trX, ( height/2+vTBL[1] ) + trY, ( -depth/2+vTBL[2] ) + trZ ] ) #topBackLeft
        drawPoints.append( [ ( -width/2+vTBR[0] ) + trX, ( height/2+vTBR[1] ) + trY, ( -depth/2+vTBR[2] ) + trZ ] ) #topBackRight
        
        # Calculate bounding box min and max points. Basically bbp1 is the bottom or negative point
        # while bbp2 is the top or positive point.
        X, Y, Z = ( [] for i in range( 3 ) )
        for point in drawPoints:
            X.append( point[0] )
            Y.append( point[1] )
            Z.append( point[2] )        
        self.bbp1 = OpenMaya.MPoint( min( X ), min( Y ), min( Z ) )
        self.bbp2 = OpenMaya.MPoint( max( X ), max( Y ), max( Z ) )
        
        def drawObject( self ):
            # Draw the box
            glFT.glBegin( OpenMayaRender.MGL_QUADS )
            # Front. Normal faces +Z.
            glFT.glVertex3f( drawPoints[1][0], drawPoints[1][1], drawPoints[1][2] )#bottom right
            glFT.glVertex3f( drawPoints[0][0], drawPoints[0][1], drawPoints[0][2] )#bottom left
            glFT.glVertex3f( drawPoints[4][0], drawPoints[4][1], drawPoints[4][2] )#top left
            glFT.glVertex3f( drawPoints[5][0], drawPoints[5][1], drawPoints[5][2] )#top right
            # Back. Normal faces -Z.
            glFT.glVertex3f( drawPoints[3][0], drawPoints[3][1], drawPoints[3][2] )#bottom right
            glFT.glVertex3f( drawPoints[7][0], drawPoints[7][1], drawPoints[7][2] )#top right
            glFT.glVertex3f( drawPoints[6][0], drawPoints[6][1], drawPoints[6][2] )#top left
            glFT.glVertex3f( drawPoints[2][0], drawPoints[2][1], drawPoints[2][2] )#bottom left
            # Right. Normal faces -X.
            glFT.glVertex3f( drawPoints[3][0], drawPoints[3][1], drawPoints[3][2] )#bottom back
            glFT.glVertex3f( drawPoints[1][0], drawPoints[1][1], drawPoints[1][2] )#bottom front
            glFT.glVertex3f( drawPoints[5][0], drawPoints[5][1], drawPoints[5][2] )#top front
            glFT.glVertex3f( drawPoints[7][0], drawPoints[7][1], drawPoints[7][2] )#top back
            # Left. Normal faces +X.
            glFT.glVertex3f( drawPoints[0][0], drawPoints[0][1], drawPoints[0][2] )#bottom front
            glFT.glVertex3f( drawPoints[2][0], drawPoints[2][1], drawPoints[2][2] )#bottom back
            glFT.glVertex3f( drawPoints[6][0], drawPoints[6][1], drawPoints[6][2] )#top back
            glFT.glVertex3f( drawPoints[4][0], drawPoints[4][1], drawPoints[4][2] )#top front
            # Top. Normal faces +Y.
            glFT.glVertex3f( drawPoints[5][0], drawPoints[5][1], drawPoints[5][2] )#front right
            glFT.glVertex3f( drawPoints[4][0], drawPoints[4][1], drawPoints[4][2] )#front left
            glFT.glVertex3f( drawPoints[6][0], drawPoints[6][1], drawPoints[6][2] )#back left
            glFT.glVertex3f( drawPoints[7][0], drawPoints[7][1], drawPoints[7][2] )#back right
            # Bottom. Normal faces -Y.
            glFT.glVertex3f( drawPoints[3][0], drawPoints[3][1], drawPoints[3][2] )#back right
            glFT.glVertex3f( drawPoints[2][0], drawPoints[2][1], drawPoints[2][2] )#back left
            glFT.glVertex3f( drawPoints[0][0], drawPoints[0][1], drawPoints[0][2] )#front left
            glFT.glVertex3f( drawPoints[1][0], drawPoints[1][1], drawPoints[1][2] )#front right
            glFT.glEnd()

        def drawShaded(self):
            glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glFrontFace( OpenMayaRender.MGL_CCW )
            drawObject( self )
            glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glPolygonMode(OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE)
            drawObject( self )
            glFT.glCullFace( OpenMayaRender.MGL_BACK )

        def drawWireframe(self):
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
        
        def drawText( self, string, vec ):
                halfV = vec * 0.5            
                # Draw the text string.
                glFT.glColor4f( 1.0, 0.2, 0.0, 1.0 )
                textPoint = OpenMaya.MPoint( halfV.x, halfV.y, halfV.z)
                view.drawText( string, textPoint )

        view.beginGL()
        glFT.glPushMatrix()
        
        # Change the rotation of the controller.
        glFT.glRotatef( rotation[ 0 ], 1.0,0.0,0.0 )
        glFT.glRotatef( rotation[ 1 ], 0.0,1.0,0.0 )
        glFT.glRotatef( rotation[ 2 ], 0.0,0.0,1.0 )
        
        glFT.glPushAttrib( OpenMayaRender.MGL_ALL_ATTRIB_BITS )
        
        # Handle switching between wireframe and shaded.
        f = drawShaded
        if style not in [ OpenMayaUI.M3dView.kFlatShaded, OpenMayaUI.M3dView.kGouraudShaded ]: f = drawWireframe
        if dt == 1: f = drawShaded
        elif dt == 0: f = drawWireframe
        
        glFT.glClearDepth( 1.0 )
        glFT.glEnable( OpenMayaRender.MGL_BLEND )
        glFT.glEnable( OpenMayaRender.MGL_DEPTH_TEST )
        glFT.glDepthFunc( OpenMayaRender.MGL_LEQUAL )
        glFT.glShadeModel( OpenMayaRender.MGL_SMOOTH )
        glFT.glBlendFunc( OpenMayaRender.MGL_SRC_ALPHA, OpenMayaRender.MGL_ONE_MINUS_SRC_ALPHA )
        glFT.glDepthMask( OpenMayaRender.MGL_FALSE )
        
        # Sets the color of the polygons.
        statusColor( r, g, b, a, status )
        glFT.glLineWidth( lw )
        f( self )
        # Sets the color of the wireframes.
        statusColor( r, g, b, ba, status )
        f( self )
        
        glFT.glPopAttrib()
        glFT.glPopMatrix()
        view.endGL()
        
    def boundingBox( self ):
        # Creates a bounding box for the controller.
        corner1 = OpenMaya.MPoint( self.bbp1.x, self.bbp1.y, self.bbp1.z )
        corner2 = OpenMaya.MPoint( self.bbp2.x, self.bbp2.y, self.bbp2.z )
        bbox = OpenMaya.MBoundingBox( corner1, corner2 )
        return bbox

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( ControlBox() )
  
def nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    enumAttr = OpenMaya.MFnEnumAttribute()

    ControlBox.aColor = nAttr.createColor( 'color', 'color' )
    nAttr.setDefault( 0.1, 0.1, 0.8 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0, 0, 0 )
    nAttr.setMax( 1, 1, 1 )
    
    ControlBox.aRotate = nAttr.createPoint( 'rotate', 'rotate' )
    nAttr.setDefault( 0.0, 0.0, 0.0 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
  
    ControlBox.aTransparency = nAttr.create( 'transparency', 'transparency', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 0.5 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 1 )
  
    ControlBox.aBackAlpha = nAttr.create( 'backAlpha', 'backAlpha', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 0.2 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 1 )
  
    ControlBox.aLineWidth = nAttr.create( 'lineWidth', 'lineWidth', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 0 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1)
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 10 )
    
    ControlBox.aWidth = nAttr.create( 'width', 'width', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(6.0)
    nAttr.setMin(2)
    nAttr.setKeyable(1)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
  
    ControlBox.aHeight = nAttr.create( 'height', 'height', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(12.0)
    nAttr.setMin(2)
    nAttr.setKeyable(1)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
  
    ControlBox.aDepth = nAttr.create( 'depth', 'depth', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(2.0)
    nAttr.setKeyable(1)
    nAttr.setReadable(1)
    nAttr.setWritable(1)
    nAttr.setStorable(1)
    
    ControlBox.aDrawType = enumAttr.create( 'drawType', 'drawType' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )

    ControlBox.aTopAX = nAttr.create( 'tfrX', 'tfrX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopAY = nAttr.create( 'tfrY', 'tfrY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopAZ = nAttr.create( 'tfrZ', 'tfrZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopA = nAttr.create( 'topFrontRight', 'topFrontRight', ControlBox.aTopAX, ControlBox.aTopAY, ControlBox.aTopAZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aTopBX = nAttr.create( 'tflX', 'tflX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopBY = nAttr.create( 'tflY', 'tflY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopBZ = nAttr.create( 'tflZ', 'tflZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopB = nAttr.create( 'topFrontLeft', 'topFrontLeft', ControlBox.aTopBX, ControlBox.aTopBY, ControlBox.aTopBZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aTopCX = nAttr.create( 'tbrX', 'tbrX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopCY = nAttr.create( 'tbrY', 'tbrY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopCZ = nAttr.create( 'tbrZ', 'tbrZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopC = nAttr.create( 'topBackRight', 'topBackRight', ControlBox.aTopCX, ControlBox.aTopCY, ControlBox.aTopCZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aTopDX = nAttr.create( 'tblX', 'tblX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopDY = nAttr.create( 'tblY', 'tblY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopDZ = nAttr.create( 'tblZ', 'tblZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aTopD = nAttr.create( 'topBackLeft', 'topBackLeft', ControlBox.aTopDX, ControlBox.aTopDY, ControlBox.aTopDZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aBotAX = nAttr.create( 'bfrX', 'bfrX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotAY = nAttr.create( 'bfrY', 'bfrY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotAZ = nAttr.create( 'bfrZ', 'bfrZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotA = nAttr.create( 'botFrontRight', 'botFrontRight', ControlBox.aBotAX, ControlBox.aBotAY, ControlBox.aBotAZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aBotBX = nAttr.create( 'bflX', 'bflX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotBY = nAttr.create( 'bflY', 'bflY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotBZ = nAttr.create( 'bflZ', 'bflZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotB = nAttr.create( 'botFrontLeft', 'botFrontLeft', ControlBox.aBotBX, ControlBox.aBotBY, ControlBox.aBotBZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aBotCX = nAttr.create( 'bbrX', 'bbrX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotCY = nAttr.create( 'bbrY', 'bbrY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotCZ = nAttr.create( 'bbrZ', 'bbrZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotC = nAttr.create( 'botBackRight', 'botBackRight', ControlBox.aBotCX, ControlBox.aBotCY, ControlBox.aBotCZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    ControlBox.aBotDX = nAttr.create( 'bblX', 'bblX', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotDY = nAttr.create( 'bblY', 'bblY', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotDZ = nAttr.create( 'bblZ', 'bblZ', OpenMaya.MFnNumericData.kDouble, 0.0 )
    ControlBox.aBotD = nAttr.create( 'botBackLeft', 'botBackLeft', ControlBox.aBotDX, ControlBox.aBotDY, ControlBox.aBotDZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )

    ControlBox.aState = nAttr.create( 'state', 's', OpenMaya.MFnNumericData.kLong, 0 )
    
    ControlBox.addAttribute( ControlBox.aColor )
    ControlBox.addAttribute( ControlBox.aRotate )
    ControlBox.addAttribute( ControlBox.aTransparency )
    ControlBox.addAttribute( ControlBox.aBackAlpha )
    ControlBox.addAttribute( ControlBox.aLineWidth )
    ControlBox.addAttribute( ControlBox.aWidth )
    ControlBox.addAttribute( ControlBox.aHeight )
    ControlBox.addAttribute( ControlBox.aDepth )
    ControlBox.addAttribute( ControlBox.aDrawType )

    ControlBox.addAttribute( ControlBox.aTopA )
    ControlBox.addAttribute( ControlBox.aTopB )
    ControlBox.addAttribute( ControlBox.aTopC )
    ControlBox.addAttribute( ControlBox.aTopD )
    ControlBox.addAttribute( ControlBox.aBotA )
    ControlBox.addAttribute( ControlBox.aBotB )
    ControlBox.addAttribute( ControlBox.aBotC )
    ControlBox.addAttribute( ControlBox.aBotD )

    ControlBox.addAttribute( ControlBox.aState )    
    OpenMayaMPx.MPxManipContainer.addToManipConnectTable( nodeID )

# ==
# COMMAND
class controllerCmd( OpenMayaMPx.MPxCommand ):
    def __init__( self ):
        ''' Command constructor. '''
        OpenMayaMPx.MPxCommand.__init__( self )
        self.MDagMod = OpenMaya.MDagModifier()
        self.MFnDepNode = OpenMaya.MFnDependencyNode()
        self.MDGMod = OpenMaya.MDGModifier()
        self.MFnDagNode = OpenMaya.MFnDagNode()
   
    def parseArguments( self, args ):
        # FLAGS: Setup flags.
        # An error here likely means the flag doesn't exist in the syntax.
        argData = OpenMaya.MArgDatabase( self.syntax(), args )
        
        # Name.
        if argData.isFlagSet( kShortName ) or argData.isFlagSet( kLongName ):
            self.name = argData.flagArgumentString( kShortName, 0 )
        else:
            self.name = 'controller'
            
        # Offset position.
        if argData.isFlagSet( kShortPosition ) or argData.isFlagSet( kLongPosition ):
            # The 0 is the index of the flag's parameter.
            self.position = [ argData.flagArgumentDouble( kShortPosition, 0 ),
                              argData.flagArgumentDouble( kShortPosition, 1 ),
                              argData.flagArgumentDouble( kShortPosition, 2 ) ]
        else:
            self.position = [ 0.0, 0.0, 0.0 ]
            
        # Line width.
        if argData.isFlagSet( kShortLineWidth ) or argData.isFlagSet( kLongLineWidth ):
            self.lineWidth = argData.flagArgumentInt( kShortLineWidth, 0 )
        else:
            self.lineWidth = 1
            
        # Offset rotate.
        if argData.isFlagSet( kShortRotate ) or argData.isFlagSet( kLongRotate ):
            self.rotation = OpenMaya.MEulerRotation( argData.flagArgumentMAngle( kShortRotate, 0 ).asDegrees(),
                                                     argData.flagArgumentMAngle( kShortRotate, 1 ).asDegrees(),
                                                     argData.flagArgumentMAngle( kShortRotate, 2 ).asDegrees() )
        else:
            self.rotation = OpenMaya.MEulerRotation( 0.0, 0.0, 0.0 )
        
        # Transparency.
        if argData.isFlagSet( kShortTransparency ) or argData.isFlagSet( kLongTransparency ):
            self.transparency = argData.flagArgumentDouble( kShortTransparency, 0 )
        else:
            self.transparency = 0.5
        
        # Back alpha.
        if argData.isFlagSet( kShortBackAlpha ) or argData.isFlagSet( kLongBackAlpha ):
            self.backAlpha = argData.flagArgumentDouble( kShortBackAlpha, 0 )
        else:
            self.backAlpha = 0.2

        # Color.
        if argData.isFlagSet( kShortColor ) or argData.isFlagSet( kLongColor ):
            self.color = [ argData.flagArgumentDouble( kShortColor, 0 ),
                           argData.flagArgumentDouble( kShortColor, 1 ),
                           argData.flagArgumentDouble( kShortColor, 2 ) ]
        else:
            self.color = [ 0.2, 0.2, 0.5 ]
        
        # Draw type.
        if argData.isFlagSet( kShortDrawType ) or argData.isFlagSet( kLongDrawType ):
            self.drawType = argData.flagArgumentInt( kShortDrawType, 0 )
        else:
            self.drawType = 2
        
        # Width.
        if argData.isFlagSet( kShortWidth ) or argData.isFlagSet( kLongWidth ):
            self.width = argData.flagArgumentDouble( kShortWidth, 0 )
        else:
            self.width = 1.0
        
        # Height.
        if argData.isFlagSet( kShortHeight ) or argData.isFlagSet( kLongHeight ):
            self.height = argData.flagArgumentDouble( kShortHeight, 0 )
        else:
            self.height = 1.0
        
        # Depth.
        if argData.isFlagSet( kShortDepth ) or argData.isFlagSet( kLongDepth ):
            self.depth = argData.flagArgumentDouble( kShortDepth, 0 )
        else:
            self.depth = 1.0
        
        # Offset points.        
        if argData.isFlagSet( kShortTopFrontRight ) or argData.isFlagSet( kLongTopFrontRight ):
            self.opTFR = [ argData.flagArgumentDouble( kShortTopFrontRight, 0 ),
                           argData.flagArgumentDouble( kShortTopFrontRight, 1 ),
                           argData.flagArgumentDouble( kShortTopFrontRight, 2 ) ]
        else:
            self.opTFR = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortTopFrontLeft ) or argData.isFlagSet( kLongTopFrontLeft ):
            self.opTFL = [ argData.flagArgumentDouble( kShortTopFrontLeft, 0 ),
                           argData.flagArgumentDouble( kShortTopFrontLeft, 1 ),
                           argData.flagArgumentDouble( kShortTopFrontLeft, 2 ) ]
        else:
            self.opTFL = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortTopBackRight ) or argData.isFlagSet( kLongTopBackRight ):
            self.opTBR = [ argData.flagArgumentDouble( kShortTopBackRight, 0 ),
                           argData.flagArgumentDouble( kShortTopBackRight, 1 ),
                           argData.flagArgumentDouble( kShortTopBackRight, 2 ) ]
        else:
            self.opTBR = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortTopBackLeft ) or argData.isFlagSet( kLongTopBackLeft ):
            self.opTBL = [ argData.flagArgumentDouble( kShortTopBackLeft, 0 ),
                           argData.flagArgumentDouble( kShortTopBackLeft, 1 ),
                           argData.flagArgumentDouble( kShortTopBackLeft, 2 ) ]
        else:
            self.opTBL = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortBotFrontRight ) or argData.isFlagSet( kLongBotFrontRight ):
            self.opBFR = [ argData.flagArgumentDouble( kShortBotFrontRight, 0 ),
                           argData.flagArgumentDouble( kShortBotFrontRight, 1 ),
                           argData.flagArgumentDouble( kShortBotFrontRight, 2 ) ]
        else:
            self.opBFR = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortBotFrontLeft ) or argData.isFlagSet( kLongBotFrontLeft ):
            self.opBFL = [ argData.flagArgumentDouble( kShortBotFrontLeft, 0 ),
                           argData.flagArgumentDouble( kShortBotFrontLeft, 1 ),
                           argData.flagArgumentDouble( kShortBotFrontLeft, 2 ) ]
        else:
            self.opBFL = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortBotBackRight ) or argData.isFlagSet( kLongBotBackRight ):
            self.opBBR = [ argData.flagArgumentDouble( kShortBotBackRight, 0 ),
                           argData.flagArgumentDouble( kShortBotBackRight, 1 ),
                           argData.flagArgumentDouble( kShortBotBackRight, 2 ) ]
        else:
            self.opBBR = [ 0.0, 0.0, 0.0 ]
            
        if argData.isFlagSet( kShortBotBackLeft ) or argData.isFlagSet( kLongBotBackLeft ):
            self.opBBL = [ argData.flagArgumentDouble( kShortBotBackLeft, 0 ),
                           argData.flagArgumentDouble( kShortBotBackLeft, 1 ),
                           argData.flagArgumentDouble( kShortBotBackLeft, 2 ) ]
        else:
            self.opBBL = [ 0.0, 0.0, 0.0 ]

    def doIt( self, args ):
        ''' Setup the command. '''
        # Parse the flags and arguments.
        self.parseArguments( args )
        
        # Create the controller node.
        self.controllerNode = self.MDagMod.createNode( nodeName )
        self.redoIt()
                
    def redoIt( self ):
        ''' Do the actual work of the command. '''
        # Perform the operations enqueued within our reference to MDagModifier. This effectively
        # creates the DAG nodes specified using self.dagModifier.createNode(). Node creation is 
        # done in doIt().
        self.MDagMod.doIt()
        
        # Apply the user defined arguments to the controller node.
        self.MFnDagNode.setObject( self.controllerNode )
        
        # Set the name.
        self.MFnDagNode.setName( self.name )
        # Get the aim node's shape.
        self.MFnDepNode.setObject( self.MFnDagNode.child( 0 ) )
        print self.MFnDepNode.name()
        
        # Update plugs with values, if any, from the command.
        print self.MFnDepNode.findPlug( 'color' )
        
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'color' ), self.color )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'localPosition' ), self.position )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'rotate' ), self.rotation )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'transparency' ), self.transparency )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'backAlpha' ), self.backAlpha )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'lineWidth' ), self.lineWidth )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'width' ), self.width )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'height' ), self.height )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'depth' ), self.depth )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'drawType' ), self.drawType )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'topFrontRight' ), self.opTFR )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'topFrontLeft' ), self.opTFL )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'topBackRight' ), self.opTBR )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'topBackLeft' ), self.opTBL )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'botFrontRight' ), self.opBFR )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'botFrontLeft' ), self.opBFL )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'botBackRight' ), self.opBBR )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'botBackLeft' ), self.opBBL )
            
        self.MDGMod.doIt()
    
    def undoIt( self ):
        ''' Clean up anything done by the command. '''
        self.MFnDagNode.removeChild( self.controllerNode )
        self.MDagMod.undoIt()
        
    def isUndoable( self ):
        return True
    
# ===
# INITIALIZE COMMAND
def cmdCreator():
    ''' Creates an instance of the command. '''
    return OpenMayaMPx.asMPxPtr( controllerCmd() )

def syntaxCreator():
    ''' Creates the arguments and flags of the command. '''
    syntax = OpenMaya.MSyntax()
    
    # FLAGS: Add flags.
    syntax.addFlag( kShortName, kLongName, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortPosition, kLongPosition, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortLineWidth, kLongLineWidth, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortRotate, kLongRotate, OpenMaya.MSyntax.kAngle, OpenMaya.MSyntax.kAngle, OpenMaya.MSyntax.kAngle )
    syntax.addFlag( kShortTransparency, kLongTransparency, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortBackAlpha, kLongBackAlpha, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortColor, kLongColor, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortDrawType, kLongDrawType, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortWidth, kLongWidth, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortHeight, kLongHeight, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortDepth, kLongDepth, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortTopFrontRight, kLongTopFrontRight, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortTopFrontLeft, kLongTopFrontLeft, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortTopBackRight, kLongTopBackRight, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortTopBackLeft, kLongTopBackLeft, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortBotFrontRight, kLongBotFrontRight, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortBotFrontLeft, kLongBotFrontLeft, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortBotBackRight, kLongBotBackRight, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortBotBackLeft, kLongBotBackLeft, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble, OpenMaya.MSyntax.kDouble )
    return syntax

# ==
# MANIPULATOR
class ContrlBoxManip( OpenMayaMPx.MPxManipContainer ):
    def __init__( self ):
        OpenMayaMPx.MPxManipContainer.__init__( self )
        
        self.leftSideManip = OpenMaya.MDagPath()
        self.rightSideManip = OpenMaya.MDagPath()
        self.widthManip = OpenMaya.MDagPath()
        self.heightManip = OpenMaya.MDagPath()
        self.depthManip = OpenMaya.MDagPath()
        self.fStateManip = OpenMaya.MDagPath()
        self.fNodePath = OpenMaya.MDagPath()
        
    def createChildren(self ):
        # Left Side Manip
        self.leftSideManip = self.addFreePointTriadManip( 'leftSideManip', 'lsm' )
        leftSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.leftSideManip )
        
        # Right Side Manip
        self.rightSideManip = self.addFreePointTriadManip( 'rightSideManip', 'rsm' )
        rightSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.rightSideManip )
        
        # Width/Height/Depth
        self.startPoint = OpenMaya.MPoint( 0, 0, 0 )
        self.widthManip = self.addDistanceManip( 'widthManip', 'width' )
        widthManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        
        self.heightManip = self.addDistanceManip( 'heightManip', 'height' )
        heightManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        
        self.depthManip = self.addDistanceManip( 'depthManip', 'depth' )
        depthManipFn = OpenMayaUI.MFnDistanceManip( self.depthManip )
        
        # State Change
        self.fStateManip = self.addStateManip("stateManip", "state")
        stateManipFn = OpenMayaUI.MFnStateManip(self.fStateManip)
        stateManipFn.setMaxStates( 2 )
        stateManipFn.setInitialState( 0 )
        
    def connectToDependNode( self, node ):
        # Get the DAG path
        dagNodeFn = OpenMaya.MFnDagNode(node)
        dagNodeFn.getPath(self.fNodePath)
        parentNode = dagNodeFn.parent(0)
        parentNodeFn = OpenMaya.MFnDagNode(parentNode)

        # Connect the plugs
        nodeFn = OpenMaya.MFnDependencyNode()
        nodeFn.setObject(node)
        
        print 'parentNode: {0}'.format( parentNode )
        print 'parentNodeFn: {0}'.format( parentNodeFn.name() )
        print 'nodeFn: {0}'.format( nodeFn.name() )        
        
        localPosition = NodeUtility.getPlugValue( nodeFn.findPlug( 'localPosition' ) )
        
        tfrPlug = nodeFn.findPlug( 'topFrontRight' )
        tbrPlug = nodeFn.findPlug( 'topBackRight' )
        bfrPlug = nodeFn.findPlug( 'botFrontRight' )
        bbrPlug = nodeFn.findPlug( 'botBackRight' )
        
        tflPlug = nodeFn.findPlug( 'topFrontLeft' )
        tblPlug = nodeFn.findPlug( 'topBackLeft' )
        bflPlug = nodeFn.findPlug( 'botFrontLeft' )
        bblPlug = nodeFn.findPlug( 'botBackLeft' )
        
        tfrValue = NodeUtility.getPlugValue( tfrPlug )
        tbrValue = NodeUtility.getPlugValue( tbrPlug )
        bfrValue = NodeUtility.getPlugValue( bfrPlug )
        bbrValue = NodeUtility.getPlugValue( bbrPlug )
        
        tflValue = NodeUtility.getPlugValue( tflPlug )
        tblValue = NodeUtility.getPlugValue( tblPlug )
        bflValue = NodeUtility.getPlugValue( bflPlug )
        bblValue = NodeUtility.getPlugValue( bblPlug )
        
        widthPlug = nodeFn.findPlug( 'width' )
        widthValue = NodeUtility.getPlugValue( widthPlug )
        heightPlug = nodeFn.findPlug( 'height' )
        heightValue = NodeUtility.getPlugValue( heightPlug )
        depthPlug = nodeFn.findPlug( 'depth' )       
        depthValue = NodeUtility.getPlugValue( depthPlug )
            
        drawPoints = []        
        drawPoints.append( [ ( -widthValue/2 + bfrValue[0] ) + localPosition[0], ( -heightValue/2+bfrValue[1] ) + localPosition[1], ( depthValue/2+bfrValue[2] ) + localPosition[2] ] ) #0, bottomFrontRight
        drawPoints.append( [ ( -widthValue/2+bbrValue[0] ) + localPosition[0], ( -heightValue/2+bbrValue[1] ) + localPosition[1], ( -depthValue/2+bbrValue[2] ) + localPosition[2] ] ) #1, bottomBackRight
        drawPoints.append( [ ( -widthValue/2 + tfrValue[0] ) + localPosition[0], ( heightValue/2+tfrValue[1] ) + localPosition[1], ( depthValue/2+tfrValue[2] ) + localPosition[2] ] ) #2, topFrontRight
        drawPoints.append( [ ( -widthValue/2+tbrValue[0] ) + localPosition[0], ( heightValue/2+tbrValue[1] ) + localPosition[1], ( -depthValue/2+tbrValue[2] ) + localPosition[2] ] ) #3, topBackRight
        
        drawPoints.append( [ ( widthValue/2 + bflValue[0] ) + localPosition[0], ( -heightValue/2+bflValue[1] ) + localPosition[1], ( depthValue/2+bflValue[2] ) + localPosition[2] ] ) #4, bottomFrontLeft
        drawPoints.append( [ ( widthValue/2+bblValue[0] ) + localPosition[0], ( -heightValue/2+bblValue[1] ) + localPosition[1], ( -depthValue/2+bblValue[2] ) + localPosition[2] ] ) #5, bottomBackLeft
        drawPoints.append( [ ( widthValue/2 + tflValue[0] ) + localPosition[0], ( heightValue/2+tflValue[1] ) + localPosition[1], ( depthValue/2+tflValue[2] ) + localPosition[2] ] ) #6, topFrontLeft
        drawPoints.append( [ ( widthValue/2+tblValue[0] ) + localPosition[0], ( heightValue/2+tblValue[1] ) + localPosition[1], ( -depthValue/2+tblValue[2] ) + localPosition[2] ] ) #7, topBackLeft

        # Triad Manipulator for right side
        try:
            leftSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.leftSideManip )
            #translationPlug = nodeFn.findPlug('topFrontRight')               
            centroid = getCentroid( [ drawPoints[2], drawPoints[3], drawPoints[0], drawPoints[1] ] )
            leftSideTriadManipFn.setTranslation( centroid, OpenMaya.MSpace.kTransform )
            
            leftSideTriadManipFn.connectToPointPlug( tfrPlug )
            leftSideTriadManipFn.connectToPointPlug( tbrPlug )
            leftSideTriadManipFn.connectToPointPlug( bfrPlug )
            leftSideTriadManipFn.connectToPointPlug( bbrPlug )
            self.addPlugToManipConversion( self.leftSideManip )
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: left side tri\n' )
        
        # Triad manipulator for left side
        try:                
            rightSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.rightSideManip )
            #translationPlug = nodeFn.findPlug('topFrontRight')
            centroid = getCentroid( [ drawPoints[6], drawPoints[7], drawPoints[4], drawPoints[5] ] )
            rightSideTriadManipFn.setTranslation( centroid, OpenMaya.MSpace.kTransform )
            
            rightSideTriadManipFn.connectToPointPlug( tflPlug )
            rightSideTriadManipFn.connectToPointPlug( tblPlug )
            rightSideTriadManipFn.connectToPointPlug( bflPlug )
            rightSideTriadManipFn.connectToPointPlug( bblPlug )
            self.addPlugToManipConversion( self.rightSideManip )
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: right side tri\n' )
        
        # Width
        try:
            widthManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
            widthManipFn.setStartPoint( self.startPoint )
            self.widthDir = OpenMaya.MVector( widthValue, 0.0, 0.0 )
            widthManipFn.setDirection( self.widthDir )
            widthManipFn.connectToDistancePlug( widthPlug )
            #self.addPlugToManipConversion( widthManipFn.startPointIndex() )
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: width\n' )
        
        # Height
        try:
            heightManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
            heightManipFn.setStartPoint( self.startPoint )
            self.heightDir = OpenMaya.MVector( 0.0, heightValue, 0.0 )
            heightManipFn.setDirection( self.heightDir )
            heightManipFn.connectToDistancePlug( heightPlug )
            #self.addPlugToManipConversion( heightManipFn.startPointIndex() )
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: height\n' )
            
        # Depth
        try:
            depthManipFn = OpenMayaUI.MFnDistanceManip( self.depthManip )
            depthManipFn.setStartPoint( self.startPoint )
            self.depthDir = OpenMaya.MVector( 0.0, 0.0, depthValue )
            depthManipFn.setDirection( self.depthDir )
            depthManipFn.connectToDistancePlug( depthPlug )
            #self.addPlugToManipConversion( depthManipFn.startPointIndex() )
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: depth\n' )
        
        # StateManip
        try:
            stateManipFn = OpenMayaUI.MFnStateManip(self.fStateManip)
            statePlug = nodeFn.findPlug("state")
            stateManipFn.connectToStatePlug(statePlug)
            positionIndex = stateManipFn.positionIndex()
            stateManipFn.setTranslation( OpenMaya.MVector( 0, 0, 3 ), OpenMaya.MSpace.kTransform )
            self.addPlugToManipConversion(positionIndex)
        except:
            sys.stderr.write( 'ERROR: rigControllers.connectToDependNode: state\n' )
            
        self.updateManipLocations( node )
        self.finishAddingManips()
        OpenMayaMPx.MPxManipContainer.connectToDependNode( self, node )
        
    def draw(self, view, path, style, status):
        OpenMayaMPx.MPxManipContainer.draw(self, view, path, style, status)
        mode = OpenMayaUI.MFnStateManip(self.fStateManip).state()
        
        leftSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.leftSideManip )
        rightSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.rightSideManip )
        
        widthManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        heightManipFn = OpenMayaUI.MFnDistanceManip( self.heightManip )
        depthManipFn = OpenMayaUI.MFnDistanceManip( self.depthManip )
            
        view.beginGL()
        if mode == 0:
            textPos = OpenMaya.MPoint(self.nodeTranslation())
            view.drawText('Fuck', textPos, OpenMayaUI.M3dView.kLeft)
            leftSideTriadManipFn.setVisible( True )
            rightSideTriadManipFn.setVisible( True )
            
            widthManipFn.setVisible( False )
            heightManipFn.setVisible( False )
            depthManipFn.setVisible( False )
        else:
            textPos = OpenMaya.MPoint(self.nodeTranslation())
            view.drawText('Shit', textPos, OpenMayaUI.M3dView.kLeft)
            leftSideTriadManipFn.setVisible( False )
            rightSideTriadManipFn.setVisible( False )
            
            widthManipFn.setVisible( True )
            heightManipFn.setVisible( True )
            depthManipFn.setVisible( True )
        view.endGL()

    def updateManipLocations( self, node ):
        '''
        Moves manipulators with the object.
        '''
        nodeFn = OpenMaya.MFnDependencyNode()
        nodeFn.setObject(node)    
        
        nodeMatrix = TransformUtility.getMatrix( nodeFn.name(), 'worldMatrix' )
        nodePos = TransformUtility.getMatrixTranslation( nodeMatrix )
        nodeRot = TransformUtility.getMatrixRotation( nodeMatrix, 'quat' )
        
        leftSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.leftSideManip )
        leftSideTriadManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        leftSideTriadManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
        rightSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.rightSideManip )        
        rightSideTriadManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        rightSideTriadManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
        widthManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        widthManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        widthManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
        heightManipFn = OpenMayaUI.MFnDistanceManip( self.heightManip )
        heightManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        heightManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
        depthManipFn = OpenMayaUI.MFnDistanceManip( self.depthManip )
        depthManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        depthManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
        stateManipFn = OpenMayaUI.MFnStateManip(self.fStateManip)
        stateManipFn.setTranslation( nodePos, OpenMaya.MSpace.kWorld )
        stateManipFn.setRotation( nodeRot, OpenMaya.MSpace.kWorld )
        
    def plugToManipConversion( self, manipIndex ):
        try:
            numData = OpenMaya.MFnNumericData()
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Double)
            
            vec = self.nodeTranslation()
            numData.setData3Double(vec.x, vec.y, vec.z)
            
            returnData = OpenMayaUI.MManipData( numDataObj ) 
        except:
            sys.stderr.write("ERROR: footPrintLocatorManip.plugToManipConversion\n")
            raise
        return returnData
        '''
        manipData = OpenMayaUI.MManipData()
        numData = OpenMaya.MFnNumericData()
        print theIndex
        
        leftSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.leftSideManip )
        rightSideTriadManipFn = OpenMayaUI.MFnFreePointTriadManip( self.rightSideManip )
        widthManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        heightManipFn = OpenMayaUI.MFnDistanceManip( self.widthManip )
        depthManipFn = OpenMayaUI.MFnDistanceManip( self.depthManip )
        
        if theIndex == leftSideTriadManipFn.pointIndex():
            print 'left side tri'
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
            vec = self.nodeTranslation()
            numData.setData3Float(vec.x, vec.y, vec.z)
            manipData = OpenMayaUI.MManipData(numDataObj)
            
        elif theIndex == leftSideTriadManipFn.pointIndex():
            print 'right side tri'
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
            vec = self.nodeTranslation()
            numData.setData3Float(vec.x, vec.y, vec.z)
            manipData = OpenMayaUI.MManipData(numDataObj)
            
        elif theIndex == widthManipFn.startPointIndex():
            print 'width'
            #numData = OpenMaya.MFnNumericData()
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
            vec = self.nodeTranslation()
            numData.setData3Double(vec.x, vec.y, vec.z)
            manipData = OpenMayaUI.MManipData(numDataObj)
            
        elif theIndex == heightManipFn.startPointIndex():
            print 'height'
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
            vec = self.nodeTranslation()
            numData.setData3Double(vec.x, vec.y, vec.z)
            manipData = OpenMayaUI.MManipData(numDataObj)
            
        elif theIndex == depthManipFn.startPointIndex():
            print 'depth'
            numDataObj = numData.create(OpenMaya.MFnNumericData.k3Float)
            vec = self.nodeTranslation()
            numData.setData3Double(vec.x, vec.y, vec.z)
            manipData = OpenMayaUI.MManipData(numDataObj)       
        
        return manipData
        '''

    def nodeTranslation(self):
            dagFn = OpenMaya.MFnDagNode(self.fNodePath)
            path = OpenMaya.MDagPath()
            dagFn.getPath(path)
            path.pop()  # pop from the shape to the transform
            transformFn = OpenMaya.MFnTransform(path)
            return transformFn.getTranslation(OpenMaya.MSpace.kWorld)
    
def manipCreator():
    return ContrlBoxManip()

def manipInit():
    OpenMayaMPx.MPxManipContainer.initialize()
    
# ==
#  UTILITY
def getCentroid( inPoints ):
    '''
    Returns the centroid of a list of points.
    @param inPoints: List of points.
    '''
    numPoints = len( inPoints )
    for p in xrange( len( inPoints )-1 ):
        if p == 0:
            x = inPoints[p][0] + inPoints[p+1][0]
            y = inPoints[p][1] + inPoints[p+1][1]
            z = inPoints[p][2] + inPoints[p+1][2]
        else:
            x = x + inPoints[p+1][0]
            y = y + inPoints[p+1][1]
            z = z + inPoints[p+1][2]
    x = x / numPoints
    y = y / numPoints
    z = z / numPoints
    
    return OpenMaya.MVector( x, y, z )

# ==
#  PLUGIN INIT
def initializePlugin( obj ):
    ''' initialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj, 'Austin Baker', '1.0', 'Any' )
    try:
        plugin.registerCommand( cmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write( 'Failed to register command: {0}'.format( cmdName ) )
        raise
    try:
        plugin.registerNode( nodeName, nodeID, nodeCreator, nodeInitializer,
                             OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( nodeName ) )
        raise
    try:
        plugin.registerNode( manipNodeName, manipNodeID, manipCreator, manipInit,
                             OpenMayaMPx.MPxNode.kManipContainer )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( manipNodeName ) )
        raise

def uninitializePlugin( obj ):
    ''' uninitialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj )
    try:
        plugin.deregisterCommand( cmdName )
    except:
        sys.stderr.write( 'Failed to deregister command: {0}'.format( cmdName ) )
        raise
    try:
        plugin.deregisterNode( nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( nodeName ) )
        raise
    try:
        plugin.deregisterNode( manipNodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( manipNodeName ) )
        raise