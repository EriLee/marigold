import maya.cmds as cmds
import maya.OpenMayaAnim as OpenMayaAnim
import marigold.meta.metaNode as metaNode
import marigold.controllers.marigoldControls as marigoldControls
import marigold.skeleton.marigoldJoints as marigoldJoints
import marigold.utility.NodeUtility as NodeUtility

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
        cmds.setAttr( '{0}.metaClass'.format( self.node ), 'fkikArm', type='string', lock=True )
        
        cmds.addAttr( longName='buildFolder', dataType='string')
        cmds.setAttr( '{0}.buildFolder'.format( self.node ), 'arms', type='string', lock=True )
        
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
    '''
    Build function for all the rigging associated with this module.
    '''
    # Get the frame module meta nodes in the scene.
    modules = NodeUtility.getMetaNodesInScene( 'frameModule' )
    
    # Read the meta node.
    nodeData = NodeUtility.getFrameBitSettings( modules[0] )
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
        spacerName = 'j_{0}_{1}'.format( prefix, i[2] )
        newSpacer = marigoldControls.makeControl().createSpacer( i[3], i[1], spacerName, True )
        
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
    jointShoulder = 'j_{0}_{1}'.format( prefix, nodeData['jShoulder'] )
    rootJointDagPath = NodeUtility.getDagPath( jointShoulder )
    
    # IK eff joint.
    jointWrist = 'j_{0}_{1}'.format( prefix, nodeData['jWrist'] ) 
    effJointDagPath = NodeUtility.getDagPath( jointWrist )
    
    # Do up the solver.
    ikHandleName = '{0}_{1}_arm'.format( nodeData['ikEffControlName'], prefix )
    cmds.ikHandle( name=ikHandleName,
                   startJoint=rootJointDagPath.fullPathName(),
                   endEffector=effJointDagPath.fullPathName(),
                   solver='ikRPsolver' )
    
    effControlName = 'ct_{0}_{1}'.format( prefix, nodeData['ikEffControlName'] ) 
    cmds.parent( ikHandleName, effControlName, absolute=True )
    
    upVecControlName = 'ct_{0}_{1}'.format( prefix, nodeData['ikUpVecControlName'] )
    cmds.poleVectorConstraint( upVecControlName, ikHandleName )