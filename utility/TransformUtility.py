import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

# ============================
# MATRIX
# ============================
def getMatrix( inNode, inMatrixType ):
    '''
    @param inNode: String. Name of object.
    @param inMatrixType: String. "matrix", "inverseMatrix", "worldMatrix", "worldInverseMatrix",
        "parentMatrix", "parentInverseMatrix", "xformMatrix"
    @return: MMatrix of object in the space requested.
    '''
    nodeMAttr = cmds.getAttr( inNode+"."+inMatrixType )
    mMatrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList( nodeMAttr, mMatrix )
    return mMatrix
    
def getMatrixTranslation( inObjMatrix ):
    '''
    Get the position from the passed in object matrix.
    @param inObjMatrix: MMatrix.
    @return: World space translation from MMatrix.
    '''
    # Get the transform matrix of the object.
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    # Return the translation as a vector.
    return transformMatrix.getTranslation( OpenMaya.MSpace.kWorld )

def getMatrixRotation( inObjMatrix, inType ):
    '''
    Takes an object's matrix and a rotation type and return the rotation.
    @param inObjMatrix: MMatrix.
    @param inType: String. Type of rotation, 'euler' or 'quat'
    @return: Rotation from MMatrix
    '''
    # Get the transform matrix of the object.
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    if inType == 'eulerVector':
        return transformMatrix.eulerRotation().asVector()
    elif inType == 'euler':
        return transformMatrix.eulerRotation()
    elif inType == 'quat':
        return transformMatrix.rotation()

# ============================
# MATCH TRANSFORMS
# Matches the transforms of one object to another. Can be rotation only, translation only or both.
# ============================
def matchTransforms( inType ):
    '''
    @param inType: String. Type of matching to perform. 'tran', 'rot', or 'all'
    '''
    selObjs = cmds.ls( selection=True, dag=False, ap=True )
    
    if len( selObjs ) == 0:
        cmds.warning( 'No objects are selected. Select two objects and try again' )
    elif len( selObjs ) > 2:
        cmds.warning( 'To many objects are selected. Select only two objects and try again' )
    else:
        # first object is child, second object is target
        cObj = selObjs[0]
        tObj = selObjs[1]
        
        # do the matching of child to target
        MFnTrans = OpenMaya.MFnTransform()
        childDagPath = NodeUtility.getDagPath( cObj )
        MFnTrans.setObject( childDagPath )
        targetMatrix = getMatrix( tObj, 'worldMatrix' )
        if inType == 'tran' or inType == 'all':
            childTranslation = getMatrixTranslation( targetMatrix )
            MFnTrans.setTranslation( childTranslation, OpenMaya.MSpace.kWorld )
        if inType == 'rot' or inType == 'all':            
            childRotation = getMatrixRotation( targetMatrix, 'quat' )
            MFnTrans.setRotation( childRotation, OpenMaya.MSpace.kWorld )
            
def matchObjectTransforms( src, cld ):
    '''
    Matches the child's translation and rotation to the source object.
    
    @param src: String. Name of the source transform object.
    @param cld: String. Name of the child object.
    '''
    # do the matching of child to target
    MFnTrans = OpenMaya.MFnTransform()
    childDagPath = NodeUtility.getDagPath( cld )
    MFnTrans.setObject( childDagPath )
    targetMatrix = getMatrix( src, 'worldMatrix' )
    
    childTranslation = getMatrixTranslation( targetMatrix )
    MFnTrans.setTranslation( childTranslation, OpenMaya.MSpace.kWorld )
       
    childRotation = getMatrixRotation( targetMatrix, 'quat' )
    MFnTrans.setRotation( childRotation, OpenMaya.MSpace.kWorld )