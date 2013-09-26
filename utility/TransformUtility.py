import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

# ============================
# MATRIX
# ============================
def getMatrix( inNode, inMatrixType ):
    '''
    Get an object's matrix.
    
    @param inNode: String. Name of object.
    @param inMatrixType: String. "matrix", "inverseMatrix", "worldMatrix", "worldInverseMatrix",
        "parentMatrix", "parentInverseMatrix", "xformMatrix"
    @return: MMatrix of object in the space requested.
    '''
    nodeMAttr = cmds.getAttr( inNode+"."+inMatrixType )
    mMatrix = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList( nodeMAttr, mMatrix )
    return mMatrix
    
def getMatrixTranslation( inObjMatrix, inSpace ):
    '''
    Get the position from the passed in object matrix.
    
    @param inObjMatrix: MMatrix.
    @return: World space translation from MMatrix.
    '''
    # Get the transform matrix of the object.
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    # Return the translation as a vector.
    return transformMatrix.getTranslation( inSpace )

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

def getMatrixScale( inObjMatrix, inSpace ):
    '''
    Get the position from the passed in object matrix.
    
    @param inObjMatrix: MMatrix.
    @return: MVector. Scale from MMatrix.
    '''
    transformMatrix = OpenMaya.MTransformationMatrix( inObjMatrix )
    scaleDoubleArray = OpenMaya.MScriptUtil()
    scaleDoubleArray.createFromList( [1.0, 1.0, 1.0], 3 )
    scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
    transformMatrix.getScale( scaleDoubleArrayPtr, inSpace )
    
    return OpenMaya.MVector( *( scaleDoubleArray.getDoubleArrayItem( scaleDoubleArrayPtr, i ) for i in range(3) ) )

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
            childTranslation = getMatrixTranslation( targetMatrix, OpenMaya.MSpace.kWorld )
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
    
    childTranslation = getMatrixTranslation( targetMatrix, OpenMaya.MSpace.kWorld )
    MFnTrans.setTranslation( childTranslation, OpenMaya.MSpace.kWorld )
       
    childRotation = getMatrixRotation( targetMatrix, 'quat' )
    MFnTrans.setRotation( childRotation, OpenMaya.MSpace.kWorld )
    
# =======================
# MIRRORING TOOLS
# ==========================
def mirrorObjectPrompt():
    form = cmds.setParent(q=True)
    cmds.formLayout(form, e=True, width=300)

    t = cmds.text(l='Which axis to mirror across?')

    b1 = cmds.button(l='X', c='cmds.layoutDialog( dismiss="0" )' )
    b2 = cmds.button(l='Y', c='cmds.layoutDialog( dismiss="1" )' )
    b3 = cmds.button(l='Z', c='cmds.layoutDialog( dismiss="2" )' )

    spacer = 5
    top = 5
    edge = 5

    cmds.formLayout(form, edit=True,
                    attachForm=[(t, 'top', top), (t, 'left', edge), (t, 'right', edge), (b1, 'left', edge), (b3, 'right', edge)],
                    attachNone=[(t, 'bottom'), (b1, 'bottom'), (b2, 'bottom'), (b3, 'bottom')],
                    attachControl=[(b1, 'top', spacer, t), (b2, 'top', spacer, t), (b3, 'top', spacer, t)],
                    attachPosition=[(b1, 'right', spacer, 33), (b2, 'left', spacer, 33), (b2, 'right', spacer, 66), (b3, 'left', spacer, 66)])
    
def mirrorObject( inSourceObj=None, inTargetObj=None, inMirrorAxis=None ):
    # Mirrors the position and rotation of one object(source) and applies it to another (target).
    
    if inSourceObj is None or inTargetObj is None:
        # Target object should be selected first, followed by source object.
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) == 2:
            inTargetObj = selList[0]
            inSourceObj = selList[1]
        
    if inMirrorAxis is None:
        inMirrorAxis = int( cmds.layoutDialog( ui=mirrorObjectPrompt ) )
        
    if inMirrorAxis is not None:
        # Get the source module's root world matrix.
        sourceWorldMatrix = getMatrix( inSourceObj, 'worldMatrix' )
        
        # Get the source's translation vector.
        sourceWorldTranslation = getMatrixTranslation( sourceWorldMatrix, OpenMaya.MFn.kWorld )
        
        # Get the source's rotation matrix.
        sourceRotationMatrix = OpenMaya.MTransformationMatrix( sourceWorldMatrix ).asRotateMatrix()
        
        # Mirror the translation across the selected axis.
        if inMirrorAxis is 0:
            sourceWorldTranslation.x = sourceWorldTranslation.x * -1
        elif inMirrorAxis is 1:
            sourceWorldTranslation.y = sourceWorldTranslation.y * -1        
        elif inMirrorAxis is 2:
            sourceWorldTranslation.z = sourceWorldTranslation.z * -1    
    
        # Apply the mirrored position back to the target object.
        MFnTrans = OpenMaya.MFnTransform()
        targetDagPath = NodeUtility.getDagPath( inTargetObj )
        MFnTrans.setObject( targetDagPath )
        MFnTrans.setTranslation( sourceWorldTranslation, OpenMaya.MSpace.kWorld )
        
        # Mirror the rotation.
        baseVectors = {}
            
        for row in xrange( 3 ):
            # We only need the first three rows.
            rowPtr = sourceRotationMatrix[row]
            baseVectors[ row ] = []
            for col in xrange( 3 ):
                # We only need the first three columns.
                if col is not inMirrorAxis:
                    origValue = OpenMaya.MScriptUtil.getDoubleArrayItem( rowPtr, col ) * -1
                    OpenMaya.MScriptUtil.setDoubleArray( rowPtr, col, origValue )
    
        targetInverseMatrix = getMatrix( inTargetObj, 'parentInverseMatrix' )
        mirroredTarget = sourceRotationMatrix * targetInverseMatrix
        toEuler = OpenMaya.MTransformationMatrix( mirroredTarget ).eulerRotation()
        #x,y,z = map(math.degrees,(toEuler.x,toEuler.y,toEuler.z))
        #print x,y,z 
        
        MFnTrans.setRotation( toEuler )

def mirrorModule():
    # Mirrors a module.
    selList = cmds.ls( selection=True, long=True )
    if len( selList ) == 1:
        # Prompt for axis.
        mirrorAxis = int( cmds.layoutDialog( ui=mirrorObjectPrompt ) )
        
        inBitObj = selList[0]
    
        # Check if selected bit is the root.
        if NodeUtility.attributeCheck( inBitObj, 'frameRoot' ):
            # This is the root bit of the module. From here we know we can get the
            # meta node by accessing the frameRoot attribute.
            metaNode = NodeUtility.getNodeAttrDestination( inBitObj, 'frameRoot' )[0]
        else:
            # The selected bit is not the root. Run through each custom attribute
            # to find one connected to the meta node.
            attrList = cmds.listAttr( inBitObj, userDefined=True )
            for attr in attrList:
                connection = NodeUtility.getNodeAttrDestination( inBitObj, attr )
                if NodeUtility.attributeCheck( connection[0], 'metaType' ):
                    metaNode = connection[0]
                    break
                
        # Now that we have the meta node, we need the XML file name and it's location.
        metaClassPlug = NodeUtility.getPlug( metaNode, 'metaClass' )
        metaClassValue = NodeUtility.getPlugValue( metaClassPlug )
        
        metaBuildFolderPlug = NodeUtility.getPlug( metaNode, 'buildFolder' )
        metaBuildFolderValue = NodeUtility.getPlugValue( metaBuildFolderPlug )
        
        # Create the target module.
        '''
        NEED TO FIX THIS!
        targetRootBit = buildFrameModule( metaBuildFolderValue, metaClassValue )
        '''
    
        # Loop through each object in the source module.
        metaRootBit = NodeUtility.getNodeAttrSource( metaNode, 'rootBit' )[0]
        
        sourceChildBits = NodeUtility.getFrameRootAllChildren( metaRootBit )
        targetChildBits = NodeUtility.getFrameRootAllChildren( targetRootBit )
        
        sourceBits = []
        targetBits = []
        
        for i,bit in enumerate( sourceChildBits ):
            sourceBits.append( bit )
        sourceBits.insert( 0, metaRootBit )
        
        for i, bit in enumerate( targetChildBits ):
            targetBits.append( bit )
        targetBits.insert( 0, targetRootBit )
        
        for bit in xrange( len(sourceBits) ):
            # Mirror the source onto the target.
            mirrorObject( inSourceObj=sourceBits[bit], inTargetObj=targetBits[bit], inMirrorAxis=mirrorAxis )