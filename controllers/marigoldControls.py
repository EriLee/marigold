import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.NodeUtility as NodeUtility
import marigold.controllers.glBox as glBox

class makeControl():
    def __init__( self ):
        # Do stuff
        pass
        
    def createSpacer( self, inBitName, inGroupName='newGroup', inTargetObject=None, inDoParent=False, inPrefix=None ):
        '''
        Creates an empty group. Optionally, the group's transforms can be matched to
        another object.
        
        @param inGroupName: String. Name to give the new group.
        @param inTargetObject: String. Name of object to match the group's transforms
        to.
        @return: The newly created group.
        '''
        # Create empty group.
        if inPrefix is not None:
            groupName = 'sp_'+inPrefix+'_'+inGroupName
        else:
            groupName = 'sp_'+inGroupName
            
        newGroup = cmds.group( em=True, name=groupName )
    
        # Set its transforms.
        if inTargetObject is not None:
            # Get target objects matrix.
            targetMatrix = TransformUtility.getMatrix( inTargetObject, 'worldMatrix' )
            
            # Get groups transform.
            MFnTrans = OpenMaya.MFnTransform()
            groupDagPath = NodeUtility.getDagPath( newGroup )
            MFnTrans.setObject( groupDagPath )
            
            # Apply the targets translation to the group.
            targetTranslation = TransformUtility.getMatrixTranslation( targetMatrix, OpenMaya.MFn.kWorld )
            MFnTrans.setTranslation( targetTranslation, OpenMaya.MSpace.kWorld )
            
            # Apply the targets rotation to the group.         
            targetRotation = TransformUtility.getMatrixRotation( targetMatrix, 'quat' )
            MFnTrans.setRotation( targetRotation, OpenMaya.MSpace.kWorld )
            
            # Parent the spacer.
            if inDoParent:
                parent = cmds.listRelatives( inBitName, parent=True )
                if NodeUtility.attributeCheck( parent[0], 'controlName' ):
                    parentControl = NodeUtility.getFrameBitSettings( parent[0] )[ 'controlName' ]
                    cmds.parent( newGroup, 'ct_'+parentControl, absolute=True )
                    
        return newGroup
            
    def createController( self, inControlType, inControlSubType, inControlName, inControlParent=None, inPrefix=None ):        
        if inControlType == 'glBox':
            if inPrefix is not None:
                controlName = 'ct_'+inPrefix+'_'+inControlName
            else:
                controlName = 'ct_'+inControlName
            
            glBox.glBoxControl( inControlSubType, controlName )
            
            if inControlParent is not None:
                cmds.parent( controlName, inControlParent, relative=True )