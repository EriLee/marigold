'''
NOTES:
1. Add priority rank to each module so the system knows what to build first.
2. Build UI needs to add one dynamically created tab for each module used. From 
    the tabs the user sets the build options. This is where things like FK/IK, 
    rotation order, etc are specified. Basically anything unique and optional 
    to the module.
3. Options
    a. Joint prefix in build settings.
'''
import sys
import math
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

#=================
def scaleRange( inValue, inOrigRange, inNewRange ):
    return ( ( inValue - inOrigRange[0] ) / ( inOrigRange[1] - inOrigRange[0] ) ) * ( inNewRange[1] - inNewRange[0] ) + inNewRange[0]

# Inputs
inX = NodeUtility.getPlug( 'multiAxisBlend1', 'inputX' )
inY = NodeUtility.getPlug( 'multiAxisBlend1', 'inputY' )

# Get values for input plugs
xValue = NodeUtility.getPlugValue( inX )
yValue = NodeUtility.getPlugValue( inY )
print 'X,Y: {0},{1}'.format( xValue, yValue )
# Blend points.
blendRowPlug = NodeUtility.getPlug( 'multiAxisBlend1', 'blendRow' )
blendRowAttr = blendRowPlug.attribute()
blendWeightPlug = NodeUtility.getPlug( 'multiAxisBlend1', 'blendWeight' )

# Out blends.
outRowPlug = NodeUtility.getPlug( 'multiAxisBlend1', 'outRow' )
outRowAttr = outRowPlug.attribute()
outWeightPlug = NodeUtility.getPlug( 'multiAxisBlend1', 'outBlendWeight' )

# For each row get the number of blend points.
numRows = outRowPlug.numElements()

gridLength = 2.0 # Both inputs range from -1 to 1. To make things easier we map this to 0.0 to 2.0
rowPoints = []

# Subtract 1 since Maya automatically adds an empty element at the end of the compound plug.
for row in range( numRows ):
    print 'ROW: {0}'.format( row )
    rowPoints.append( [] )
    outWeightPlug.selectAncestorLogicalIndex( row, outRowAttr )
    
    # Get the radius for all points in the row.
    numPoints = outWeightPlug.numElements()
    if numPoints > 1:
        tempXLoc = 0.0
        
        # The first plug will be at zero X.
        radius = gridLength / numPoints
        xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
        yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
        print 'xLoc, yLoc: {0}, {1}'.format( xLoc, yLoc )
        inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
        if inputDistance <= radius:
            perc = ( inputDistance / radius ) * 100
            rowPoints[row].append( ( 100 - perc ) / 100 )
        else:
            rowPoints[row].append( 0.0 )
        
        # Loop to get the remaining plug X locations.
        for point in xrange( numPoints - 1 ):
            xLoc = gridLength / ( numPoints - 1 )
            tempXLoc = tempXLoc + xLoc
            xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
            yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
            inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
            if inputDistance <= radius:
                perc = ( inputDistance / radius ) * 100
                rowPoints[row].append( ( 100 - perc ) / 100 )
            else:
                rowPoints[row].append( 0.0 )
    else:
        # Handle single point rows.
        radius = 1.0 # Maximum for a single point in a row.
        tempXLoc = 1.0
        xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
        yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
        inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
        if inputDistance <= radius:
            perc = ( inputDistance / radius ) * 100
            rowPoints[row].append( ( 100 - perc ) / 100 )
        else:
            rowPoints[row].append( 0.0 )

#for row in range( outRowPlug.numElements() ):
    #outWeightPlug.selectAncestorLogicalIndex( row, outRowAttr )
    for a in range( outWeightPlug.numElements() ):
        #outWeightPlug[a].setFloat( rowPoints[row][a] )
        print rowPoints[row][a]
print rowPoints
'''
# Loop through the points to check their range against the X,Y inputs.
# If they overlap then we set the blend weight for that point.
print len( rowPoints )
for p in xrange( len( rowPoints ) ):
    inputDistance = math.sqrt( ( rowPoints[p][0] - xValue )**2 + ( rowPoints[p][1] - yValue )**2 )
    print 'inputDistance: {0}'.format( inputDistance )
    
    if inputDistance <= rowPoints[p][2]:
        perc = ( inputDistance / rowPoints[p][2] ) * 100
        print ( 100 - perc ) / 100
'''

# Loop each row.
for c in range( blendRowPlug.numElements()-1 ):
    blendWeightPlug.selectAncestorLogicalIndex( c, blendRowAttr )
    for a in range( blendWeightPlug.numElements() ):
        #print blendWeightPlug[a].name()
        pass

for row in range( outRowPlug.numElements() ):
    outWeightPlug.selectAncestorLogicalIndex( row, outRowAttr )
    for a in range( outWeightPlug.numElements() ):
        #print outWeightPlug[a].name()
        #outWeightPlug[a].setFloat( 0.3 )
        #print 'out: {0}'.format( rowPoints[row][1] )
        pass

#==================

# GETS
def getBits( inModule ):
    '''
    Gets all the bits in the module and returns a list of MObjects.
    '''
    pass

def getModuleProperties( inModule ):
    '''
    Gets all the properties of a module.
    '''
    pass

# SETS
def setPosition():
    pass

def setRotation():
    pass

def setJointOrient():
    pass

def setRotationOrder():
    pass

# MAKES
def makeJoint( inBit ):
    '''
    mBit = inBit.matrix
    newJoint = joint( name=inBit.name, position=mBit.position )
    newJoint.jointOrient( mBit.orientation )
    parent( newJoint, inBit.parent )
    '''
    pass

def makeControl( inBit ):
    '''
    Makes the control for the bit.
    '''
    pass

def makeIK( inRootJoint, inRootEnd ):
    '''
    Creates IK chain between the inRootJoint and inRootEnd.
    '''
    pass

def getBoxPoints():
    '''
    retrieves a meshes vertices.
    '''
    selList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selList )
    if selList.length() is 1:
        control = OpenMaya.MObject()
        selList.getDependNode( 0, control )    
        controlDagNode = OpenMaya.MFnDagNode( control )
        for c in xrange( controlDagNode.childCount() ):
            child = controlDagNode.child( c )
            if child.apiType() == OpenMaya.MFn.kMesh:
                deformMesh = OpenMaya.MFnMesh( child )
                print deformMesh
                vertexCount = OpenMaya.MIntArray()    
                vertexList = OpenMaya.MIntArray()
                deformMesh.getVertices( vertexCount, vertexList )
                print vertexCount
                print vertexList
                
                vertexArray = OpenMaya.MFloatPointArray()
                deformMesh.getPoints( vertexArray, OpenMaya.MSpace.kObject )
                print vertexArray
                for p in xrange( vertexArray.length() ):
                    print p
                    print vertexArray[p].x, vertexArray[p].y, vertexArray[p].z
                    
# SCRIBBLE
def createCube( inParent ):
    '''
    creates a mesh cube.
    '''
    cubeSize = 0.5
    numPolygons = 6
    numVertices = 8
    numPolygonConnects = 4 * numPolygons
    
    # Floating point array listing the XYZ for each vertex in the cube.
    vertexArray = OpenMaya.MFloatPointArray()
    vertexArray.setLength( numVertices )
    vertexArray.set( OpenMaya.MFloatPoint( -cubeSize, -cubeSize, -cubeSize ), 0 )#bottomBackRight
    vertexArray.set( OpenMaya.MFloatPoint( cubeSize+0.5, -cubeSize, -cubeSize ), 1 )#bottomBackLeft
    vertexArray.set( OpenMaya.MFloatPoint( cubeSize, -cubeSize,  cubeSize ), 2 )#bottomFrontLeft
    vertexArray.set( OpenMaya.MFloatPoint( -cubeSize, -cubeSize,  cubeSize ), 3 )#bottomFrontRight
    vertexArray.set( OpenMaya.MFloatPoint( -cubeSize,  cubeSize, -cubeSize ), 4 )#topBackRight
    vertexArray.set( OpenMaya.MFloatPoint( -cubeSize,  cubeSize,  cubeSize ), 5 )#topFrontRight
    vertexArray.set( OpenMaya.MFloatPoint( cubeSize,  cubeSize,  cubeSize ), 6 )#topFrontLeft
    vertexArray.set( OpenMaya.MFloatPoint( cubeSize,  cubeSize, -cubeSize ), 7 )#topBackLeft
    
    # Int array listing the number of vertices for each face. In this case there are
    # 4 vertices per face and a total of 6 faces.
    polygonCounts = OpenMaya.MIntArray()
    polygonCounts.setLength( numPolygons )
    polygonCounts.set( 4, 0 )
    polygonCounts.set( 4, 1 )
    polygonCounts.set( 4, 2 )
    polygonCounts.set( 4, 3 )
    polygonCounts.set( 4, 4 )
    polygonCounts.set( 4, 5 )

    # Int array listing the vertices for every face.
    # The first number is the vertex index from vertexArray.
    polygonConnects = OpenMaya.MIntArray()
    polygonConnects.setLength( numPolygonConnects )
    # Bottom face. -Y.
    polygonConnects.set(0, 0)
    polygonConnects.set(1, 1)
    polygonConnects.set(2, 2)
    polygonConnects.set(3, 3)
    #  Top face. +Y.
    polygonConnects.set(4, 4)
    polygonConnects.set(5, 5)
    polygonConnects.set(6, 6)
    polygonConnects.set(7, 7)
    # Front face. +Z.
    polygonConnects.set(3, 8)
    polygonConnects.set(2, 9)
    polygonConnects.set(6, 10)
    polygonConnects.set(5, 11)
    # Right face. -X.
    polygonConnects.set(0, 12)
    polygonConnects.set(3, 13)
    polygonConnects.set(5, 14)
    polygonConnects.set(4, 15)
    # Back Face. -Z.
    polygonConnects.set(0, 16)
    polygonConnects.set(4, 17)
    polygonConnects.set(7, 18)
    polygonConnects.set(1, 19)
    # Left face. +X.
    polygonConnects.set(1, 20)
    polygonConnects.set(7, 21)
    polygonConnects.set(6, 22)
    polygonConnects.set(2, 23)

    meshFn = OpenMaya.MFnMesh()
    meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, inParent )      


def getDeformMesh():
    # Get the current user selection.
    selList = OpenMaya.MSelectionList() 
    OpenMaya.MGlobal.getActiveSelectionList( selList )
    if selList.length() is 1:
        control = OpenMaya.MObject()
        selList.getDependNode( 0, control )    
        controlDagNode = OpenMaya.MFnDagNode( control )
        
        # Check if the selected control already has a deformer mesh.
        if controlDagNode.childCount() > 1:
            for c in xrange( controlDagNode.childCount() ):
                if controlDagNode.child( c ).apiType() == OpenMaya.MFn.kMesh:
                    print 'The selected controller has a deformer mesh already.'
                    pass
        
        controlShape = controlDagNode.child( 0 )
        controlShapeDep = OpenMaya.MFnDependencyNode( controlShape )
        if controlShape.apiType() == OpenMaya.MFn.kPluginLocatorNode:
            # Get the controller OpenGL attributes.
            glPosition = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'localPosition' ) )
            glRotation = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'rotate' ) )
            glWidth = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'width' ) )
            glHeight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'height' ) )
            glDepth = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'depth' ) )
            glBottomBackRight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botBackRight' ) )
            glBottomBackLeft = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botBackLeft' ) )
            glBottomFrontLeft = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botFrontLeft' ) )
            glBottomFrontRight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botFrontRight' ) )
            glTopBackRight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topBackRight' ) )
            glTopFrontRight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topFrontRight' ) )
            glTopFrontLeft = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topFrontLeft' ) )
            glTopBackLeft = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topBackLeft' ) )
            
            # Mesh cube attributes.
            numPolygons = 6
            numVertices = 8
            numPolygonConnects = 4 * numPolygons
            
            # Floating point array listing the XYZ for each vertex in the cube.
            # Add in the Width/Height/Depth values and the offset translation.
            vertexArray = OpenMaya.MFloatPointArray()
            vertexArray.setLength( numVertices )
            vertexArray.set( OpenMaya.MFloatPoint( ( -glWidth/2+glBottomBackRight[0] ) + glPosition[0],
                                                   ( -glHeight/2+glBottomBackRight[1] ) + glPosition[1],
                                                   ( -glDepth/2+glBottomBackRight[2] ) + glPosition[2] ), 0 )#bottomBackRight
            vertexArray.set( OpenMaya.MFloatPoint( ( glWidth/2+glBottomBackLeft[0] ) + glPosition[0],
                                                   ( -glHeight/2+glBottomBackLeft[1] ) + glPosition[1],
                                                   ( -glDepth/2+glBottomBackLeft[2] ) + glPosition[2] ), 1 )#bottomBackLeft
            vertexArray.set( OpenMaya.MFloatPoint( ( glWidth/2 + glBottomFrontLeft[0] ) + glPosition[0],
                                                   ( -glHeight/2+glBottomFrontLeft[1] ) + glPosition[1],
                                                   ( glDepth/2+glBottomFrontLeft[2] ) + glPosition[2] ), 2 )#bottomFrontLeft
            vertexArray.set( OpenMaya.MFloatPoint( ( -glWidth/2 + glBottomFrontRight[0] ) + glPosition[0],
                                                   ( -glHeight/2+glBottomFrontRight[1] ) + glPosition[1],
                                                   ( glDepth/2+glBottomFrontRight[2] ) + glPosition[2] ), 3 )#bottomFrontRight
            vertexArray.set( OpenMaya.MFloatPoint( ( -glWidth/2+glTopBackRight[0] ) + glPosition[0],
                                                   ( glHeight/2+glTopBackRight[1] ) + glPosition[1],
                                                   ( -glDepth/2+glTopBackRight[2] ) + glPosition[2] ), 4 )#topBackRight
            vertexArray.set( OpenMaya.MFloatPoint( ( -glWidth/2 + glTopFrontRight[0] ) + glPosition[0],
                                                   ( glHeight/2 + glTopFrontRight[1] ) + glPosition[1],
                                                   ( glDepth/2 + glTopFrontRight[2] ) + glPosition[2] ), 5 )#topFrontRight
            vertexArray.set( OpenMaya.MFloatPoint( ( glWidth/2 + glTopFrontLeft[0] ) + glPosition[0],
                                                   ( glHeight/2+glTopFrontLeft[1] ) + glPosition[1],
                                                   ( glDepth/2+glTopFrontLeft[2] ) + glPosition[2] ), 6 )#topFrontLeft
            vertexArray.set( OpenMaya.MFloatPoint( ( glWidth/2+glTopBackLeft[0] ) + glPosition[0],
                                                   ( glHeight/2+glTopBackLeft[1] ) + glPosition[1],
                                                   ( -glDepth/2+glTopBackLeft[2] ) + glPosition[2] ), 7 )#topBackLeft
            
            # Int array listing the number of vertices for each face. In this case there are
            # 4 vertices per face and a total of 6 faces.
            polygonCounts = OpenMaya.MIntArray()
            polygonCounts.setLength( numPolygons )
            polygonCounts.set( 4, 0 )
            polygonCounts.set( 4, 1 )
            polygonCounts.set( 4, 2 )
            polygonCounts.set( 4, 3 )
            polygonCounts.set( 4, 4 )
            polygonCounts.set( 4, 5 )
        
            # Int array listing the vertices for every face.
            # The first number is the vertex index from vertexArray.
            polygonConnects = OpenMaya.MIntArray()
            polygonConnects.setLength( numPolygonConnects )
            # Bottom face. -Y.
            polygonConnects.set(0, 0)
            polygonConnects.set(1, 1)
            polygonConnects.set(2, 2)
            polygonConnects.set(3, 3)
            #  Top face. +Y.
            polygonConnects.set(4, 4)
            polygonConnects.set(5, 5)
            polygonConnects.set(6, 6)
            polygonConnects.set(7, 7)
            # Front face. +Z.
            polygonConnects.set(3, 8)
            polygonConnects.set(2, 9)
            polygonConnects.set(6, 10)
            polygonConnects.set(5, 11)
            # Right face. -X.
            polygonConnects.set(0, 12)
            polygonConnects.set(3, 13)
            polygonConnects.set(5, 14)
            polygonConnects.set(4, 15)
            # Back Face. -Z.
            polygonConnects.set(0, 16)
            polygonConnects.set(4, 17)
            polygonConnects.set(7, 18)
            polygonConnects.set(1, 19)
            # Left face. +X.
            polygonConnects.set(1, 20)
            polygonConnects.set(7, 21)
            polygonConnects.set(6, 22)
            polygonConnects.set(2, 23)
        
            # Make the mesh cube.
            meshFn = OpenMaya.MFnMesh()
            newMesh = meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, control )
            
def setDeformMesh():
    selList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selList )
    if selList.length() is 1:
        control = OpenMaya.MObject()
        selList.getDependNode( 0, control )    
        controlDagNode = OpenMaya.MFnDagNode( control )
        controlShape = controlDagNode.child( 0 )
        controlShapeDep = OpenMaya.MFnDependencyNode( controlShape )
        meshCheck = False
        for c in xrange( controlDagNode.childCount() ):
            child = controlDagNode.child( c )
            if child.apiType() == OpenMaya.MFn.kMesh:
                # Set the check to True.
                meshCheck = True
                # Grab the mesh.
                deformMesh = OpenMaya.MFnMesh( child )
                
                # Grab the vertices of the mesh.
                vertexCount = OpenMaya.MIntArray()    
                vertexList = OpenMaya.MIntArray()
                vertexArray = OpenMaya.MFloatPointArray()
                deformMesh.getVertices( vertexCount, vertexList )
                deformMesh.getPoints( vertexArray, OpenMaya.MSpace.kObject )
                
                # Set the opengl points.
                glPosition = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'localPosition' ) )
                glWidth = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'width' ) )
                glHeight = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'height' ) )
                glDepth = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'depth' ) )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botBackRight' ), [ (vertexArray[0].x-(-glWidth/2))-glPosition[0],(vertexArray[0].y-(-glHeight/2))-glPosition[1],(vertexArray[0].z-(-glDepth/2))-glPosition[2] ]  )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botBackLeft' ), [ (vertexArray[1].x-(glWidth/2))-glPosition[0],(vertexArray[1].y-(-glHeight/2))-glPosition[1],(vertexArray[1].z-(-glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botFrontLeft' ), [ (vertexArray[2].x-(glWidth/2))-glPosition[0],(vertexArray[2].y-(-glHeight/2))-glPosition[1],(vertexArray[2].z-(glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'botFrontRight' ), [ (vertexArray[3].x-(-glWidth/2))-glPosition[0],(vertexArray[3].y-(-glHeight/2))-glPosition[1],(vertexArray[3].z-(glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topBackRight' ), [ (vertexArray[4].x-(-glWidth/2))-glPosition[0],(vertexArray[4].y-(glHeight/2))-glPosition[1],(vertexArray[4].z-(-glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topFrontRight' ), [ (vertexArray[5].x-(-glWidth/2))-glPosition[0],(vertexArray[5].y-(glHeight/2))-glPosition[1],(vertexArray[5].z-(glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topFrontLeft' ), [ (vertexArray[6].x-(glWidth/2))-glPosition[0],(vertexArray[6].y-(glHeight/2))-glPosition[1],(vertexArray[6].z-(glDepth/2))-glPosition[2] ] )
                NodeUtility.setPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'topBackLeft' ), [ (vertexArray[7].x-(glWidth/2))-glPosition[0],(vertexArray[7].y-(glHeight/2))-glPosition[1],(vertexArray[7].z-(-glDepth/2))-glPosition[2] ] )
                
                # Clean up by deleting the mesh.
                MDGMod = OpenMaya.MDGModifier()
                MDGMod.deleteNode( child )
                MDGMod.doIt()
        if meshCheck is False:
            sys.stderr.write( 'This control object doesn\'t have a deformer mesh.' )