from math import degrees
import maya.OpenMaya as OpenMaya
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.NodeUtility as NodeUtility

def storeControlTransforms( sourceObj, targetObj ):
    '''
    Store control transform data.
    
    @param sourceObj: String. Name of object to pull data from.
    @param targetObj: String. Name of object to store data on.
    '''    
    sourceMatrix = TransformUtility.getMatrix( sourceObj, 'matrix' )
    
    # Store the position
    targetPosPlug = NodeUtility.getPlug( targetObj, 'controlPosition' )
    sourceTranslation = TransformUtility.getMatrixTranslation( sourceMatrix, OpenMaya.MSpace.kTransform )
    pos = [ sourceTranslation.x, sourceTranslation.y, sourceTranslation.z ]
    NodeUtility.setPlugValue( targetPosPlug, pos )
    
    # Store the rotation
    targetRotPlug = NodeUtility.getPlug( targetObj, 'controlRotation' )
    sourceRotation = TransformUtility.getMatrixRotation( sourceMatrix, 'euler' )
    #rot = [ degrees(angle) for angle in (sourceRotation.x, sourceRotation.y, sourceRotation.z) ]
    rot = [ sourceRotation.x, sourceRotation.y, sourceRotation.z ]
    NodeUtility.setPlugValue( targetRotPlug, rot )
    
    # Store the scale.
    targetSclPlug = NodeUtility.getPlug( targetObj, 'controlScale' )
    sourceScale = TransformUtility.getMatrixScale( sourceMatrix, OpenMaya.MSpace.kTransform )
    scl = [ sourceScale.x, sourceScale.y, sourceScale.z ]
    NodeUtility.setPlugValue( targetSclPlug, scl )

def applyStoredTransforms( sourceObj, targetObj ):
    '''
    Applies stored transform data for a control object.
    
    @param sourceObj: String. Name of object to pull data from.
    @param targetObj: String. Name of object to apply data to.
    '''
    print 'applyStoredTransforms @@@@@@'
    print 'sourceObj: {0}'.format( sourceObj )
    print 'targetObj: {0}'.format( targetObj )
    
    MFnTrans = OpenMaya.MFnTransform()
    targetDagPath = NodeUtility.getDagPath( targetObj )
    MFnTrans.setObject( targetDagPath )
    
    sourcePosPlug = NodeUtility.getPlug( sourceObj, 'controlPosition' )
    sourcePosValue = NodeUtility.getPlugValue( sourcePosPlug )
    sourcePos = OpenMaya.MVector( sourcePosValue[0], sourcePosValue[1], sourcePosValue[2] )
    MFnTrans.setTranslation( sourcePos, OpenMaya.MSpace.kTransform )
    
    sourceRotPlug = NodeUtility.getPlug( sourceObj, 'controlRotation' )
    sourceRotValue = NodeUtility.getPlugValue( sourceRotPlug )
    sourceRot = OpenMaya.MEulerRotation( sourceRotValue[0], sourceRotValue[1], sourceRotValue[2] ) 
    MFnTrans.setRotation( sourceRot )
    
    sourceSclPlug = NodeUtility.getPlug( sourceObj, 'controlScale' )
    sourceSclValue = NodeUtility.getPlugValue( sourceSclPlug )
    scaleDoubleArray = OpenMaya.MScriptUtil()
    scaleDoubleArray.createFromList( [sourceSclValue[0], sourceSclValue[1], sourceSclValue[2]], 3 )
    scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
    MFnTrans.setScale( scaleDoubleArrayPtr )