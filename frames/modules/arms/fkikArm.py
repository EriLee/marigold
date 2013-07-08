import maya.cmds as cmds
import marigold.meta.metaNode as metaNode
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.FrameUtility as FrameUtility
import marigold.controllers.marigoldControls as marigoldControls
import marigold.skeleton.marigoldJoints as marigoldJoints

class MetaFrameFKIKArm( metaNode.MetaNode ):
    '''
    Creates a node of the MetaNode type. This node holds information about the character
    and is the top most meta node in a character hierarchy.
    '''
    def __init__( self ):
        self.inNodeMetaType = 'frameModule'
        self.inNodeName = 'metaFKIKArm'        
        super( MetaFrameFKIKArm, self ).__init__( self.inNodeName, self.inNodeMetaType )
    
    def createAttrs( self ):
        cmds.addAttr( longName='buildPriority', attributeType='byte' )
        cmds.addAttr( longName='prefix', dataType='string' )
        cmds.addAttr( longName='rootBit', dataType='string' )
        
        cmds.addAttr( longName='jShoulder', dataType='string' )
        cmds.addAttr( longName='jElbow', dataType='string' )
        cmds.addAttr( longName='jWrist', dataType='string' )
        
        cmds.addAttr( longName='fkShoulderControl', dataType='string' )
        cmds.addAttr( longName='fkShoulderControlName', dataType='string' )
        cmds.addAttr( longName='fkElbowControl', dataType='string' )
        cmds.addAttr( longName='fkElbowControlName', dataType='string' )
        
        cmds.addAttr( longName='ikRoot', dataType='string' )
        cmds.addAttr( longName='ikEnd', dataType='string' )
        cmds.addAttr( longName='ikEffControl', dataType='string' )
        cmds.addAttr( longName='ikEffControlName', dataType='string' )
        cmds.addAttr( longName='ikUpVecControl', dataType='string' )
        cmds.addAttr( longName='ikUpVecControlName', dataType='string' )

def buildModule():
    import maya.OpenMayaAnim as OpenMayaAnim
    
    # Get the frame module meta nodes in the scene.
    modules = NodeUtility.getMetaNodesInScene( 'frameModule' )
    
    # Read the meta node.
    nodeData = FrameUtility.getFrameBitSettings( modules[0] )
    prefix = nodeData['prefix'] 
    
    # Get the frame module bits.
    frameRoot = NodeUtility.getNodeAttrSource( modules[0], 'rootBit' )[0]
    shoulderBit = NodeUtility.getNodeAttrSource( modules[0], 'jShoulder' )[0]
    elbowBit = NodeUtility.getNodeAttrSource( modules[0], 'jElbow' )[0]
    wristBit = NodeUtility.getNodeAttrSource( modules[0], 'jWrist' )[0]
    ikRootBit = NodeUtility.getNodeAttrSource( modules[0], 'ikRoot' )[0]
    ikEndBit = NodeUtility.getNodeAttrSource( modules[0], 'ikEnd' )[0]
    ikUpVecBit = NodeUtility.getNodeAttrSource( modules[0], 'ikUpVecControl' )[0]
    
    # Build shadow skeleton.
    jointShoulder = marigoldJoints.createJoint( nodeData['jShoulder'], shoulderBit, inPrefix=prefix )
    jointElbow = marigoldJoints.createJoint( nodeData['jElbow'], elbowBit, jointShoulder, inPrefix=prefix )
    jointWrist = marigoldJoints.createJoint( nodeData['jWrist'], wristBit, jointElbow, inPrefix=prefix )
    
    # Make the FK rigging.
    fkControls = [ [nodeData['fkShoulderControl'], nodeData['fkShoulderControlName'], nodeData['jShoulder'], shoulderBit],
                   [nodeData['fkElbowControl'], nodeData['fkElbowControlName'], nodeData['jElbow'],elbowBit] ]
    for i in fkControls:
        # Create the spacer.
        newSpacer = marigoldControls.makeControl().createSpacer( i[3], i[1], 'j_'+prefix+'_'+i[2], True )
        # Create the controller.
        controlSplit = i[0].split( '.' )
        marigoldControls.makeControl().createController( controlSplit[0], controlSplit[1], i[1], newSpacer )
        
    # Make the IK rigging.
    effSplit = nodeData['ikEffControl'].split('.')
    effSpacer = marigoldControls.makeControl().createSpacer( ikEndBit, nodeData['ikEffControlName'], 'j_'+prefix+'_'+nodeData['jWrist'], inDoParent=False, inPrefix=prefix )
    marigoldControls.makeControl().createController( effSplit[0], effSplit[1], nodeData['ikEffControlName'], effSpacer, inPrefix=prefix )
    
    upVecSplit = nodeData['ikUpVecControl'].split('.')
    upVecSpacer = marigoldControls.makeControl().createSpacer( ikUpVecBit, nodeData['ikUpVecControlName'], ikUpVecBit, inDoParent=False, inPrefix=prefix )
    marigoldControls.makeControl().createController( upVecSplit[0], upVecSplit[1], nodeData['ikUpVecControlName'], upVecSpacer, inPrefix=prefix )
    
    jointFn = OpenMayaAnim.MFnIkJoint()

    # IK root joint.
    jointShoulder = 'j_'+prefix+'_'+nodeData['jShoulder']
    rootJointDagPath = NodeUtility.getDagPath( jointShoulder )
    
    # IK eff joint.
    jointWrist = 'j_'+prefix+'_'+nodeData['jWrist']
    effJointDagPath = NodeUtility.getDagPath( jointWrist )
    
    # Do up the solver.
    cmds.ikHandle( name=nodeData['ikEffControlName']+'_'+prefix+'_arm',
                   startJoint=rootJointDagPath.fullPathName(),
                   endEffector=effJointDagPath.fullPathName(),
                   solver='ikRPsolver' )
    cmds.parent( nodeData['ikEffControlName']+'_'+prefix+'_arm', 'ct_'+prefix+'_'+nodeData['ikEffControlName'], absolute=True )
    
    cmds.poleVectorConstraint( 'ct_'+prefix+'_'+nodeData['ikUpVecControlName'], nodeData['ikEffControlName']+'_'+prefix+'_arm' )
    
def test():
    print 'TESTING'