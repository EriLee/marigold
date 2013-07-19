'''
IMPORTS
'''
import sys
import math
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

'''
NODES: Names and IDs.
'''
glBox_nodeName = 'glBox'
glBox_nodeID = OpenMaya.MTypeId( 0x1001A )
glSphere_nodeName = 'glSphere'
glSphere_nodeID = OpenMaya.MTypeId( 0x1001B )
glCylinder_nodeName = 'glCylinder'
glCylinder_nodeID = OpenMaya.MTypeId( 0x1001C )
glCone_nodeName = 'glCone'
glCone_nodeID = OpenMaya.MTypeId( 0x1001D )
glTorus_nodeName = 'glTorus'
glTorus_nodeID = OpenMaya.MTypeId( 0x1001E )
glSpanner_nodeName = 'glSpanner'
glSpanner_nodeID = OpenMaya.MTypeId( 0x1001F )

'''
COMMAND: Flags.
'''
cmdName = 'makeGLBit'
kShortType = '-ot'
kLongType = '-objecttype'
kShortName = '-n'
kLongName = '-name'
kShortPosition = '-pos'
kLongPosition = '-position'
kShortScale = '-scl'
kLongScale = '-scale'
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
# sphere
kShortLatitude = '-slt'
kLongLatitude = '-sphLatitude'
kShortLongitude = '-slg'
kLongLongitude = '-sphLongitude'
kShortRadius = '-ord'
kLongRadius = '-oRadius'
# torus
kShortSides = '-tsd'
kLongSides = '-torSides'
kShortRings = '-trg'
kLongRings = '-torRings'
kShortOuterRadius = '-tor'
kLongOuterRadius = '-torOtRad'
kShortInnerRadius = '-tir'
kLongInnerRadius = '-torInRad'
kShortDrawPlace = '-dp'
kLongDrawPlace = '-drawPlace'
# cone
kShortSegments = '-nsg'
kLongSegments = '-numSegments'
kShortConeLength = '-cln'
kLongConeLength = '-coneLength'
# cylinder
kShortCylinderLength = '-cyn'
kLongCylinderLength = '-cylLength'
# spanner
kShortSpanSource = '-ss'
kLongSpanSource = '-spanSource'
kShortSpanTarget = '-st'
kLongSpanTarget = '-spanTarget'

'''

NODES

'''
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

def addStandardAttributes( node ):
    # Common attributes shared across all gl objects.
    nAttr = OpenMaya.MFnNumericAttribute()

    # Object color.
    node.aColor = nAttr.createColor( 'color', 'col' )
    nAttr.setDefault( 0.1, 0.1, 0.8 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0, 0, 0 )
    nAttr.setMax( 1, 1, 1 )
    
    # Object color alpha.
    node.aTransparency = nAttr.create( 'transparency', 't', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 0.5 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 1 )
    
    # Object children color.
    node.childLinkColor = nAttr.createColor( 'childLinkColor', 'clc' )
    nAttr.setDefault( 0.1, 0.1, 0.4 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0, 0, 0 )
    nAttr.setMax( 1, 1, 1 )
    
    # Object children color alpha.
    node.childTransparency = nAttr.create( 'childTransparency', 'ct', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 0.5 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 1 )
    
    # Object children line arrowhead radius.
    node.childArrowRadius = nAttr.create( 'childArrowRadius', 'car', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 1.0 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1)
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 10 )
    
    # Object children line arrowhead segments.
    node.childArrowSegments = nAttr.create( 'childArrowSegments', 'cas', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 6 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1)
    nAttr.setStorable( 1 )
    nAttr.setMin( 3 )
    nAttr.setMax( 20 )
    
    # Object offset rotation.
    node.aRotate = nAttr.createPoint( 'rotate', 'rot' )
    nAttr.setDefault( 0.0, 0.0, 0.0 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
  
    # Wireframe alpha.
    node.aBackAlpha = nAttr.create( 'backAlpha', 'ba', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 0.2 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1 )
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 1 )
  
    # Wireframe line width.
    node.aLineWidth = nAttr.create( 'lineWidth', 'lw', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 0 )
    nAttr.setKeyable( 1 )
    nAttr.setReadable( 1 )
    nAttr.setWritable( 1)
    nAttr.setStorable( 1 )
    nAttr.setMin( 0 )
    nAttr.setMax( 10 )
  
    node.addAttribute( node.aRotate )
    node.addAttribute( node.aBackAlpha )
    node.addAttribute( node.aLineWidth )    
    node.addAttribute( node.aColor )
    node.addAttribute( node.aTransparency )
    node.addAttribute( node.childLinkColor )
    node.addAttribute( node.childTransparency )
    node.addAttribute( node.childArrowRadius )
    node.addAttribute( node.childArrowSegments )
    
    
'''
START: GL BOX
'''
class glBox( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        # Declare the min and max points for the bounding box. The math for the points
        # is done in draw().
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        self.childLineRoot = OpenMaya.MVector()
        self.upVec = OpenMaya.MVector( 0, 1, 0 )
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
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        width = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'width' ) ).asFloat()#X
        height = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'height' ) ).asFloat()#Y
        depth = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'depth' ) ).asFloat()#Z
        rotation = NodeUtility.getPlugValue( rt )
        
        # Color for object.
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'color' ))
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Color for children lines.
        clc = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'childLinkColor' ) )
        childColor = NodeUtility.getPlugValue( clc )
        ( cr, cg, cb ) = tuple( childColor )[:3]
        ca = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childTransparency' ) ).asFloat()
        car = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowRadius' ) ).asFloat()
        cas = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowSegments' ) ).asInt()
        arl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'arrowLength' ) ).asFloat()
        
        # Get vectors for drawing lines between this node and it's children.
        mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
        childrenList = []
        for i in xrange( mPlug.numElements() ):
            childPlug = mPlug.elementByPhysicalIndex( i )
            mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
            mTrans = OpenMaya.MTransformationMatrix( mData )
            childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )
                
        # Do the maths! For each point we factor in the width/height/depth, the point tweak value and the offset object offset position.
        drawPoints = []
        drawPoints.append( [ ( width/2 ) + trX, ( -height/2 ) + trY, ( depth/2 ) + trZ ] ) #bottomFrontLeft
        drawPoints.append( [ ( -width/2 ) + trX, ( -height/2 ) + trY, ( depth/2 ) + trZ ] ) #bottomFrontRight
        drawPoints.append( [ ( width/2 ) + trX, ( -height/2 ) + trY, ( -depth/2 ) + trZ ] ) #bottomBackLeft
        drawPoints.append( [ ( -width/2 ) + trX, ( -height/2 ) + trY, ( -depth/2 ) + trZ ] ) #bottomBackRight
        drawPoints.append( [ ( width/2 ) + trX, ( height/2 ) + trY, ( depth/2 ) + trZ ] ) #topFrontLeft
        drawPoints.append( [ ( -width/2 ) + trX, ( height/2 ) + trY, ( depth/2 ) + trZ ] ) #topFrontRight
        drawPoints.append( [ ( width/2 ) + trX, ( height/2 ) + trY, ( -depth/2 ) + trZ ] ) #topBackLeft
        drawPoints.append( [ ( -width/2 ) + trX, ( height/2 ) + trY, ( -depth/2 ) + trZ ] ) #topBackRight
        
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
            for vec in childrenList:
                glFT.glBegin( OpenMayaRender.MGL_LINE_LOOP )
                glFT.glColor4f( cr, cg, cb, ca )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( vec.x, vec.y, vec.z )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
                circleCenter = ( vec + self.childLineRoot )/arl
                N = vec - self.childLineRoot
                R = (self.upVec - self.childLineRoot) ^ N
                R.normalize()
                S = R ^ N
                S.normalize()
                for i in xrange( cas+1, 0, -1 ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( vec.x, vec.y, vec.z )
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_POLYGON )
                for i in xrange( cas ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
            
            # Draw the box
            # Reset color after drawing children arrows.
            statusColor( r, g, b, a, status )
            
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
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )

def glBox_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glBox() )
  
def glBox_nodeInitializer():
    addStandardAttributes( glBox )
    nAttr = OpenMaya.MFnNumericAttribute()
    enumAttr = OpenMaya.MFnEnumAttribute()
    unitFn = OpenMaya.MFnUnitAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    
    glBox.aRotateX = unitFn.create( 'rotX', 'rotX', OpenMaya.MFnUnitAttribute.kAngle,0)
    glBox.aRotateY = unitFn.create( 'rotY', 'rotY', OpenMaya.MFnUnitAttribute.kAngle,0)
    glBox.aRotateZ = unitFn.create( 'rotZ', 'rotZ', OpenMaya.MFnUnitAttribute.kAngle,0)
    glBox.aRotate = nAttr.create( 'rotate', 'rotate', glBox.aRotateX, glBox.aRotateY, glBox.aRotateZ )
    nAttr.setKeyable( False )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glBox.aWidth = unitFn.create( 'width', 'width', OpenMaya.MFnUnitAttribute.kDistance )
    unitFn.setDefault(1.0)
    unitFn.setKeyable( True )
    unitFn.setReadable( True )
    unitFn.setWritable( True )
    unitFn.setStorable( True )
  
    glBox.aHeight = unitFn.create( 'height', 'height', OpenMaya.MFnUnitAttribute.kDistance )
    unitFn.setDefault(1.0)
    unitFn.setKeyable( True )
    unitFn.setReadable( True )
    unitFn.setWritable( True )
    unitFn.setStorable( True )
  
    glBox.aDepth = unitFn.create( 'depth', 'depth', OpenMaya.MFnUnitAttribute.kDistance )
    unitFn.setDefault(1.0)
    unitFn.setKeyable( True )
    unitFn.setReadable( True )
    unitFn.setWritable( True )
    unitFn.setStorable( True )
    
    glBox.aDrawType = enumAttr.create( 'drawType', 'drawType' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )

    glBox.aState = nAttr.create( 'state', 's', OpenMaya.MFnNumericData.kLong, 0 )
    
    glBox.targetWorldMatrix = mAttr.create( 'targetWorldMatrix', 'targetWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setKeyable( True )
    mAttr.setReadable( True )
    mAttr.setWritable( True )
    mAttr.setStorable( True )
    mAttr.setArray( True )
    
    glBox.arrowLength = nAttr.create( 'arrowLength', 'arl', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setMin( 1.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glBox.addAttribute( glBox.aWidth )
    glBox.addAttribute( glBox.aHeight )
    glBox.addAttribute( glBox.aDepth )
    glBox.addAttribute( glBox.aDrawType )
    glBox.addAttribute( glBox.aState )
    glBox.addAttribute( glBox.targetWorldMatrix )
    glBox.addAttribute( glBox.arrowLength )

'''
START: GL SPHERE
'''
class glSphere( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        # Declare the min and max points for the bounding box. The math for the points
        # is done in draw().
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        self.childLineRoot = OpenMaya.MVector()
        self.upVec = OpenMaya.MVector( 0, 1, 0 )
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        
    def compute( self, plug, dataBlock ):
        return OpenMaya.kUnknownParameter

    def draw( self, view, path, style, status ):
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        trX= OpenMaya.MPlug( self.thisMObject(), self.localPositionX ).asFloat()
        trY= OpenMaya.MPlug( self.thisMObject(), self.localPositionY ).asFloat()
        trZ= OpenMaya.MPlug( self.thisMObject(), self.localPositionZ ).asFloat()
        slX= OpenMaya.MPlug( self.thisMObject(), self.localScaleX ).asFloat()
        slY= OpenMaya.MPlug( self.thisMObject(), self.localScaleY ).asFloat()
        slZ= OpenMaya.MPlug( self.thisMObject(), self.localScaleZ ).asFloat()
        lw = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'lineWidth' ) ).asInt()
        rt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'rotate' ) )
        a = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'transparency' ) ).asFloat()
        ba = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'backAlpha' ) ).asFloat()
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        lat = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'latitude' ) ).asInt()
        long = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'longitude' ) ).asInt()
        rad = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'radius' ) ).asFloat()
        rotation = NodeUtility.getPlugValue( rt )
        
        # Color for object.
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'color' ) )
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Color for children lines.
        clc = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'childLinkColor' ) )
        childColor = NodeUtility.getPlugValue( clc )
        ( cr, cg, cb ) = tuple( childColor )[:3]
        ca = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childTransparency' ) ).asFloat()
        car = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowRadius' ) ).asFloat()
        cas = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowSegments' ) ).asInt()
        arl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'arrowLength' ) ).asFloat()
        
        # Get vectors for drawing lines between this node and it's children.
        mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
        childrenList = []
        for i in xrange( mPlug.numElements() ):
            childPlug = mPlug.elementByPhysicalIndex( i )
            mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
            mTrans = OpenMaya.MTransformationMatrix( mData )
            childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )
        
        # Get locations for bounding box corners.
        self.bbp1 = OpenMaya.MPoint( slX*rad+trX, slY*rad+trY, slZ*rad+trZ )
        self.bbp2 = OpenMaya.MPoint( slX*-rad+trX, slY*-rad+trY, slZ*-rad+trZ )
        
        def drawObject( self ):
            for vec in childrenList:
                glFT.glBegin( OpenMayaRender.MGL_LINE_LOOP )
                glFT.glColor4f( cr, cg, cb, ca )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( vec.x, vec.y, vec.z )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
                # Get the center of the circle end of the arrowhead.
                circleCenter = ( vec + self.childLineRoot )/arl
                # Get the normal vector from the parent to child.
                N = vec - self.childLineRoot
                # Get the first orthogonal vector.
                R = (self.upVec - self.childLineRoot) ^ N
                R.normalize()
                # Get the second orthogonal vector.
                S = R ^ N
                S.normalize()
                # Loop through the arrowhead segments to draw the cone.
                for i in xrange( cas+1, 0, -1 ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( vec.x, vec.y, vec.z )
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_POLYGON )
                # Can reverse the xrange by doing ( list, 0, -1 )
                for i in xrange( cas ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()

            # Draw sphere.
            statusColor( r, g, b, a, status )
            PI = math.pi
            for i in xrange( lat ):
                lat0 = PI * ( -0.5 + float( i ) / lat )
                z0  = math.sin( lat0 )
                zr0 = math.cos( lat0 )
                lat1 = PI * ( -0.5 + float( i+1 ) / lat )
                z1 = math.sin( lat1 )
                zr1 = math.cos( lat1 )
                glFT.glBegin( OpenMayaRender.MGL_QUAD_STRIP )
                for j in xrange( long+1 ):
                    lng = 2 * PI * float( j ) / long
                    x = math.cos( lng )
                    z = math.sin( lng )
                    glFT.glVertex3f( x*slX*zr0*rad+trX, z0*slY*rad+trY, z*slZ*zr0*rad+trZ )
                    glFT.glVertex3f( x*slX*zr1*rad+trX, z1*slY*rad+trY, z*slZ*zr1*rad+trZ )
                glFT.glEnd()
  
        def drawShaded( self ):
            # draw the faces
            glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glFrontFace( OpenMayaRender.MGL_CCW )
            drawObject( self )
            glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
            # draw the wireframe on top of the faces
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            glFT.glCullFace( OpenMayaRender.MGL_BACK )
  
        def drawWireframe( self ):
            # draw only the wireframe
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            
        view.beginGL()
        glFT.glPushMatrix()
        
        # change the facing of the controller
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
        # creates a bounding box for the object
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )
        
def glSphere_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glSphere() )

def glSphere_nodeInitializer():
    addStandardAttributes( glSphere )
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    
    glSphere.aLat = nAttr.create( 'latitude', 'lat', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 6 )
    nAttr.setMin( 2 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
  
    glSphere.aLong = nAttr.create( 'longitude', 'long', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 12 )
    nAttr.setMin( 2 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
  
    glSphere.aRad = nAttr.create( 'radius', 'rad', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    enumAttr = OpenMaya.MFnEnumAttribute()
    glSphere.aDrawType = enumAttr.create( 'drawType', 'dt' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )
    
    glSphere.targetWorldMatrix = mAttr.create( 'targetWorldMatrix', 'targetWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setKeyable( True )
    mAttr.setReadable( True )
    mAttr.setWritable( True )
    mAttr.setStorable( True )
    mAttr.setArray( True )
    
    glSphere.arrowLength = nAttr.create( 'arrowLength', 'arl', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setMin( 1.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glSphere.addAttribute( glSphere.aLat )
    glSphere.addAttribute( glSphere.aLong )
    glSphere.addAttribute( glSphere.aRad )
    glSphere.addAttribute( glSphere.aDrawType )
    glSphere.addAttribute( glSphere.targetWorldMatrix )
    glSphere.addAttribute( glSphere.arrowLength )
    

'''
START: GL CYLINDER
'''
class glCylinder( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        self.childLineRoot = OpenMaya.MVector()
        self.upVec = OpenMaya.MVector( 0, 1, 0 )
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        
    def compute( self, plug, dataBlock ):
        return OpenMaya.kUnknownParameter

    def draw( self, view, path, style, status ):
        trX= OpenMaya.MPlug( self.thisMObject(), self.localPositionX ).asFloat()
        trY= OpenMaya.MPlug( self.thisMObject(), self.localPositionY ).asFloat()
        trZ= OpenMaya.MPlug( self.thisMObject(), self.localPositionZ ).asFloat()
        slX= OpenMaya.MPlug( self.thisMObject(), self.localScaleX ).asFloat()
        slY= OpenMaya.MPlug( self.thisMObject(), self.localScaleY ).asFloat()
        slZ= OpenMaya.MPlug( self.thisMObject(), self.localScaleZ ).asFloat()
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        lw = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'lineWidth' ) ).asInt()
        rt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'rotate' ) )
        a = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'transparency' ) ).asFloat()
        ba = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'backAlpha' ) ).asFloat()
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        dp = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawPlace' ) ).asInt()
        rad = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'radius' ) ).asFloat()
        seg = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'segment' ) ).asInt()
        cLen = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'cylinderLength' ) ).asFloat()
        rotation = NodeUtility.getPlugValue( rt )
        
        # Color for object.
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ('color'))
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Color for children lines.
        clc = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'childLinkColor' ) )
        childColor = NodeUtility.getPlugValue( clc )
        ( cr, cg, cb ) = tuple( childColor )[:3]
        ca = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childTransparency' ) ).asFloat()
        car = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowRadius' ) ).asFloat()
        cas = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowSegments' ) ).asInt()
        arl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'arrowLength' ) ).asFloat()
        
        # Get vectors for drawing lines between this node and it's children.
        mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
        childrenList = []
        for i in xrange( mPlug.numElements() ):
            childPlug = mPlug.elementByPhysicalIndex( i )
            mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
            mTrans = OpenMaya.MTransformationMatrix( mData )
            childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )
        
        # Get bounding points.
        if dp == 0:
            self.bbp1 = OpenMaya.MPoint( slX*cLen+trX, slY*rad+trY, slZ+rad+trZ )
            self.bbp2 = OpenMaya.MPoint( slX*(-0.0)+trX, slY*(-rad)+trY, slZ*(-rad)+trZ )
        elif dp == 1:
            self.bbp1 = OpenMaya.MPoint( slX*rad+trX, slY*+cLen+trY, slZ+rad+trZ )
            self.bbp2 = OpenMaya.MPoint( slX*(-rad)+trX, slY*(-0.0)+trY, slZ*(-rad)+trZ )
        else:
            self.bbp1 = OpenMaya.MPoint( slX*rad+trX, slY*rad+trY, slZ+cLen+trZ )
            self.bbp2 = OpenMaya.MPoint( slX*(-rad)+trX, slY*(-rad)+trY, slZ*(-0.0)+trZ )
        
        def drawObject( self ):
            for vec in childrenList:
                glFT.glBegin( OpenMayaRender.MGL_LINE_LOOP )
                glFT.glColor4f( cr, cg, cb, ca )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( vec.x, vec.y, vec.z )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
                circleCenter = ( vec + self.childLineRoot )/arl
                N = vec - self.childLineRoot
                R = (self.upVec - self.childLineRoot) ^ N
                R.normalize()
                S = R ^ N
                S.normalize()
                for i in xrange( cas+1, 0, -1 ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( vec.x, vec.y, vec.z )
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_POLYGON )
                for i in xrange( cas ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
            
            # draw the cylinder
            # Reset color after drawing children arrows.
            statusColor( r, g, b, a, status )
            
            glFT.glBegin( OpenMayaRender.MGL_QUAD_STRIP )
            for i in xrange( seg+1 ):
                angle = ( i*360.0/seg ) * math.pi/180.0
                cyCos = math.cos( angle )
                cySin = math.sin( angle )
                if dp == 0:
                    glFT.glVertex3f( 0.0*slX+trX+cLen, cyCos*slY*rad+trY, cySin*slZ*rad+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, cyCos*slY*rad+trY, cySin*slZ*rad+trZ )
                elif dp == 1:
                    glFT.glVertex3f( cyCos*slX*rad+trX, 0.0*slY+trY, cySin*slZ*rad+trZ )
                    glFT.glVertex3f( cyCos*slX*rad+trX, 0.0*slY+trY+cLen, cySin*slZ*rad+trZ )
                else:
                    glFT.glVertex3f( cyCos*slX*rad+trX, cySin*slY*rad+trY, 0.0*slZ+trZ+cLen )
                    glFT.glVertex3f( cyCos*slX*rad+trX, cySin*slY*rad+trY, 0.0*slZ+trZ )
            glFT.glEnd()
            # bottom cap
            ang = float( 360 )/float( seg )
            glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_FAN )
            for i in xrange( seg ):
                x = math.cos( math.radians( ang*float( i ) ) )
                y = math.sin( math.radians( ang*float( i ) ) )
                x1= math.cos( math.radians( ang*float( i+1 ) ) )
                y1= math.sin( math.radians( ang*float( i+1 ) ) )
                if dp == 0:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, x1*slY*rad+trY, y1*slZ*rad+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, x*slY*rad+trY, y*slZ*rad+trZ )
                elif dp == 1:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( x*slX*rad+trX, 0.0*slY+trY, y*slZ*rad+trZ )
                    glFT.glVertex3f( x1*slX*rad+trX, 0.0*slY+trY, y1*slZ*rad+trZ )
                else:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( x1*slX*rad+trX, y1*slY*rad+trY, 0.0*slZ+trZ )
                    glFT.glVertex3f( x*slX*rad+trX, y*slY*rad+trY, 0.0*slZ+trZ )
            glFT.glEnd()
            # top cap
            glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_FAN )
            for i in xrange( seg ):
                x = math.cos( math.radians( ang*float( i ) ) )
                y = math.sin( math.radians( ang*float( i ) ) )
                x1= math.cos( math.radians( ang*float( i+1 ) ) )
                y1= math.sin( math.radians( ang*float( i+1 ) ) )
                if dp == 0:
                    glFT.glVertex3f( 0.0*slX+trX+cLen, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( 0.0*slX+trX+cLen, x*slY*rad+trY, y*slZ*rad+trZ )
                    glFT.glVertex3f( 0.0*slX+trX+cLen, x1*slY*rad+trY, y1*slZ*rad+trZ )
                elif dp == 1:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY+cLen, 0*slZ+trZ )
                    glFT.glVertex3f( x1*slX*rad+trX, 0.0*slY+trY+cLen, y1*slZ*rad+trZ )
                    glFT.glVertex3f( x*slX*rad+trX, 0.0*slY+trY+cLen, y*slZ*rad+trZ )
                else:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ+cLen )
                    glFT.glVertex3f( x*slX*rad+trX, y*slY*rad+trY, 0.0*slZ+trZ+cLen )
                    glFT.glVertex3f( x1*slX*rad+trX, y1*slY*rad+trY, 0.0*slZ+trZ+cLen )
            glFT.glEnd()
 
        def drawShaded( self ):
            # draw the faces
            glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glFrontFace( OpenMayaRender.MGL_CCW )
            drawObject( self )
            glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
            # draw the wireframe on top of the faces
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            glFT.glCullFace( OpenMayaRender.MGL_BACK )
  
        def drawWireframe( self ):
            # draw only the wireframe
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            
        view.beginGL()
        glFT.glPushMatrix()
        
        # change the facing of the controller
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
        
    def isBounded( self ):
        return True
  
    def drawLast( self ):
        return True
        
    def boundingBox( self ):
        # creates a bounding box for the object
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )
        
def glCylinder_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glCylinder() )
  
def glCylinder_nodeInitializer():
    addStandardAttributes( glCylinder )
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    
    glCylinder.aSeg = nAttr.create( 'segment', 'seg', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 8 )
    nAttr.setMin( 2 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
  
    glCylinder.aRad = nAttr.create( 'radius', 'rad', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(2.0)
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glCylinder.cLen = nAttr.create( 'cylinderLength', 'cLen', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    enumAttr = OpenMaya.MFnEnumAttribute()
    glCylinder.aDrawType = enumAttr.create( 'drawType', 'dt' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )
    
    glCylinder.aDrawPlace = enumAttr.create( 'drawPlace', 'dp' )
    enumAttr.addField( 'x', 0 )
    enumAttr.addField( 'y', 1 )
    enumAttr.addField( 'z', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 1 )
  
    glCylinder.targetWorldMatrix = mAttr.create( 'targetWorldMatrix', 'targetWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setKeyable( True )
    mAttr.setReadable( True )
    mAttr.setWritable( True )
    mAttr.setStorable( True )
    mAttr.setArray( True )
    
    glCylinder.arrowLength = nAttr.create( 'arrowLength', 'arl', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setMin( 1.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glCylinder.addAttribute( glCylinder.aSeg )
    glCylinder.addAttribute( glCylinder.cLen )
    glCylinder.addAttribute( glCylinder.aRad )
    glCylinder.addAttribute( glCylinder.aDrawType )
    glCylinder.addAttribute( glCylinder.aDrawPlace )
    glCylinder.addAttribute( glCylinder.targetWorldMatrix )
    glCylinder.addAttribute( glCylinder.arrowLength )
    
    
'''
START: GL CONE
'''
class glCone( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        self.childLineRoot = OpenMaya.MVector()
        self.upVec = OpenMaya.MVector( 0, 1, 0 )
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        
    def compute( self, plug, dataBlock ):
        return OpenMaya.kUnknownParameter

    def draw( self, view, path, style, status ):
        trX= OpenMaya.MPlug( self.thisMObject(), self.localPositionX ).asFloat()
        trY= OpenMaya.MPlug( self.thisMObject(), self.localPositionY ).asFloat()
        trZ= OpenMaya.MPlug( self.thisMObject(), self.localPositionZ ).asFloat()
        slX= OpenMaya.MPlug( self.thisMObject(), self.localScaleX ).asFloat()
        slY= OpenMaya.MPlug( self.thisMObject(), self.localScaleY ).asFloat()
        slZ= OpenMaya.MPlug( self.thisMObject(), self.localScaleZ ).asFloat()
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        lw = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'lineWidth' ) ).asInt()
        rt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'rotate' ) )
        a = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'transparency' ) ).asFloat()
        ba = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'backAlpha' ) ).asFloat()
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        dp = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawPlace' ) ).asInt()
        rad = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'radius' ) ).asFloat()
        seg = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'segment' ) ).asInt()
        cLen = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'coneLength' ) ).asFloat()
        rotation = NodeUtility.getPlugValue( rt )
        
        # Object color.
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ('color'))
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Color for children lines.
        clc = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'childLinkColor' ) )
        childColor = NodeUtility.getPlugValue( clc )
        ( cr, cg, cb ) = tuple( childColor )[:3]
        cat = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childTransparency' ) ).asFloat()
        car = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowRadius' ) ).asFloat()
        cas = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowSegments' ) ).asInt()
        arl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'arrowLength' ) ).asFloat()
        
        # Get vectors for drawing lines between this node and it's children.
        mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
        childrenList = []
        for i in xrange( mPlug.numElements() ):
            childPlug = mPlug.elementByPhysicalIndex( i )
            mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
            mTrans = OpenMaya.MTransformationMatrix( mData )
            childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )
                
        # Calculate bounding box.
        if dp == 0:
            # X
            self.bbp1 = OpenMaya.MPoint( (slX*cLen)+trX, slY*rad+trY, slZ*rad+trZ )
            self.bbp2 = OpenMaya.MPoint( slX*(-0.0)+trX, slY*(-rad)+trY, slZ*(-rad)+trZ )
        elif dp == 1:
            # Y
            self.bbp1 = OpenMaya.MPoint( slX*rad+trX, slY*(cLen+trY), slZ*rad+trZ )
            self.bbp2 = OpenMaya.MPoint( slX*(-rad)+trX, slY*(-0.0)+trY, slZ*(-rad)+trZ )
        else:
            # Z
            self.bbp1 = OpenMaya.MPoint( slX*rad+trX, slY*rad+trY, slZ*(cLen+trZ) )
            self.bbp2 = OpenMaya.MPoint( slX*(-rad)+trX, slY*(-rad)+trY, slZ*(-0.0)+trZ )
        
        def drawObject( self ):
            for vec in childrenList:
                glFT.glBegin( OpenMayaRender.MGL_LINE_LOOP )
                glFT.glColor4f( cr, cg, cb, cat )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( vec.x, vec.y, vec.z )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
                circleCenter = ( vec + self.childLineRoot )/arl
                N = vec - self.childLineRoot
                R = (self.upVec - self.childLineRoot) ^ N
                R.normalize()
                S = R ^ N
                S.normalize()
                for i in xrange( cas+1, 0, -1 ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( vec.x, vec.y, vec.z )
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_POLYGON )
                for i in xrange( cas ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
            
            # draw the cone
            # Reset color after drawing children arrows.
            statusColor( r, g, b, a, status )
            
            glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
            for i in xrange( seg+1 ):
                angle = ( i*360.0/seg ) * math.pi/180.0
                ca = math.cos( angle )
                sa = math.sin( angle )
                if dp == 0:
                    glFT.glVertex3f( 0.0*slX+trX, ca*slY*rad+trY, sa*slZ*rad+trZ )
                    glFT.glVertex3f( slX*cLen+trX, 0.0*slY+trY, 0.0*slZ+trZ )
                elif dp == 1:
                    glFT.glVertex3f( ca*slX*rad+trX, 0.0*slY+trY, sa*slZ*rad+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, slY*cLen+trY, 0.0*slZ+trZ )
                else:
                    glFT.glVertex3f( ca*slX*rad+trX, sa*slY*rad+trY, 0.0*slZ+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, 0.0*slY+trY, slZ*cLen+trZ )
            glFT.glEnd()
            
            # draw the bottom disc
            ang = float( 360 )/float( seg )
            glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_FAN )
            for i in xrange( seg ):
                x = math.cos( math.radians( ang*float( i ) ) )
                y = math.sin( math.radians( ang*float( i ) ) )
                x1= math.cos( math.radians( ang*float( i+1 ) ) )
                y1= math.sin( math.radians( ang*float( i+1 ) ) )
                if dp == 0:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, x*slY*rad+trY, y*slZ*rad+trZ )
                    glFT.glVertex3f( 0.0*slX+trX, x1*slY*rad+trY, y1*slZ*rad+trZ )
                elif dp == 1:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( x*slX*rad+trX, 0.0*slY+trY, y*slZ*rad+trZ )
                    glFT.glVertex3f( x1*slX*rad+trX, 0.0*slY+trY, y1*slZ*rad+trZ )
                else:
                    glFT.glVertex3f( 0.0*slX+trX, 0*slY+trY, 0*slZ+trZ )
                    glFT.glVertex3f( x*slX*rad+trX, y*slY*rad+trY, 0.0*slZ+trZ )
                    glFT.glVertex3f( x1*slX*rad+trX, y1*slY*rad+trY, 0.0*slZ+trZ )
            glFT.glEnd()
  
        def drawShaded( self ):
            # draw the faces
            glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glFrontFace( OpenMayaRender.MGL_CCW )
            drawObject( self )
            glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
            # draw the wireframe on top of the faces
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            glFT.glCullFace( OpenMayaRender.MGL_BACK )
  
        def drawWireframe( self ):
            # draw only the wireframe
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            
        view.beginGL()
        glFT.glPushMatrix()
        
        # change the facing of the controller
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
        
    def isBounded( self ):
        return True
  
    def drawLast( self ):
        return True
        
    def boundingBox( self ):
        # creates a bounding box for the object
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )
        
def glCone_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glCone() )
  
def glCone_nodeInitializer():
    addStandardAttributes( glCone )
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    
    glCone.aSeg = nAttr.create( 'segment', 'seg', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 8 )
    nAttr.setMin( 2 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
  
    glCone.aRad = nAttr.create( 'radius', 'rad', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(2.0)
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glCone.cLen = nAttr.create( 'coneLength', 'cLen', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    enumAttr = OpenMaya.MFnEnumAttribute()
    glCone.aDrawType = enumAttr.create( 'drawType', 'dt' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )
    
    glCone.aDrawPlace = enumAttr.create( 'drawPlace', 'dp' )
    enumAttr.addField( 'x', 0 )
    enumAttr.addField( 'y', 1 )
    enumAttr.addField( 'z', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 1 )
    
    glCone.targetWorldMatrix = mAttr.create( 'targetWorldMatrix', 'targetWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setKeyable( True )
    mAttr.setReadable( True )
    mAttr.setWritable( True )
    mAttr.setStorable( True )
    mAttr.setArray( True )
    
    glCone.arrowLength = nAttr.create( 'arrowLength', 'arl', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setMin( 1.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glCone.addAttribute( glCone.aSeg )
    glCone.addAttribute( glCone.cLen )
    glCone.addAttribute( glCone.aRad )
    glCone.addAttribute( glCone.aDrawType )
    glCone.addAttribute( glCone.aDrawPlace )
    glCone.addAttribute( glCone.targetWorldMatrix )
    glCone.addAttribute( glCone.arrowLength )
    
'''
START: GL TORUS
'''
class glTorus( OpenMayaMPx.MPxLocatorNode ):
    def __init__( self ):
        self.bbp1 = OpenMaya.MPoint()
        self.bbp2 = OpenMaya.MPoint()
        self.childLineRoot = OpenMaya.MVector()
        self.upVec = OpenMaya.MVector( 0, 1, 0 )
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        
    def compute( self, plug, dataBlock ):
        return OpenMaya.kUnknownParameter

    def draw( self, view, path, style, status ):        
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        trX= OpenMaya.MPlug( self.thisMObject(), self.localPositionX ).asFloat()
        trY= OpenMaya.MPlug( self.thisMObject(), self.localPositionY ).asFloat()
        trZ= OpenMaya.MPlug( self.thisMObject(), self.localPositionZ ).asFloat()
        slX= OpenMaya.MPlug( self.thisMObject(), self.localScaleX ).asFloat()
        slY= OpenMaya.MPlug( self.thisMObject(), self.localScaleY ).asFloat()
        slZ= OpenMaya.MPlug( self.thisMObject(), self.localScaleZ ).asFloat()
        lw = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'lineWidth' ) ).asInt()
        rt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'rotate' ) )
        a = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'transparency' ) ).asFloat()
        ba = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'backAlpha' ) ).asFloat()
        dt = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawType' ) ).asInt()
        dp = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'drawPlace' ) ).asInt()
        sides = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'sides' ) ).asInt()
        rings = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'rings' ) ).asInt()
        outRad = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'outerRadius' ) ).asFloat()
        inRad = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'innerRadius' ) ).asFloat()
        rotation = NodeUtility.getPlugValue( rt )
        
        # Object color.
        cl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ('color') )
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
        # Color for children lines.
        clc = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute ( 'childLinkColor' ) )
        childColor = NodeUtility.getPlugValue( clc )
        ( cr, cg, cb ) = tuple( childColor )[:3]
        ca = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childTransparency' ) ).asFloat()
        car = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowRadius' ) ).asFloat()
        cas = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'childArrowSegments' ) ).asInt()
        arl = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'arrowLength' ) ).asFloat()
        
        # Get vectors for drawing lines between this node and it's children.
        mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
        childrenList = []
        for i in xrange( mPlug.numElements() ):
            childPlug = mPlug.elementByPhysicalIndex( i )
            mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
            mTrans = OpenMaya.MTransformationMatrix( mData )
            childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )
                
        # Calculate bounding box.
        centerRadius = inRad * 0.5 + outRad * 0.5
        rangeRadius = outRad - centerRadius
        
        if dp == 0:
            # X
            self.bbp1 = OpenMaya.MPoint( rangeRadius*2*slX+trX, outRad*2*slY+trY, outRad*2*slZ+trZ )
            self.bbp2 = OpenMaya.MPoint( -rangeRadius*2*slX+trX, -outRad*2*slY+trY, -outRad*2*slZ+trZ )
        elif dp == 1:
            # Y
            self.bbp1 = OpenMaya.MPoint( outRad*2*slX+trX, rangeRadius*2*slY+trY, outRad*2*slZ+trZ )
            self.bbp2 = OpenMaya.MPoint( -outRad*2*slX+trX, -rangeRadius*2*slY+trY, -outRad*2*slZ+trZ )
        else:
            # Z
            self.bbp1 = OpenMaya.MPoint( outRad*2*slX+trX, outRad*2*slY+trY, rangeRadius*2*slZ+trZ )
            self.bbp2 = OpenMaya.MPoint( -outRad*2*slX+trX, -outRad*2*slY+trY, -rangeRadius*2*slZ+trZ )
        
        def drawObject( self ):
            for vec in childrenList:
                glFT.glBegin( OpenMayaRender.MGL_LINE_LOOP )
                glFT.glColor4f( cr, cg, cb, ca )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( vec.x, vec.y, vec.z )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_STRIP )
                circleCenter = ( vec + self.childLineRoot )/arl
                N = vec - self.childLineRoot
                R = (self.upVec - self.childLineRoot) ^ N
                R.normalize()
                S = R ^ N
                S.normalize()
                for i in xrange( cas+1, 0, -1 ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( vec.x, vec.y, vec.z )
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
                
                glFT.glBegin( OpenMayaRender.MGL_POLYGON )
                for i in xrange( cas ):
                    angle = ( i*360.0/cas ) * math.pi/180.0
                    coneCos = math.cos( angle )
                    coneSin = math.sin( angle )
                    Qx = circleCenter.x + car*coneCos*R.x + car*coneSin*S.x
                    Qy = circleCenter.y + car*coneCos*R.y + car*coneSin*S.y
                    Qz = circleCenter.z + car*coneCos*R.z + car*coneSin*S.z
                    glFT.glVertex3f( Qx, Qy, Qz )
                glFT.glEnd()
            
            # Draw main object.
            # Reset color after drawing children arrows.
            statusColor( r, g, b, a, status )
            
            centerRadius = inRad * 0.5 + outRad * 0.5
            rangeRadius = outRad - centerRadius
            stepRing = ( 360.0/rings ) * ( math.pi/180.0 )
            stepSide = ( 360.0/sides ) * ( math.pi/180.0 )
            for i in xrange( rings ):
                glFT.glBegin( OpenMayaRender.MGL_QUAD_STRIP )
                curRings = [ (stepRing*( i+0 ) ), ( stepRing*( i+1 ) ) ]
                ringSins = [ (math.sin(curRings[0])), (math.sin(curRings[1])) ]
                ringCoss = [ (math.cos(curRings[0])), (math.cos(curRings[1])) ]
                for j in xrange( sides+1 ):
                    curSide = (j % sides) * stepSide
                    sideSin = math.sin( curSide )
                    sideCos = math.cos( curSide )
                    for k in xrange( 2 ):
                        #uvX = 1.0-((1.0/rings)*(i+k))
                        #uvY = ((1.0/sides)*j)
                        if dp == 0:
                            pX = rangeRadius*sideSin
                            pY = (centerRadius+rangeRadius*sideCos)*ringCoss[k]
                            pZ = (centerRadius+rangeRadius*sideCos)*ringSins[k]
                        elif dp == 1:
                            pX = (centerRadius+rangeRadius*sideCos)*ringCoss[k]
                            pY = rangeRadius*sideSin
                            pZ = (centerRadius+rangeRadius*sideCos)*ringSins[k]
                        else:
                            pX = (centerRadius+rangeRadius*sideCos)*ringCoss[k]
                            pY = (centerRadius+rangeRadius*sideCos)*ringSins[k]
                            pZ = rangeRadius*sideSin
                        glFT.glVertex3d( 2*pX*slX+trX, 2*pY*slY+trY, 2*pZ*slZ+trZ )
                glFT.glEnd()

        def drawShaded( self ):
            # draw the faces
            glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
            glFT.glFrontFace( OpenMayaRender.MGL_CCW )
            drawObject( self )
            glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
            # draw the wireframe on top of the faces
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            glFT.glCullFace( OpenMayaRender.MGL_BACK )
  
        def drawWireframe( self ):
            # draw only the wireframe
            glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
            drawObject( self )
            
        view.beginGL()
        glFT.glPushMatrix()
        
        # change the facing of the controller
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
        
    def isBounded( self ):
        return True
  
    def drawLast( self ):
        return True
        
    def boundingBox( self ):
        # creates a bounding box for the object
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )
        
def glTorus_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glTorus() )
  
def glTorus_nodeInitializer():
    addStandardAttributes( glTorus )
    nAttr = OpenMaya.MFnNumericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
            
    glTorus.aSides = nAttr.create( 'sides', 'sides', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 8 )
    nAttr.setMin( 3 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glTorus.aRings = nAttr.create( 'rings', 'rings', OpenMaya.MFnNumericData.kInt )
    nAttr.setDefault( 8 )
    nAttr.setMin( 3 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
  
    glTorus.aOuterRadius = nAttr.create( 'outerRadius', 'orad', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(4.0)
    nAttr.setMin( 0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glTorus.aInnerRadius = nAttr.create( 'innerRadius', 'irad', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault(2.0)
    nAttr.setMin( 0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    enumAttr = OpenMaya.MFnEnumAttribute()
    glTorus.aDrawType = enumAttr.create( 'drawType', 'dt' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )
    
    glTorus.aDrawPlace = enumAttr.create( 'drawPlace', 'dp' )
    enumAttr.addField( 'x', 0 )
    enumAttr.addField( 'y', 1 )
    enumAttr.addField( 'z', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 0 )

    glTorus.targetWorldMatrix = mAttr.create( 'targetWorldMatrix', 'targetWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setKeyable( True )
    mAttr.setReadable( True )
    mAttr.setWritable( True )
    mAttr.setStorable( True )
    mAttr.setArray( True )
    
    glTorus.arrowLength = nAttr.create( 'arrowLength', 'arl', OpenMaya.MFnNumericData.kFloat )
    nAttr.setDefault( 2.0 )
    nAttr.setMin( 1.0 )
    nAttr.setKeyable( True )
    nAttr.setReadable( True )
    nAttr.setWritable( True )
    nAttr.setStorable( True )
    
    glTorus.addAttribute( glTorus.aSides )
    glTorus.addAttribute( glTorus.aRings )
    glTorus.addAttribute( glTorus.aOuterRadius )
    glTorus.addAttribute( glTorus.aInnerRadius )
    glTorus.addAttribute( glTorus.aDrawType )
    glTorus.addAttribute( glTorus.aDrawPlace )
    glTorus.addAttribute( glTorus.targetWorldMatrix )
    glTorus.addAttribute( glTorus.arrowLength )

'''
START: GL SPANNER
'''
class glSpanner( OpenMayaMPx.MPxLocatorNode ):
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
        
        sS = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'spanSource' ) )
        sT = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'spanTarget' ) )
        
        
        
        rotation = NodeUtility.getPlugValue( rt )
        color = NodeUtility.getPlugValue( cl )
        ( r, g, b ) = tuple( color )[:3]
        
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
            pass            

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
        return OpenMaya.MBoundingBox( self.bbp1, self.bbp2 )

def glSpanner_nodeCreator():
    return OpenMayaMPx.asMPxPtr( glSpanner() )
  
def glSpanner_nodeInitializer():
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    enumAttr = OpenMaya.MFnEnumAttribute()
    
    glSpanner.spanSourceMatrix = mAttr.create( 'spanSourceMatrix', 'sSM', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    
    glSpanner.spanTargetMatrix = mAttr.create( 'spanTargetMatrix', 'sTM', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    
    glSpanner.aDrawType = enumAttr.create( 'drawType', 'drawType' )
    enumAttr.addField( 'wireframe', 0 )
    enumAttr.addField( 'shaded', 1 )
    enumAttr.addField( 'normal', 2 )
    enumAttr.setHidden( False )
    enumAttr.setKeyable( True )
    enumAttr.setDefault( 2 )
    
    glSpanner.addAttribute( glSpanner.spanSourceMatrix )
    glSpanner.addAttribute( glSpanner.spanTargetMatrix )
    glSpanner.addAttribute( glSpanner.aDrawType )
    
'''    
START: COMMAND
'''
class makeGLBit( OpenMayaMPx.MPxCommand ):
    def __init__( self ):
        OpenMayaMPx.MPxCommand.__init__( self )
        self.MDagMod = OpenMaya.MDagModifier()
        self.MFnDepNode = OpenMaya.MFnDependencyNode()
        self.MDGMod = OpenMaya.MDGModifier()
        self.MFnDagNode = OpenMaya.MFnDagNode()
   
    def parseArguments( self, args ):
        # FLAGS: Setup flags.
        # An error here likely means the flag doesn't exist in the syntax.
        argData = OpenMaya.MArgDatabase( self.syntax(), args )
        
        # Type.
        if argData.isFlagSet( kShortType ) or argData.isFlagSet( kLongType ):
            self.type = argData.flagArgumentString( kShortType, 0 )
        else:
            self.type = 'glBox'
            
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
        
        # Scale.
        if argData.isFlagSet( kShortScale ) or argData.isFlagSet( kLongScale ):
            # The 0 is the index of the flag's parameter.
            self.scale = [ argData.flagArgumentDouble( kLongScale, 0 ),
                              argData.flagArgumentDouble( kLongScale, 1 ),
                              argData.flagArgumentDouble( kLongScale, 2 ) ]
        else:
            self.scale = [ 1.0, 1.0, 1.0 ]
            
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
            self.transparency = 0.8
        
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
            
    # SPHERE FLAGS.
        # Latitude.
        if argData.isFlagSet( kShortLatitude ) or argData.isFlagSet( kLongLatitude ):
            self.latitude = argData.flagArgumentInt( kShortLatitude, 0 )
        else:
            self.latitude = 4

        # Longitude.
        if argData.isFlagSet( kShortLongitude ) or argData.isFlagSet( kLongLongitude ):
            self.longitude = argData.flagArgumentInt( kShortLongitude, 0 )
        else:
            self.longitude = 6

        # Radius.
        if argData.isFlagSet( kShortRadius ) or argData.isFlagSet( kLongRadius ):
            self.radius = argData.flagArgumentDouble( kShortRadius, 0 )
        else:
            self.radius = 2.0
    # TORUS FLAGS.
        # Number of Sides.
        if argData.isFlagSet( kShortSides ) or argData.isFlagSet( kLongSides ):
            self.torusSides = argData.flagArgumentInt( kShortSides, 0 )
        else:
            self.torusSides = 4

        # Number of Rings.
        if argData.isFlagSet( kShortRings ) or argData.isFlagSet( kLongRings ):
            self.torusRings = argData.flagArgumentInt( kShortRings, 0 )
        else:
            self.torusRings = 6

        # Outer Radius.
        if argData.isFlagSet( kShortOuterRadius ) or argData.isFlagSet( kLongOuterRadius ):
            self.torusOuterRadius = argData.flagArgumentDouble( kShortOuterRadius, 0 )
        else:
            self.torusOuterRadius = 4.0

        # Inner Radius.
        if argData.isFlagSet( kShortInnerRadius ) or argData.isFlagSet( kLongInnerRadius ):
            self.torusInnerRadius = argData.flagArgumentDouble( kShortInnerRadius, 0 )
        else:
            self.torusInnerRadius = 2.0
        
        # Draw Place.
        if argData.isFlagSet( kShortDrawPlace ) or argData.isFlagSet( kLongDrawPlace ):
            self.drawPlace = argData.flagArgumentInt( kShortDrawPlace, 0 )
        else:
            self.drawPlace = 2
    # CONE FLAGS.
        # Segments.
        if argData.isFlagSet( kShortSegments ) or argData.isFlagSet( kLongSegments ):
            self.segments = argData.flagArgumentInt( kShortSegments, 0 )
        else:
            self.segments = 6
            
        # Cone Length.
        if argData.isFlagSet( kShortConeLength ) or argData.isFlagSet( kLongConeLength ):
            self.coneLength = argData.flagArgumentDouble( kShortConeLength, 0 )
        else:
            self.coneLength = 2.0
    # CYLINDER FLAGS.
        # Cylinder Length.
        if argData.isFlagSet( kShortCylinderLength ) or argData.isFlagSet( kLongCylinderLength ):
            self.cylinderLength = argData.flagArgumentDouble( kShortCylinderLength, 0 )
        else:
            self.cylinderLength = 2.0
    # SPANNER FLAGS.
        # Span Source.
        if argData.isFlagSet( kShortSpanSource ) or argData.isFlagSet( kLongSpanSource ):
            self.spanSource = argData.flagArgumentString( kShortSpanSource )
            
        # Span Target.
        if argData.isFlagSet( kShortSpanTarget ) or argData.isFlagSet( kLongSpanTarget ):
            self.spanSource = argData.flagArgumentString( kShortSpanTarget )

    def doIt( self, args ):
        # Parse the flags and arguments.
        self.parseArguments( args )
        
        # Create the controller node.
        if self.type == 'glBox':
            self.glNode = self.MDagMod.createNode( glBox_nodeName )
        elif self.type == 'glSphere':
            self.glNode = self.MDagMod.createNode( glSphere_nodeName )
        elif self.type == 'glCylinder':
            self.glNode = self.MDagMod.createNode( glCylinder_nodeName )
        elif self.type == 'glCone':
            self.glNode = self.MDagMod.createNode( glCone_nodeName )
        elif self.type == 'glTorus':
            self.glNode = self.MDagMod.createNode( glTorus_nodeName )
        elif self.type == 'glSpanner':
            self.glNode = self.MDagMod.createNode( glSpanner_nodeName )
        
        return self.redoIt()
                
    def redoIt( self ):
        # Perform the operations enqueued within our reference to MDagModifier. This effectively
        # creates the DAG nodes specified using self.dagModifier.createNode(). Node creation is 
        # done in doIt().
        self.MDagMod.doIt()
        
        # Apply the user defined arguments to the controller node.
        self.MFnDagNode.setObject( self.glNode )
        
        # Set the name.
        self.MFnDagNode.setName( self.name )
        
        #print 'redoIt > dagFn.fullPathName: {0}'.format( self.MFnDagNode.fullPathName() )
        # Return the full path name of the created node.
        self.setResult( self.MFnDagNode.fullPathName() )
        
        
        # Get the aim node's shape.
        self.MFnDepNode.setObject( self.MFnDagNode.child( 0 ) )
        
        # Update plugs with values, if any, from the command.       
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'color' ), self.color )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'localPosition' ), self.position )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'localScale' ), self.scale )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'rotate' ), self.rotation )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'transparency' ), self.transparency )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'backAlpha' ), self.backAlpha )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'lineWidth' ), self.lineWidth )
        NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'drawType' ), self.drawType )
        
        # Object type specific plugs.
        if self.type == 'glBox':
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'width' ), self.width )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'height' ), self.height )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'depth' ), self.depth )
        elif self.type == 'glSphere':
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'latitude' ), self.latitude )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'longitude' ), self.longitude )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'radius' ), self.radius )
        elif self.type == 'glCone':
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'segment' ), self.segments )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'coneLength' ), self.coneLength )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'radius' ), self.radius )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'drawPlace' ), self.drawPlace )
        elif self.type == 'glTorus':
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'sides' ), self.torusSides )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'rings' ), self.torusRings )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'outerRadius' ), self.torusOuterRadius )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'innerRadius' ), self.torusInnerRadius )
            NodeUtility.setPlugValue( self.MFnDepNode.findPlug( 'drawPlace' ), self.drawPlace )
        
        return self.MDGMod.doIt()
    
    def undoIt( self ):
        ''' Clean up anything done by the command. '''
        self.MFnDagNode.removeChild( self.glNode )
        return self.MDagMod.undoIt()
        
    def isUndoable( self ):
        return True

def cmdCreator():
    ''' Creates an instance of the command. '''
    return OpenMayaMPx.asMPxPtr( makeGLBit() )

def syntaxCreator():
    ''' Creates the arguments and flags of the command. '''
    syntax = OpenMaya.MSyntax()
    
    # FLAGS: Add flags.
    syntax.addFlag( kShortType, kLongType, OpenMaya.MSyntax.kString )
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
    # FLAGS: Sphere.
    syntax.addFlag( kShortLatitude, kLongLatitude, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortLongitude, kLongLongitude, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortRadius, kLongRadius, OpenMaya.MSyntax.kDouble )
    # FLAGS: Torus.
    syntax.addFlag( kShortSides, kLongSides, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortRings, kLongRings, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortOuterRadius, kLongOuterRadius, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortInnerRadius, kLongInnerRadius, OpenMaya.MSyntax.kDouble )
    syntax.addFlag( kShortDrawPlace, kLongDrawPlace, OpenMaya.MSyntax.kLong )
    # FLAGS: Cone.
    syntax.addFlag( kShortSegments, kLongSegments, OpenMaya.MSyntax.kLong )
    syntax.addFlag( kShortConeLength, kLongConeLength, OpenMaya.MSyntax.kDouble )
    # FLAGS: Cylinder.
    syntax.addFlag( kShortCylinderLength, kLongCylinderLength, OpenMaya.MSyntax.kDouble )
    # FLAGS: Spanner.
    syntax.addFlag( kShortSpanSource, kLongSpanSource, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortSpanTarget, kLongSpanTarget, OpenMaya.MSyntax.kString )
    
    return syntax


'''
PLUGIN INIT
'''
def initializePlugin( obj ):
    plugin = OpenMayaMPx.MFnPlugin( obj, 'Austin Baker', '1.0', 'Any' )
    try:
        plugin.registerCommand( cmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write( 'Failed to register command: {0}'.format( cmdName ) )
        raise
    try:
        plugin.registerNode( glBox_nodeName, glBox_nodeID, glBox_nodeCreator, glBox_nodeInitializer,
                             OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( glBox_nodeName ) )
        raise
    try:
        plugin.registerNode( glSphere_nodeName, glSphere_nodeID, glSphere_nodeCreator, glSphere_nodeInitializer,
                             OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( glSphere_nodeName ) )
        raise
    try:
        plugin.registerNode( glCylinder_nodeName, glCylinder_nodeID,
                             glCylinder_nodeCreator, glCylinder_nodeInitializer,
                             OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( glCylinder_nodeName ) )
        raise
    try:
        plugin.registerNode( glCone_nodeName, glCone_nodeID, glCone_nodeCreator,
                             glCone_nodeInitializer, OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( glCone_nodeName ) )
        raise
    try:
        plugin.registerNode( glTorus_nodeName, glTorus_nodeID, glTorus_nodeCreator,
                             glTorus_nodeInitializer, OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( glTorus_nodeName ) )
        raise

def uninitializePlugin( obj ):
    plugin = OpenMayaMPx.MFnPlugin( obj )
    try:
        plugin.deregisterCommand( cmdName )
    except:
        sys.stderr.write( 'Failed to deregister command: {0}'.format( cmdName ) )
        raise
    try:
        plugin.deregisterNode( glBox_nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( glBox_nodeName ) )
        raise
    try:
        plugin.deregisterNode( glSphere_nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( glSphere_nodeName ) )
        raise
    try:
        plugin.deregisterNode( glCylinder_nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( glCylinder_nodeName ) )
        raise
    try:
        plugin.deregisterNode( glCone_nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( glCone_nodeName ) )
        raise
    try:
        plugin.deregisterNode( glTorus_nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( glTorus_nodeName ) )
        raise