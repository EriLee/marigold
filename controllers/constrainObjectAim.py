'''
Plug-in: Aim Constraint
Author: Austin Baker
Date Started: May 2013

*ABOUT*
Creates an aim constraint. Requires a target object and an up object.

*SAMPLE USAGE*
import maya.cmds as cmds
cmds.loadPlugin( 'constrainObjectAim.py' )
cmds.aimConstraintSetup( co='constrained object name', ao='aim object name', uo='up object name' )
    
*COMMAND FLAGS*
    Constraint transform name: -n, -name 
    Object to be constrained: -co, -conObject
    Object to aim at: -ao, -aimObject
    Object to be up vector: -uo, -upObject
    Maintain constrained object's rotation offset: -mo, -maintainOffset NOTE: THIS DOES NOTHING AT THE MOMENT
    
*TODO*
    Maintain offset for constrained object upon creation of node
'''
import sys, math
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMayaRender as OpenMayaRender
import maya.OpenMayaUI as OpenMayaUI

glRenderer = OpenMayaRender.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

# Aim Node variables.
nodeName = 'aimConstraintNode'
nodeID = OpenMaya.MTypeId( 0x1234A )

# Command flags.
cmdName = 'aimConstraintSetup'
kShortConstraintName = '-n'
kLongConstraintName = '-name'
kShortConstrainedObject = '-co'
kLongConstrainedObject = '-conObject'
kShortAimObject = '-ao'
kLongAimObject = '-aimObject'
kShortUpObject = '-uo'
kLongUpObject = '-upObject'
kShortMaintainOffset = '-mo'
kLongMaintainOffset = '-maintainOffset'

# ==
# NODE CLASS
class aimConstraintNode( OpenMayaMPx.MPxLocatorNode ):
    # Statics for node attributes
    conObjMatrix = OpenMaya.MObject()
    aimObjMatrix = OpenMaya.MObject()
    upObjMatrix = OpenMaya.MObject()
    constraintAxes = OpenMaya.MObject()
    rotationOffset = OpenMaya.MObject()
    outputRotation = OpenMaya.MObject()
    
    def __init__( self ):
        OpenMayaMPx.MPxLocatorNode.__init__( self )
        self.conObjWorldVector = OpenMaya.MVector()
        self.aimObjWorldVector = OpenMaya.MVector()
        self.upObjWorldVector = OpenMaya.MVector()
        self.upVector = OpenMaya.MVector()
        self.eulerRot = OpenMaya.MVector()
        self.rotationOffset = OpenMaya.MVector()
        
    def compute( self, plug, dataBlock ):
        if plug == aimConstraintNode.outputRotation:
            # CONNECTIONS DATA
            conObjMatrixData = dataBlock.inputValue( aimConstraintNode.constraintWorldMatrix )
            conObjParentMatrixData = dataBlock.inputValue( aimConstraintNode.constraintParentMatrix )
            aimObjMatrixData = dataBlock.inputValue( aimConstraintNode.aimObjMatrix )        
            upObjMatrixData = dataBlock.inputValue( aimConstraintNode.upObjMatrix )
            constraintAxesData = dataBlock.inputValue( aimConstraintNode.constraintAxes )
            jointOrientData = dataBlock.inputValue( aimConstraintNode.constraintJointOrient )
            #rotationOffsetData = dataBlock.inputValue( aimConstraintNode.rotationOffset )
            outRotation = dataBlock.outputValue( aimConstraintNode.outputRotation )
            # Get the data by type.
            self.conObjMatrixValue = conObjMatrixData.asMatrix()
            self.conObjParentMatrixValue = conObjParentMatrixData.asMatrix()
            self.aimObjMatrixValue = aimObjMatrixData.asMatrix()
            self.upObjMatrixValue = upObjMatrixData.asMatrix()
            self.jointOrientValue = jointOrientData.asVector()
            self.constraintAxesValue = constraintAxesData.asShort()
            #rotationOffsetValue = rotationOffsetData.asVector()
         
            # AIM VECTOR: ( target - camera )
            # Get the aim vector by subtracting the world position of the aim object from
            # the world position of the constrained object.
            self.conObjWorldVector = getMatrixTranslation( self.conObjMatrixValue )
            self.aimObjWorldVector = getMatrixTranslation( self.aimObjMatrixValue )
            aimVector = self.aimObjWorldVector - self.conObjWorldVector
            aimVector.normalize()
            
            # UP VECTOR: ( up 'cross' target )
            # Making sure this sucker is orthogonal.
            self.upObjWorldVector = getMatrixTranslation( self.upObjMatrixValue )
            self.upVector = self.upObjWorldVector - self.conObjWorldVector
            upDot = aimVector * self.upVector
            self.upVector = self.upVector - aimVector * upDot    
            self.upVector.normalize()
    
            # SIDE VECTOR: ( right 'cross' camera )
            # Get the cross product of the aim and up vectors. 
            sideVector = aimVector ^ self.upVector
            sideVector.normalize()
            
            # ROTATION
            # Handle any axes switching
            order = {}
            order[0] = [ 0, 1, 2 ]#'XYZ' good
            order[1] = [ 1, 0, 2 ]#'YXZ' good
            order[2] = [ 2, 0, 1 ]#'ZXY' good
            order[3] = [ 0, 2, 1 ]#'XZY' reversed, flip Z
            order[4] = [ 1, 2, 0 ]#'YZX' good
            order[5] = [ 2, 1, 0 ]#'ZYX' reversed, flip Z
            # Create a zero matrix.
            # Set the rows to the calculated vectors.
            aimMatrix = OpenMaya.MMatrix()
            setRow( aimMatrix, order[ self.constraintAxesValue ][ 0 ], aimVector )#X
            setRow( aimMatrix, order[ self.constraintAxesValue ][ 1 ], self.upVector )#Y
            setRow( aimMatrix, order[ self.constraintAxesValue ][ 2 ], sideVector )#Z
            
            # Parent - Get the rotation of the parent and add it into the calculation.
            matrixTrans = OpenMaya.MTransformationMatrix( aimMatrix )
            parentOffset = getMatrixRotation( self.conObjParentMatrixValue.inverse(), 'quat' )
            matrixTrans.addRotationQuaternion( parentOffset.x, parentOffset.y, parentOffset.z, parentOffset.w, OpenMaya.MSpace.kTransform )
            
            # Joint - Handle joint orientation if the constrained is in fact a joint.
            jointOrient = OpenMaya.MVector( self.jointOrientValue.x, self.jointOrientValue.y, self.jointOrientValue.z )
            rotateOrder = OpenMaya.MTransformationMatrix().kXYZ
            eulerJointOrientMatrix = OpenMaya.MEulerRotation( jointOrient, rotateOrder ).asMatrix()
            jointOffset = getMatrixRotation( eulerJointOrientMatrix.inverse(), 'quat' )            
            matrixTrans.addRotationQuaternion( jointOffset.x, jointOffset.y, jointOffset.z, jointOffset.w, OpenMaya.MSpace.kTransform )
            self.eulerRot = matrixTrans.eulerRotation()
            
            # Set output plug
            outRotation.set3Double( self.eulerRot.x, self.eulerRot.y, self.eulerRot.z )
            
            dataBlock.setClean( plug )
        else:
            return OpenMaya.kUnknownParameter
        
    def draw( self, view, path, style, status ):
        # Get the value of the debug draw attribute on the constraint node.
        socketNode = OpenMaya.MFnDependencyNode( self.thisMObject() )
        debug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'debugDraw' ) ).asInt()
        axisChange = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'constraintAxes' ) ).asShort()
        
        if debug == True:
            # Change of basis of the aim vector to constrained object's space.
            aimVectorConSpace = self.aimObjMatrixValue * self.conObjMatrixValue.inverse()
            aimVectorTrans = getMatrixTranslation( aimVectorConSpace )
            # Change of basis of the up vector to constrained object's space.
            upVectorConSpace = self.upObjMatrixValue * self.conObjMatrixValue.inverse()
            upVectorTrans = getMatrixTranslation( upVectorConSpace )
            
            # Project the up vector onto the plane of the constrained object. The disc!
            # Dict that lists the direction of the plane upvector. This is used for drawing the fin.
            order = {}
            order[0] = [ 0, 1, 0 ]#'XYZ'
            order[1] = [ 1, 0, 0 ]#'YXZ'
            order[2] = [ 1, 0, 0 ]#'ZXY'
            order[3] = [ 0, 0, 1 ]#'XZY'
            order[4] = [ 0, 0, 1 ]#'YZX'
            order[5] = [ 0, 1, 0 ]#'ZYX'
            conUp = OpenMaya.MVector( order[ self.constraintAxesValue ][ 0 ], order[ self.constraintAxesValue ][ 1 ], order[ self.constraintAxesValue ][ 2 ] )
            conUpDot = upVectorTrans * conUp
            conUpProjection = conUp*conUpDot
            planeUpVector = conUpProjection
            
            def drawLine( self ):
                # Draws a line between the constrained object and the aim object.
                glFT.glColor4f( 1.0, 0.2, 0.0, 0.25 )
                glFT.glBegin( OpenMayaRender.MGL_LINES)
                glFT.glVertex3f( aimVectorTrans.x, aimVectorTrans.y, aimVectorTrans.z )
                glFT.glVertex3f( 0, 0, 0 )
                glFT.glEnd()
            
            def drawFin( self ):
                # Draws a triangle between the constrained object, up object and the up circle.
                glFT.glColor4f( 1.0, 0.2, 0.0, 0.25 )
                # Draw the front side.
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLES )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( upVectorTrans.x, upVectorTrans.y, upVectorTrans.z )
                glFT.glVertex3f( planeUpVector.x, planeUpVector.y, planeUpVector.z )          
                glFT.glEnd()
                # Draw the front side.
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLES )
                glFT.glVertex3f( 0.0, 0.0, 0.0 )
                glFT.glVertex3f( planeUpVector.x, planeUpVector.y, planeUpVector.z )
                glFT.glVertex3f( upVectorTrans.x, upVectorTrans.y, upVectorTrans.z )            
                glFT.glEnd()
                
            def drawCircle( self ):
                segments = 20
                ang = float( 360 )/float( segments )
                planeRadius = planeUpVector.length()
                glFT.glColor4f( 1.0, 0.6, 0.0, 0.25 )                
                # Draw the front side.
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_FAN )
                for i in xrange( segments ):
                    x = math.cos( math.radians( ang*float( i ) ) )
                    y = math.sin( math.radians( ang*float( i ) ) )
                    x1= math.cos( math.radians( ang*float( i+1 ) ) )
                    y1= math.sin( math.radians( ang*float( i+1 ) ) )
                    # 0, 3 -- YZ plane
                    if self.constraintAxesValue == 0 or self.constraintAxesValue == 3: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( 0.0, x*planeRadius, y*planeRadius )
                        glFT.glVertex3f( 0.0, x1*planeRadius, y1*planeRadius )
                    # 1, 4 -- XZ plane
                    if self.constraintAxesValue == 1 or self.constraintAxesValue == 4: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( x*planeRadius, 0.0, y*planeRadius )
                        glFT.glVertex3f( x1*planeRadius, 0.0, y1*planeRadius )
                    # 2, 5 -- XY plane
                    if self.constraintAxesValue == 2 or self.constraintAxesValue == 5: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( x*planeRadius, y*planeRadius, 0.0 )
                        glFT.glVertex3f( x1*planeRadius, y1*planeRadius, 0.0 )
                glFT.glEnd()
                # Draw the back side.
                glFT.glBegin( OpenMayaRender.MGL_TRIANGLE_FAN )
                for i in xrange( segments ):
                    x = math.cos( math.radians( ang*float( i ) ) )
                    y = math.sin( math.radians( ang*float( i ) ) )
                    x1= math.cos( math.radians( ang*float( i+1 ) ) )
                    y1= math.sin( math.radians( ang*float( i+1 ) ) )
                    # 0, 3 -- YZ plane
                    if self.constraintAxesValue == 0 or self.constraintAxesValue == 3: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( 0.0, x1*planeRadius, y1*planeRadius )
                        glFT.glVertex3f( 0.0, x*planeRadius, y*planeRadius )
                    # 1, 4 -- XZ plane
                    if self.constraintAxesValue == 1 or self.constraintAxesValue == 4: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( x1*planeRadius, 0.0, y1*planeRadius )
                        glFT.glVertex3f( x*planeRadius, 0.0, y*planeRadius )
                    # 2, 5 -- XY plane
                    if self.constraintAxesValue == 2 or self.constraintAxesValue == 5: 
                        glFT.glVertex3f( 0.0, 0.0, 0.0 )
                        glFT.glVertex3f( x1*planeRadius, y1*planeRadius, 0.0 )
                        glFT.glVertex3f( x*planeRadius, y*planeRadius, 0.0 )
                glFT.glEnd()
    
            def drawShaded( self ):
                # Draw the faces.
                glFT.glEnable( OpenMayaRender.MGL_CULL_FACE )
                glFT.glFrontFace( OpenMayaRender.MGL_CCW )
                glFT.glLineWidth( 6.0 )
                drawLine( self )
                glFT.glLineWidth( 1.0 )
                drawFin( self )
                drawCircle( self )
                glFT.glDisable( OpenMayaRender.MGL_CULL_FACE )
                # Draw the wireframe on top of the faces.
                glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
                drawLine( self )
                drawFin( self )
                drawCircle( self )
                glFT.glCullFace( OpenMayaRender.MGL_BACK )
                 
            def drawWireframe( self ):
                # Draw only the wireframe.
                glFT.glPolygonMode( OpenMayaRender.MGL_FRONT_AND_BACK, OpenMayaRender.MGL_LINE )
                glFT.glLineWidth( 1.0 )
                drawLine( self )
                drawFin( self )
                drawCircle( self )    
            
            def drawText( self, string, vec ):
                halfV = vec * 0.5            
                # Draw the text string.
                glFT.glColor4f( 1.0, 0.2, 0.0, 1.0 )
                textPoint = OpenMaya.MPoint( halfV.x, halfV.y, halfV.z)
                view.drawText( string, textPoint )
            
            # Setup for the drawing.
            view.beginGL()
            glFT.glPushMatrix()
            glFT.glPushAttrib( OpenMayaRender.MGL_ALL_ATTRIB_BITS )
            
            # Handle switching between wireframe and shaded.
            f = drawShaded
            if style not in [ OpenMayaUI.M3dView.kFlatShaded, OpenMayaUI.M3dView.kGouraudShaded ]: f = drawWireframe
            
            glFT.glClearDepth( 1.0 )
            glFT.glEnable( OpenMayaRender.MGL_BLEND )
            glFT.glEnable( OpenMayaRender.MGL_DEPTH_TEST )
            glFT.glDepthFunc( OpenMayaRender.MGL_LEQUAL )
            glFT.glShadeModel( OpenMayaRender.MGL_SMOOTH )
            glFT.glBlendFunc( OpenMayaRender.MGL_SRC_ALPHA, OpenMayaRender.MGL_ONE_MINUS_SRC_ALPHA )
            glFT.glDepthMask( OpenMayaRender.MGL_FALSE )
            
            # Draw the objects.
            f( self )
            
            drawText( self, 'UP', upVectorTrans )
            drawText( self, 'AIM', aimVectorTrans )
            
            glFT.glPopAttrib()
            glFT.glPopMatrix()
            view.endGL()
        
# ==
# HELPER FUNCTIONS
def getMatrixTranslation( inObjMatrix ):
    ''' Get the position from the passed in object matrix. '''
    # Get the transform matrix of the object.
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    # Return the translation as a vector.
    return transformMatrix.getTranslation( OpenMaya.MSpace.kWorld )

def getMatrixRotation( inObjMatrix, inType ):
    ''' takes an object's matrix and a rotation type and return the rotation. '''
    # Get the transform matrix of the object.
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    if inType == 'euler':
        return transformMatrix.eulerRotation().asVector()
    elif inType == 'quat':
        return transformMatrix.rotation()
    
def setRow( matrix, row, newRow ):
    ''' Sets a row in a matrix with new data. '''
    for c,v in enumerate( newRow ):
        # Sets the column 'c' of row 'row' to value 'v.'
        OpenMaya.MScriptUtil.setDoubleArray( matrix[row], c, v )
    
# ==
# COMMAND
class aimCmd( OpenMayaMPx.MPxCommand ):
    def __init__( self ):
        ''' Command constructor. '''
        OpenMayaMPx.MPxCommand.__init__( self )
        self.MDagMod = OpenMaya.MDagModifier()
        self.MFnDepNode = OpenMaya.MFnDependencyNode()
        self.MDGMod = OpenMaya.MDGModifier()
        self.MFnDagNode = OpenMaya.MFnDagNode()

    def parseArguments( self, args ):
        ''' Get the argument data. '''
        argData = OpenMaya.MArgParser( self.syntax(), args )
        # FLAGS: Setup flags.
        if argData.isFlagSet( kShortConstraintName ) or argData.isFlagSet( kLongConstraintName ):
            # The 0 is the index of the flag's parameter.
            self.newNodeName = argData.flagArgumentString( kShortConstraintName, 0 )
        else:
            self.newNodeName = 'aimConstraint'
        # Constrained object flag
        if argData.isFlagSet( kShortConstrainedObject ) or argData.isFlagSet( kLongConstrainedObject ):
            self.conObjStr = argData.flagArgumentString( kShortConstrainedObject, 0 )
        else:
            OpenMaya.MGlobal.displayError( 'You need to provide a constrained object.' )
        # Aim object flag
        if argData.isFlagSet( kShortAimObject ) or argData.isFlagSet( kLongAimObject ):
            self.aimStr = argData.flagArgumentString( kShortAimObject, 0 )
        else:
            OpenMaya.MGlobal.displayError( 'You need to provide an aim object.' )
        # Up vector object flag
        if argData.isFlagSet( kShortUpObject ) or argData.isFlagSet( kLongUpObject ):
            self.upStr = argData.flagArgumentString( kShortUpObject, 0 )
        else:
            OpenMaya.MGlobal.displayError( 'You need to provide an up object.' )
        # Maintain offset flag.
        if argData.isFlagSet( kShortMaintainOffset ) or argData.isFlagSet( kLongMaintainOffset ):
            self.maintainOffset = argData.flagArgumentBool( kShortMaintainOffset, 0 )
        else:
            self.maintainOffset = False

    def doIt( self, args ):
        ''' Setup the command. '''
        # Parse the flags and arguments.
        self.parseArguments( args )
        
        # Create the aim node.
        self.aimNode = self.MDagMod.createNode( nodeName )
        self.redoIt()
                
    def redoIt( self ):
        ''' Do the actual work of the command. '''
        # Perform the operations enqueued within our reference to MDagModifier. This effectively
        # creates the DAG nodes specified using self.dagModifier.createNode(). Node creation is 
        # done in doIt().
        self.MDagMod.doIt()
        
        # Get the depend node for each of the objects connected to the aim node. 
        conObject = OpenMaya.MObject()
        aimObject = OpenMaya.MObject()
        upObject = OpenMaya.MObject()
        # Build a selection list of the objects. 
        selList = OpenMaya.MSelectionList()
        selList.add( self.conObjStr )
        selList.add( self.aimStr )
        selList.add( self.upStr )
        # Use the list to get the dependency node's for each object. These are assigned
        # to the previously created MObjects.
        selList.getDependNode( 0, conObject )
        selList.getDependNode( 1, aimObject )
        selList.getDependNode( 2, upObject )
        
        # PLUGS: AIM NODE
        self.MFnDagNode.setObject( self.aimNode )
        # Change the name of the aimNode's transform to the passed in flag. If no flag was
        # set then use the default name.
        self.MFnDagNode.setName( self.newNodeName )
        # Get the aim node's shape.
        shapeObject = self.MFnDagNode.child( 0 )
        self.MFnDepNode.setObject( shapeObject )
        # Grab the desired plugs.
        constraintWorldMatrix_NodePlug = self.MFnDepNode.findPlug( 'constraintWorldMatrix' )
        constraintParentMatrix_NodePlug = self.MFnDepNode.findPlug( 'constraintParentMatrix' )
        constraintRotPivot_NodePlug = self.MFnDepNode.findPlug( 'constraintRotPivot' )
        
        aimObjMatrix_NodePlug = self.MFnDepNode.findPlug( 'aimObjMatrix' )
        upObjMatrix_NodePlug = self.MFnDepNode.findPlug( 'upObjMatrix' )
        conObjJointOrient_NodePlug = self.MFnDepNode.findPlug( 'jointOrient' )
        outRotation_NodePlug = self.MFnDepNode.findPlug( 'outRotation' )  
        conObjOffsetRotationX_Plug = self.MFnDepNode.findPlug( 'rotationOffsetX' )
        conObjOffsetRotationY_Plug = self.MFnDepNode.findPlug( 'rotationOffsetY' )
        conObjOffsetRotationZ_Plug = self.MFnDepNode.findPlug( 'rotationOffsetZ' )
        
        # Parent the aimNode under the constrained object's transform.
        self.MFnDagNode.setObject( conObject )
        self.MFnDagNode.addChild( self.aimNode, 0, False )
        
        # PLUGS: CONSTRAINED OBJECT
        self.MFnDepNode.setObject( conObject )
        # Parent matrix is an array plug. As such we need to get the plug by it's 
        # physical index.
        conObjWorldMatrix_Plug = self.MFnDepNode.findPlug( 'worldMatrix' )
        conObjWorldMatrix_Plug.setNumElements( 1 )
        conObjWorldMatrix_Plug.evaluateNumElements()
        conObjWorldMatrix_PlugIndex = conObjWorldMatrix_Plug.elementByPhysicalIndex( 0 )
        
        conObjParentMatrix_Plug = self.MFnDepNode.findPlug( 'parentMatrix' )
        conObjParentMatrix_Plug.setNumElements( 1 )
        conObjParentMatrix_Plug.evaluateNumElements()
        conObjParentMatrix_PlugIndex = conObjParentMatrix_Plug.elementByPhysicalIndex( 0 )
        
        conObjRotatePivot_Plug = self.MFnDepNode.findPlug( 'rotatePivot' )
        
        # Get the constrained object's rotation. this will take the resulting aim rotation. 
        conObjRotationPlug = self.MFnDepNode.findPlug( 'rotate' )
        
        # PLUGS: Aim Object
        self.MFnDepNode.setObject( aimObject )   
        aimObjWorldMatrix_Plug = self.MFnDepNode.findPlug( 'worldMatrix' )
        aimObjWorldMatrix_Plug.setNumElements( 1 )
        aimObjWorldMatrix_Plug.evaluateNumElements()
        aimObjWorldMatrix_PlugIndex = aimObjWorldMatrix_Plug.elementByPhysicalIndex( 0 )
        
        # PLUGS: Up Object
        self.MFnDepNode.setObject( upObject )   
        upObjWorldMatrix_Plug = self.MFnDepNode.findPlug( 'worldMatrix' )
        upObjWorldMatrix_Plug.setNumElements( 1 )
        upObjWorldMatrix_Plug.evaluateNumElements()
        upObjWorldMatrix_PlugIndex = upObjWorldMatrix_Plug.elementByPhysicalIndex( 0 )
        
        # JOINT: Handle joint orientation should the constrained object be a joint.
        if conObject.apiType() == OpenMaya.MFn.kJoint:
            self.MFnDepNode.setObject( conObject )
            conObjJointOrient_Plug = self.MFnDepNode.findPlug( 'jointOrient' )
            self.MDGMod.connect( conObjJointOrient_Plug, conObjJointOrient_NodePlug )        
        
        # CONNECTIONS: Hook up the plugs between nodes.
        self.MDGMod.connect( conObjWorldMatrix_PlugIndex, constraintWorldMatrix_NodePlug )
        self.MDGMod.connect( conObjParentMatrix_PlugIndex, constraintParentMatrix_NodePlug )
        self.MDGMod.connect( conObjRotatePivot_Plug, constraintRotPivot_NodePlug )
        self.MDGMod.connect( outRotation_NodePlug, conObjRotationPlug )
        self.MDGMod.connect( aimObjWorldMatrix_PlugIndex, aimObjMatrix_NodePlug )
        self.MDGMod.connect( upObjWorldMatrix_PlugIndex, upObjMatrix_NodePlug )
        
        # OFFSET: Get the constrained object's original rotation.
        # NOTE: THIS IS NOT CURRENTLY HOOKED UP!!! 
        if self.maintainOffset:
            # Get the transform of the constrained object.
            conObjTrans = OpenMaya.MFnTransform( conObject )
            # Get the original matrix.
            conObjOriginalMatrix = conObjTrans.transformation().asMatrix()
            # Get the rotation from the matrix.
            originalRotation = OpenMaya.MTransformationMatrix( conObjOriginalMatrix ).eulerRotation()
            # Assign it to the plugs
            self.MDGMod.newPlugValueDouble( conObjOffsetRotationX_Plug, originalRotation.x )
            self.MDGMod.newPlugValueDouble( conObjOffsetRotationY_Plug, originalRotation.y )
            self.MDGMod.newPlugValueDouble( conObjOffsetRotationZ_Plug, originalRotation.z )
        
        self.MDGMod.doIt()
    
    def undoIt( self ):
        ''' Clean up anything done by the command. '''
        self.MFnDagNode.removeChild( self.aimNode )
        self.MDagMod.undoIt()
        
    def isUndoable( self ):
        return True

'''
PLUG-IN INITIALIZATION.
'''
# INITIALIZE COMMAND
def cmdCreator():
    ''' Creates an instance of the command. '''
    return OpenMayaMPx.asMPxPtr( aimCmd() )

def syntaxCreator():
    ''' Creates the arguments and flags of the command. '''
    syntax = OpenMaya.MSyntax()
    
    # FLAGS: Add flags.
    syntax.addFlag( kShortConstraintName, kLongConstraintName, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortConstrainedObject, kLongConstrainedObject, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortAimObject, kLongAimObject, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortUpObject, kLongUpObject, OpenMaya.MSyntax.kString )
    syntax.addFlag( kShortMaintainOffset, kLongMaintainOffset, OpenMaya.MSyntax.kString )

    return syntax

def nodeCreator():
    ''' Aim Constraint Node Creator. '''
    return OpenMayaMPx.asMPxPtr( aimConstraintNode() )

# INITIALIZE NODE
def nodeInitializer():
    ''' Aim Constraint Node Initializer. '''
    # Declare MFNs
    nAttr = OpenMaya.MFnNumericAttribute()
    eAttr = OpenMaya.MFnEnumAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()
    
    # INPUT: Constrained object matrix and parent matrix. These are needed to get the object's world matrix.
    aimConstraintNode.constraintWorldMatrix = mAttr.create( 'constraintWorldMatrix', 'constraintWorldMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    aimConstraintNode.constraintParentMatrix = mAttr.create( 'constraintParentMatrix', 'constraintParentMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    
    aimConstraintNode.constraintRotPivot = nAttr.create( 'constraintRotPivot', 'constraintRotPivot', OpenMaya.MFnNumericData.k3Double )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    
    aimConstraintNode.rotationOffsetX = uAttr.create( 'rotationOffsetX', 'rotationOffsetX', OpenMaya.MFnUnitAttribute.kAngle,0)
    aimConstraintNode.rotationOffsetY = uAttr.create( 'rotationOffsetY', 'rotationOffsetY', OpenMaya.MFnUnitAttribute.kAngle,0)
    aimConstraintNode.rotationOffsetZ = uAttr.create( 'rotationOffsetZ', 'rotationOffsetZ', OpenMaya.MFnUnitAttribute.kAngle,0)
    aimConstraintNode.rotationOffset = nAttr.create( 'rotationOffset', 'rotationOffset', aimConstraintNode.rotationOffsetX, aimConstraintNode.rotationOffsetY, aimConstraintNode.rotationOffsetZ )
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
    
    aimConstraintNode.jointOrientX = uAttr.create( 'jointOrientX', 'jointOrientX', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.jointOrientY = uAttr.create( 'jointOrientY', 'jointOrientY', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.jointOrientZ = uAttr.create( 'jointOrientZ', 'jointOrientZ', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.constraintJointOrient = nAttr.create( 'jointOrient', 'jointOrient', aimConstraintNode.jointOrientX, aimConstraintNode.jointOrientY, aimConstraintNode.jointOrientZ )
    nAttr.setStorable(True)
    nAttr.setWritable(True)
    nAttr.setChannelBox(True)
        
    aimConstraintNode.addAttribute( aimConstraintNode.constraintWorldMatrix )
    aimConstraintNode.addAttribute( aimConstraintNode.constraintParentMatrix )
    aimConstraintNode.addAttribute( aimConstraintNode.constraintRotPivot )
    aimConstraintNode.addAttribute( aimConstraintNode.rotationOffset )
    aimConstraintNode.addAttribute( aimConstraintNode.constraintJointOrient )
    
    # INPUT: Aim object's matrix and parent matrix. These are needed to get the object's world matrix.
    aimConstraintNode.aimObjMatrix = mAttr.create( 'aimObjMatrix', 'aimObjMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    aimConstraintNode.aimObjParentMatrix = mAttr.create( 'aimObjParentMatrix', 'aimObjParentMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    aimConstraintNode.addAttribute( aimConstraintNode.aimObjMatrix )
    aimConstraintNode.addAttribute( aimConstraintNode.aimObjParentMatrix )
    
    # INPUT: Up object's matrix and parent matrix. These are needed to get the object's world matrix.
    aimConstraintNode.upObjMatrix = mAttr.create( 'upObjMatrix', 'upObjMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    aimConstraintNode.upObjParentMatrix = mAttr.create( 'upObjParentMatrix', 'upObjParentMatrix', OpenMaya.MFnMatrixAttribute.kDouble )
    mAttr.setHidden( True )
    mAttr.setStorable( False )
    aimConstraintNode.addAttribute( aimConstraintNode.upObjMatrix )
    aimConstraintNode.addAttribute( aimConstraintNode.upObjParentMatrix )
        
    # INPUT: User specified AIM/UP axes. Defaults to 'ZY'
    aimConstraintNode.constraintAxes = eAttr.create('constraintAxes','constraintAxes') 
    eAttr.addField('XY', 0 )
    eAttr.addField('YX', 1 )
    eAttr.addField('ZX', 2 )
    eAttr.addField('XZ', 3 )
    eAttr.addField('YZ', 4 )
    eAttr.addField('ZY', 5 )
    eAttr.setReadable( True )
    eAttr.setWritable( True )
    eAttr.setStorable( True )
    eAttr.setHidden( False )
    eAttr.setChannelBox( True )
    eAttr.setDefault( 0 )
    aimConstraintNode.addAttribute( aimConstraintNode.constraintAxes )
    
    # INPUT: Toggle debug drawing.
    aimConstraintNode.debugDraw = nAttr.create( 'debugDraw', 'debugDraw', OpenMaya.MFnNumericData.kBoolean, False )
    nAttr.setHidden( False )
    nAttr.setKeyable( 1 )
    aimConstraintNode.addAttribute( aimConstraintNode.debugDraw )
    
    # OUTPUT: Output of the aim constraint node.
    aimConstraintNode.outRotationX = uAttr.create( 'outRotationX', 'outRotationX', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.outRotationY = uAttr.create( 'outRotationY', 'outRotationY', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.outRotationZ = uAttr.create( 'outRotationZ', 'outRotationZ', OpenMaya.MFnUnitAttribute.kAngle, 0 )
    aimConstraintNode.outputRotation = nAttr.create( 'outRotation', 'outRotation', aimConstraintNode.outRotationX, aimConstraintNode.outRotationY, aimConstraintNode.outRotationZ )
    aimConstraintNode.addAttribute( aimConstraintNode.outputRotation )
    
    # Setup node attribute dependencies.
    aimConstraintNode.attributeAffects( aimConstraintNode.constraintWorldMatrix, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.constraintParentMatrix, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.constraintAxes, aimConstraintNode.outputRotation )
    
    aimConstraintNode.attributeAffects( aimConstraintNode.constraintRotPivot, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.rotationOffset, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.constraintJointOrient, aimConstraintNode.outputRotation )
    
    aimConstraintNode.attributeAffects( aimConstraintNode.aimObjMatrix, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.aimObjParentMatrix, aimConstraintNode.outputRotation )
    
    aimConstraintNode.attributeAffects( aimConstraintNode.upObjMatrix, aimConstraintNode.outputRotation )
    aimConstraintNode.attributeAffects( aimConstraintNode.upObjParentMatrix, aimConstraintNode.outputRotation )
      
    print 'Finished node initializer'  
    
def initializePlugin( obj ):
    ''' Initialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj, 'Austin Baker', '1.0', 'Any' )
    # Aim constraint command.
    try:
        plugin.registerCommand( cmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write( 'Failed to register command: {0}'.format( cmdName ) )
        raise
    # Aim constraint node.
    try:
        plugin.registerNode( nodeName, nodeID, nodeCreator, nodeInitializer, OpenMayaMPx.MPxNode.kLocatorNode )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( nodeName ) )
        raise

def uninitializePlugin( obj ):
    ''' Uninitialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj )
    # Aim constraint command.
    try:
        plugin.deregisterCommand( cmdName )
    except:
        sys.stderr.write( 'Failed to deregister command: {0}'.format( cmdName ) )
        raise
    # Aim constraint node.
    try:
        plugin.deregisterNode( nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( nodeName ) )
        raise