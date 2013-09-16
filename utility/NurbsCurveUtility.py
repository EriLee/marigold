import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

def createCurve( inName, inPoints, inDegree=1, inForm=False, inOffset=[0,0,0], inScale=1 ):
    '''
    @param inName: String. Name of the curve to be created.
    @param inPoints: List of list. Points of the control vertices of the curve.
    @param inDegree: Int. Degree of the curve. 1, 2, 3, 5, 7
    @param inForm: Int. Open or closed curve. 1 for closed, 2 for open.
    @param inOffset: List. Offset for each axis of the curve.
    @return: MObject. Nurbs curve.
    '''
    controlVerts = OpenMaya.MPointArray()
    
    if inForm:
        form = OpenMaya.MFnNurbsCurve.kClosed
    else:
        form = OpenMaya.MFnNurbsCurve.kOpen
        
    create2D = False
    rational = False
    parent = None
    
    # Create the points for the curve.
    for point in inPoints:
        controlVerts.append( OpenMaya.MPoint( (point[0]*inScale)+inOffset[0], (point[1]*inScale)+inOffset[1], (point[2]*inScale)+inOffset[2] ) )
    
    # Make the curve.
    curveFn = OpenMaya.MFnNurbsCurve()
    node = curveFn.createWithEditPoints( controlVerts, inDegree, form, create2D, rational, parent )    
    
    # Set the curve's name.
    MFnDagNode = OpenMaya.MFnDagNode()
    MFnDagNode.setObject( node )
    MFnDagNode.setName( inName )
    
    return node

def createCurveCircle( inName, inNormal=[0,1,0], inRadius=1 ):
    '''
    @param inName: String. Name of curve circle.
    @param inNormal: List. Direction the curve faces.
    @param inRadius: Int. Radius of the circle.
    @return. MObject. Curve circle.
    '''
    node = cmds.circle( name=inName, normal=inNormal, radius=inRadius)
    return NodeUtility.getDependNode( node[0] )

def createCompoundCurve( inCurves ):
    '''
    Merges all the controls into one transform node.
    
    @param inCurves: List of Strings. Names of curves to combine under one transform node.
                        The first curve in the list is considered the parent of all the others.
    @return: MObject. Compound curve transform node.
    '''
    # List for creating the compound.
    compoundList = []
    
    # Get the nurbs curves of all curves in the list.
    for index in range( 1, len(inCurves) ):
        curve = NodeUtility.getDagPath( inCurves[index] )  
        for child in xrange( curve.childCount() ):
            nurb = curve.child( child )
            nurbDagPath = OpenMaya.MDagPath.getAPathTo( nurb )
            if nurb.apiType() == OpenMaya.MFn.kNurbsCurve:
                compoundList.append( nurbDagPath.fullPathName() )
                
    # Add the transform of the parent curve. This is the first curve passed into
    # the function.
    parent = NodeUtility.getDagPath( inCurves[0] )
    compoundList.append( parent.fullPathName() )
    
    # Now parent the shapes to the first curve's transform node.
    cmds.parent( compoundList, shape=True, relative=True )
    
    # Delete the remaining transform nodes of the other curves.
    for index in range( 1, len(inCurves) ):
        cmds.delete( inCurves[index] )
        
    # Returns a MObject.
    return NodeUtility.getDependNode( parent.fullPathName() )

def getCurveCvs( inCurve ):
    '''
    Retrieves the positions for all CVs on the curve.
    
    @param inCurve: String. Name of the curve from which to retrieve CV positions.
    @return: List of Dicts. Each dict holds the information for one nurbs curve. since
                there could be multiple curves for one object we build a list of each curve.
    '''
    curDag = NodeUtility.getDagPath( inCurve )
    curFn = OpenMaya.MFnNurbsCurve()
    curCvs = OpenMaya.MPointArray()
    
    storedCvs = []
    childShapes = curDag.childCount()
    for child in xrange( childShapes ):
        childObj = curDag.child( child )
        #if childObj.apiType() == OpenMaya.MFn.kNurbsCurve:
        tempCvs = {}
        curFn.setObject( childObj )
        curFn.getCVs( curCvs )
        for cv in xrange( curCvs.length() ):
            tempCvs[cv] = [curCvs[cv].x, curCvs[cv].y, curCvs[cv].z]
        storedCvs.append( tempCvs )

    return storedCvs

def buildCVPointArray( inCVList ):
    '''
    Builds a MPointArray from the passed in CV value list.
    
    @param inCVList: List of Dicts. Each dict holds the information for one nurbs curve. since
                there could be multiple curves for one object we build a list of each curve.
    @return: List of MPointArrays.
    '''
    curList = []
    for cvDict in inCVList:
        curCvs = OpenMaya.MPointArray()
        for index in cvDict:
            curCvs.append( OpenMaya.MPoint( cvDict[index][0], cvDict[index][1], cvDict[index][2] ) )
        curList.append( curCvs )
    return curList

def setCurveCvs( inCurve, inCVArray ):
    '''
    Sets a curves CVs to the values from inCVArray.
    
    @param inCurve: String. Name of curve to update.
    @param inCVArray: List of MPointArrays.
    '''
    curDag = NodeUtility.getDagPath( inCurve )
    curFn = OpenMaya.MFnNurbsCurve()

    childShapes = curDag.childCount()
    for child in xrange( childShapes ):
        childObj = curDag.child( child )
        curFn.setObject( childObj )
        curFn.setCVs( inCVArray[child] )
        curFn.updateCurve()

def addCurveValues( inObj, inPoints ):
    '''
    Add curve CV attributes to an object.
    
    @param inObj: String. Name of object to add curve cv values too.
    @param inPoints: List of curves and their cv points. 
    '''
    print 'inObj: {0}'.format( inObj )
    print 'inPoints: {0}'.format( inPoints )
    # Naming convention: curve + curve# + CV + cv# + axis    
    for index in xrange( len(inPoints) ):
        # Create a compound attribute to hold the curves.
        curveName = 'curve{0}'.format( index )
        curDict = inPoints[index]
        numOfCvs = len( curDict )
        
        cmds.addAttr( inObj, longName=curveName, numberOfChildren=numOfCvs, attributeType='compound', category='nurbCurve' )
        
        for cv in curDict:
            cvPoint = curDict[cv]
            cvName = '{0}CV{1}'.format( curveName, cv )
            print 'cvPoint: {0}'.format( cvPoint )
            print 'cvName: {0}'.format( cvName )
            cmds.addAttr( inObj, longName=cvName, attributeType='float3', parent=curveName )
            cmds.addAttr( inObj, longName='{0}x'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[0] )
            cmds.addAttr( inObj, longName='{0}y'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[1] )
            cmds.addAttr( inObj, longName='{0}z'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[2] )
            
def writeCurveValues( inObj, inPoints ):
    '''
    Write curve CV values to an object. Object must already have curve CV attributes.
    If it does not then add them with addCurveValues()
    
    @param inObj: String. Name of object to add curve cv values too.
    @param inPoints: List of curves and their cv points. 
    '''
    for index in xrange( len(inPoints) ):
        curveName = 'curve{0}'.format( index )
        curDict = inPoints[index]
        
        for cv in curDict:
            cvPoint = curDict[cv]
            cvName = '{0}CV{1}'.format( curveName, cv )
            attrX = '{0}x'.format(cvName)
            attrY = '{0}y'.format(cvName)
            attrZ = '{0}z'.format(cvName)
            
            cmds.setAttr( '{0}.{1}'.format( inObj, attrX ), cvPoint[0] )
            cmds.setAttr( '{0}.{1}'.format( inObj, attrY ), cvPoint[1] )
            cmds.setAttr( '{0}.{1}'.format( inObj, attrZ ), cvPoint[2] )

def readCurveValues( inObj ):
    '''
    Read stored curve CV values on an object. Object must have curve CV attributes
    created with addCurveValues().
    
    @param inObj: String. Name of object to add curve cv values too.
    '''
    curveAttrs = cmds.listAttr( inObj, string='curve*', category='nurbCurve' )
    
    # [cur, cur, ...]
    # cur[i] = { #:[x,y,z] }
    curList = []
    for attr in curveAttrs:
        plug = NodeUtility.getPlug( inObj, attr )
        plugValue = NodeUtility.getPlugValue( plug )
        
        cvDict = {}
        for index,point in enumerate( plugValue ):
            cvDict[index] = point
        curList.append( cvDict )

    curList
    return curList