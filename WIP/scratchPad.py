import os
import math
import sys
import types
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.controllers.marigoldControls as marigoldControls
import marigold.skeleton.marigoldJoints as marigoldJoints
import marigold.meta.metaNode as metaNode
import marigold.utility.NurbsCurveUtility as NurbsCurveUtility
import marigold.components as Components
import marigold.utility.GeneralUtility as GeneralUtility


# @@@@@
'''
# making a matrix attr with cmd
cmds.addAttr( newObj, longName='testMatrix', dataType="matrix")
cmds.setAttr( '{0}.testMatrix'.format(newObj), (1,0,0,0,0,1,0,0,0,0,1,0,2,3,4,1), type='matrix' )
'''

'''
selList = cmds.ls( selection=True )
parent = selList[0]
print parent
children = cmds.listRelatives( parent, type='transform', allDescendents=True )
pShape = cmds.listRelatives( parent, type='shape', allDescendents=False )
print children
print pShape

shapes = cmds.listRelatives( pShape[0], type='shape', allDescendents=True )
print shapes
'''

'''
displayRGBColor -c userDefined1 0.904 0.889783 0.2712;
displayRGBColor -c userDefined2 0.607843 0.229029 0.182353;
displayRGBColor -c userDefined3 0.4095 0.63 0.189;
displayRGBColor -c userDefined4 0.189 0.63 0.3654;
displayRGBColor -c userDefined5 0.189 0.63 0.63;
displayRGBColor -c userDefined6 0.189 0.4051 0.63;
displayRGBColor -c userDefined7 0.43596 0.189 0.63;
displayRGBColor -c userDefined8 0.63 0.189 0.41391;
'''
def addMatrixAttr( targetObj, attrName ):
    mObj = NodeUtility.getDependNode( targetObj )
    dgModifier = OpenMaya.MDGModifier()

    mAttr = OpenMaya.MFnMatrixAttribute()
    controlMatrix = mAttr.create( attrName, attrName, OpenMaya.MFnMatrixAttribute.kDouble )
    dgModifier.addAttribute( mObj, controlMatrix )
    dgModifier.doIt()
        
def getModulePriorities( inModules ):
    '''
    Gets all the priorities for a list of module roots.
    
    @param inModules: List. List of module roots.
    '''
    modulesDict = {}
    for item in inModules:
        plug = NodeUtility.getPlug( item, 'buildPriority' )
        plugValue = NodeUtility.getPlugValue( plug )
        modulesDict[item] = plugValue
    return modulesDict

def sortModules( inModules, inOrder='ascending', renumber=True ):
    '''
    Sorts module roots by priority.
    
    @param inModules: Dict. Dict of modulename:priorty.
    @param inOrder: String. Ascending or descending.
    '''
    from operator import itemgetter
    
    if inOrder == 'ascending':
        sortedModules = sorted( inModules.iteritems(), key=itemgetter(1) )
    elif inOrder == 'descending':
        sortedModules = sorted( inModules.iteritems(), key=itemgetter(1), reverse=True )
        
    if renumber:
        for index, item in enumerate( sortedModules ):
            sortedModules[index] = [ item[0], index ]
    return sortedModules

#========================

def getCharactersInScene():
    nodes = cmds.ls( type='network' )
    nodeList = []
    for node in nodes:
        if NodeUtility.attributeCheck( node, 'modules' ):
            aType = cmds.getAttr( '{0}.classType'.format( node ) )
            if aType == 'CharacterRootComponent':
                nodeList.append( node )
    return nodeList

def componentCheck( inComponentList, inComponentType ):
    for component in inComponentList:
        plug = NodeUtility.getPlug( component, 'classType' )
        plugValue = NodeUtility.getPlugValue( plug )
        if plugValue == inComponentType:
            return component
    return None

def createSpacer( inBitName, inGroupName='newGroup', inTargetObject=None, inDoParent=False, inPrefix=None ):
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
            groupName = inPrefix+'_'+inGroupName
        else:
            groupName = inGroupName
            
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
            targetTranslation = TransformUtility.getMatrixTranslation( targetMatrix, OpenMaya.MSpace.kWorld )
            MFnTrans.setTranslation( targetTranslation, OpenMaya.MSpace.kWorld )
            
            # Apply the targets rotation to the group.         
            targetRotation = TransformUtility.getMatrixRotation( targetMatrix, 'quat' )
            MFnTrans.setRotation( targetRotation, OpenMaya.MSpace.kWorld )
            
            # Parent the spacer.
            if inDoParent:
                parent = cmds.listRelatives( inBitName, parent=True )
                if NodeUtility.attributeCheck( parent[0], 'controlName' ):
                    parentControl = NodeUtility.getFrameBitSettings( parent[0] )[ 'controlName' ]
                    cmds.parent( newGroup, parentControl, absolute=True )
                    
        return newGroup    
    
def buildCharacter( inCharacter ):
    '''
    Build order:
        1) Joints
        2) Control Spacers
        3) Controls
        4) Deformers and Dependencies
    '''
    print 'BUILDING: {0}'.format( inCharacter )
    
    # Get the character modules.
    characterConnections = cmds.connectionInfo( '{0}.{1}'.format( inCharacter, 'modules' ), destinationFromSource=True )
    characterModules = []
    for module in characterConnections:
        splitName = module.split( '.' )
        characterModules.append( splitName[0] )
        
    # Sort modules by priority.
    modulePriorities = getModulePriorities( characterModules )
    sortedModules = sortModules( modulePriorities, 'ascending' )
    
    rootBits = []
    for module in sortedModules:
        moduleName = module[0]
        rootBit = NodeUtility.getNodeAttrSource( moduleName, 'parentName' )
        rootBits.append( rootBit[0] )
    
    # BUILDING: JOINTS
    for root in rootBits:
        # Check the root bit for a joint component.
        rootComponents = NodeUtility.getModuleComponentSettings( root )
        jointCheck = componentCheck( rootComponents, 'BasicJointComponent' )
        if jointCheck is not None:
            # Make the joint.
            Components.BasicJointComponent( jointCheck ).buildNode( jointCheck )
        rootChildren = NodeUtility.getFrameRootAllChildren( root )
        if rootChildren is not None:
            # Check the children bits for a joint component.
            for child in rootChildren:
                childComponents = NodeUtility.getModuleComponentSettings( child )
                jointCheck = componentCheck( childComponents, 'BasicJointComponent' )
                if jointCheck is not None:
                    # Make the joint.
                    childJoint = Components.BasicJointComponent( jointCheck ).buildNode( jointCheck )
                    childJointName = GeneralUtility.getMObjectName( childJoint )
                    childParent = NodeUtility.cleanParentFullName( child )
                    parentComponents = NodeUtility.getModuleComponentSettings( childParent )
                    childParentJointComponent = componentCheck( parentComponents, 'BasicJointComponent' )
                    childParentJoint = cmds.getAttr( '{0}.jointName'.format( childParentJointComponent ) )
                    cmds.parent( childJointName, childParentJoint )
    
    # BUILDING: CONTROLS
    for root in rootBits:
        print 'CONTROL: {0}'.format( root )
        # Check the root bit for a control component.
        rootComponents = NodeUtility.getModuleComponentSettings( root )
        controlCheck = componentCheck( rootComponents, 'CurveControlComponent' )
        if controlCheck is not None:
                # Make the spacer.
                controlName = cmds.getAttr( '{0}.controlName'.format( controlCheck ) )
                controlSpacer = createSpacer( None, inGroupName=controlName, inTargetObject=root, inDoParent=False, inPrefix='sp' )
                
                # Make the control.
                curveType = Components.CurveControlComponent( controlCheck ).curveType
                curve = Components.CurveControlComponent( controlCheck ).createCurveControl( controlName, curveType )
                controlName = OpenMaya.MDagPath.getAPathTo( curve ).fullPathName()
                
                # Parent
                cmds.parent( controlName, controlSpacer )
                controlName = OpenMaya.MDagPath.getAPathTo( curve ).fullPathName()
                
                # Set the control to the transform matrix.
                Components.controls.applyStoredTransforms( controlCheck, controlName )
                
                # Get the saved properties and apply them to the curve.
                cvList = NurbsCurveUtility.readCurveValues( controlCheck )
                cvPointArray = NurbsCurveUtility.buildCVPointArray( cvList )
                NurbsCurveUtility.setCurveCvs( controlName, cvPointArray )
                
                # Color.
                controlColor = cmds.getAttr( '{0}.controlColor'.format( controlCheck ) )
                GeneralUtility.setUserColor( controlName, userColor=controlColor )
                
        # Do it for the children.
        rootChildren = NodeUtility.getFrameRootAllChildren( root )
        if rootChildren is not None:
            for child in rootChildren:
                childComponents = NodeUtility.getModuleComponentSettings( child )
                controlCheck = componentCheck( childComponents, 'CurveControlComponent' )
                if controlCheck is not None:
                    # Make the spacer.
                    controlName = cmds.getAttr( '{0}.controlName'.format( controlCheck ) )
                    controlSpacer = createSpacer( None, inGroupName=controlName, inTargetObject=child, inDoParent=False, inPrefix='sp' )
                    spacerMObject = NodeUtility.getDependNode( controlSpacer )
                    
                    # Make the control.
                    curveType = Components.CurveControlComponent( controlCheck ).curveType
                    curve = Components.CurveControlComponent( controlCheck ).createCurveControl( controlName, curveType )
                    controlName = OpenMaya.MDagPath.getAPathTo( curve ).fullPathName()
                    
                    # Parent
                    cmds.parent( controlName, controlSpacer )
                    controlName = OpenMaya.MDagPath.getAPathTo( curve ).fullPathName()
                    
                    # Set the control to the transform matrix.
                    Components.controls.applyStoredTransforms( controlCheck, controlName )
                    
                    # Get the saved properties and apply them to the curve.
                    cvList = NurbsCurveUtility.readCurveValues( controlCheck )
                    cvPointArray = NurbsCurveUtility.buildCVPointArray( cvList )
                    NurbsCurveUtility.setCurveCvs( controlName, cvPointArray )
                    
                    # Color.
                    controlColor = cmds.getAttr( '{0}.controlColor'.format( controlCheck ) )
                    GeneralUtility.setUserColor( controlName, userColor=controlColor )
                    
                    '''
                    # Parent the spacer.
                    childParent = NodeUtility.cleanParentFullName( child )
                    parentComponents = NodeUtility.getModuleComponentSettings( childParent )
                    childParentControlComponent = componentCheck( parentComponents, 'CurveControlComponent' )
                    childParentControl = cmds.getAttr( '{0}.controlName'.format( childParentControlComponent ) )
                    parentSpacerName = 'sp_{0}'.format( childParentControl )
                    cmds.parent( childJointName, parentSpacerName )
                    '''

characters = getCharactersInScene()
buildCharacter( characters[0] )