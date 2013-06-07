'''
Controller UI.

TODO:
1. UI for creating controller.
2. UI for saving controller.
3. UI listing saved controller setups.
'''
import sys
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import adam.utility.XMLUtility as XMLUtility
import adam.utility.TransformUtility as TransformUtility
import adam.utility.NodeUtility as NodeUtility
    
class createManipulatorUI():
    def __init__( self, winName='createManipulatorUI' ):
        self.winTitle = 'Controller Tools'
        self.winName = winName
        self.doIt()

    def doIt( self, *args ):
        # ui settings.
        self.winWidth = 306
        self.winHeight = 400
        self.iconWidth = 32
        self.iconHeight = 32
        
        # clean up old uis before opening a new one.
        try:
            cmds.deleteUI( self.winName )
        except:
            pass
        
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=False, resizeToFitChildren=False )
        cmds.frameLayout( borderVisible=False, labelVisible=False )
        
        self.conTools = cmds.columnLayout( height=self.winHeight/3 )
        cmds.text( label='Controller Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.conGrid = cmds.gridLayout( numberOfColumns=4, numberOfRows=2, cellWidthHeight=(self.winWidth/4, 50) )
        cmds.button( label='Make Control', command='cmds.rigController()' )
        cmds.button( label='Make From XML', command='XMLUtility.createControlFromXML()' )
        cmds.button( label='Apply XML', command='XMLUtility.applyXMLtoControl()' )
        cmds.button( label='Save XML', command='XMLUtility.createControlXML()' )
        cmds.button( label='Make Deformer', command='makeDeformerMesh()')
        cmds.button( label='Apply Deformer', command='applyDeformerMesh()')
        cmds.setParent( '..' )#self.conGrid
        cmds.separator( style='none', height=20 )
        cmds.text( label='Position Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.transGrid = cmds.gridLayout( numberOfColumns=3, cellWidthHeight=(self.winWidth/3, 50) )
        cmds.button( label='Match Translation', command=lambda *args: TransformUtility.matchTransforms( 'tran' ) )
        cmds.button( label='Match Rotation', command=lambda *args: TransformUtility.matchTransforms( 'rot' )  )
        cmds.button( label='Match All', command=lambda *args: TransformUtility.matchTransforms( 'all' )  )
        cmds.setParent( '..' )#self.transGrid
        cmds.setParent( '..' )#self.conTools
        
        cmds.setParent( '..' )#framelayout

         # show the ui.
        cmds.showWindow( self.winName )

def makeDeformerMesh():
    '''
    Creates a deformer mesh for the active controller.
    '''
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
                    return
        
        controlShape = controlDagNode.child( 0 )
        controlShapeDep = OpenMaya.MFnDependencyNode( controlShape )
        if controlShape.apiType() == OpenMaya.MFn.kPluginLocatorNode:
            # Get the controller OpenGL attributes.
            glPosition = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'localPosition' ) )
            #glRotation = NodeUtility.getPlugValue( NodeUtility.getPlug( controlShapeDep.name(), 'rotate' ) )
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
            meshFn.create(numVertices, numPolygons, vertexArray, polygonCounts, polygonConnects, control )
        else:
            sys.stderr.write( 'makeDeformerMesh: Wrong type of object selected.')
    else:
        sys.stderr.write( 'makeDeformerMesh: Nothing selected.' )
            
def applyDeformerMesh():
    '''
    Applies the deformer mesh to the OpenGL values of the active controller.
    '''
    selList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selList )
    if selList.length() is 1:
        control = OpenMaya.MObject()
        selList.getDependNode( 0, control )    
        controlDagNode = OpenMaya.MFnDagNode( control )
        controlShape = controlDagNode.child( 0 )
        controlShapeDep = OpenMaya.MFnDependencyNode( controlShape )
        locCheck = False
        meshCheck = False
        for c in xrange( controlDagNode.childCount() ):
            child = controlDagNode.child( c )
            if child.apiType() == OpenMaya.MFn.kPluginLocatorNode:
                locCheck = True
            elif child.apiType() == OpenMaya.MFn.kMesh:
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
                
                # Set the OpenGL points.
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
        if locCheck is False:
            sys.stderr.write( 'applyDeformerMesh: This is the wrong type of object. Needs to be an OpenGl Controller.' )
        if meshCheck is False:
            sys.stderr.write( 'applyDeformerMesh: This control object doesn\'t have a deformer mesh.' )
    elif selList.length() > 1:
        sys.stderr.write( 'applyDeformerMesh: To many things selected. Only select one controller.' )
    else:
        sys.stderr.write( 'applyDeformerMesh: Nothing selected.' )

createManipulatorUI()