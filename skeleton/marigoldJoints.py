import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import marigold.utility.TransformUtility as TransformUtility

def createJoint( inJointName, inJointRef, inJointParent=None, inJointRadius=4.0, inPrefix=None ):
    '''
    Creates a single joint.
    
    @param inBit: String. Name of the frame bit.
    @param inParent: MObject. Parent MObject for the new joint.
    @return: The MObject of the joint created.
    '''
    # Create the joint.
    dagMod = OpenMaya.MDagModifier()
    if inJointParent:
        newJoint = dagMod.createNode( 'joint', inJointParent )
    else:
        newJoint = dagMod.createNode( 'joint' )
    dagMod.doIt()
        
    # Name the joint.
    if inPrefix is None:
        jointName = 'j_'+inJointName
    else:
        jointName = inPrefix+'_'+inJointName
    depFn = OpenMaya.MFnDependencyNode( newJoint )
    depFn.setName( jointName )
        
    # Modify the joint.
    jointFn = OpenMayaAnim.MFnIkJoint()
    jointFn.setObject( newJoint )
    
    parentDepNode = OpenMaya.MFnDependencyNode( jointFn.parent( 0 ) )
    bitLocalMatrix = TransformUtility.getMatrix( inJointRef, 'matrix' )
    bitWorldMatrix = TransformUtility.getMatrix( inJointRef, 'worldMatrix' )
    
    # Set orientation.
    if parentDepNode.name() == 'world':
        print 'set world euler'
        bitEuler = TransformUtility.getMatrixRotation( bitWorldMatrix, 'euler' )
        jointFn.setOrientation( bitEuler )
    else:
        print 'set local euler'
        bitEuler = TransformUtility.getMatrixRotation( bitLocalMatrix, 'euler' )                
        jointFn.setOrientation( bitEuler )
    
    # Set position.
    bitWorldTranslationVector = TransformUtility.getMatrixTranslation( bitWorldMatrix )
    if parentDepNode.name() == 'world':
        # If the joint's parent is the world, then we take the translation vector straight
        # from the frame bit's world matrix.
        jointVector = bitWorldTranslationVector
    else:
        # If the joint's parent is another joint, then we need to get the parent's world
        # matrix and use it as a change of basis for the frame bit's world matrix.
        parentMatrix = TransformUtility.getMatrix( parentDepNode.name(), 'worldMatrix' )
        basisMatrix = bitWorldMatrix * parentMatrix.inverse()            
        jointVector = TransformUtility.getMatrixTranslation( basisMatrix )
    jointFn.setTranslation( jointVector, OpenMaya.MSpace.kTransform )
    
    # Set rotation order.
    # TODO
    
    # Set rotation.
    #if parentDepNode.name() == 'world':
        #print 'set world euler'
        #bitEuler = TransformUtility.getMatrixRotation( bitWorldMatrix, 'euler' )
        #jointFn.setRotation( bitEuler )
    #else:
        #print 'set local euler'
        #bitEuler = TransformUtility.getMatrixRotation( bitLocalMatrix, 'euler' )                
        #jointFn.setRotation( bitEuler )
    
    # Set preferred angle.
    # TODO
    
    # Set joint radius.
    cmds.setAttr( jointName+'.radius', inJointRadius )
    
    return newJoint