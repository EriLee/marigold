import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.GeneralUtility as GeneralUtility
import marigold.components as Components

class BitModule( object ):
    def __init__( self, inModuleNode=None ):
        #print 'BitModule: INIT'
        
        self.moduleNode = inModuleNode
        mObjRootBit = NodeUtility.getDependNode( Components.BaseComponent( self.moduleNode ).parentNode[0] )
        fnDagPath = OpenMaya.MFnDagNode( mObjRootBit )
        self.moduleRootBit = fnDagPath.fullPathName()


    @property
    def moduleName( self ):
        return cmds.getAttr( '{0}.moduleName'.format( self.moduleNode ) )


    def getBits( self ):
        '''
        Gets all the bits of a module. 
        '''        
        # Get all the bits in the module.
        allBits = NodeUtility.getFrameRootAllChildren( self.moduleRootBit )
        moduleBits = NodeUtility.getFrameRootAllChildren( self.moduleRootBit )
        
        # Gather the bits associated with the module.
        # NOTE!!! May need to do this via the component system. This would involve adding some functionality
        # to the add/remove child bit tool. I'm thinking it would connect an attribute from the bit to the 
        # module not, basically creating a list of all the associated bits.
        if allBits is not None:
            # Loop through the bits.
            for bit in allBits:
                # If a bit has a module root component then we remove it and all of it's children.
                moduleCheck = NodeUtility.checkBitForComponent( bit, 'ModuleRootComponent' )
                #print '{0}...{1}'.format( bit, moduleCheck )
                if moduleCheck is not None:
                    if moduleBits.count( bit ) == 1:
                        # There is a high likelihood that there are many levels of nested
                        # modules. Due to the way I remove bits from the list there is also
                        # a high likelihood that at this point I'm trying to remove a module
                        # that doesn't exist any more because it was removed along with another
                        # module for which it is a child. So I check to see if it is still around
                        # and if so remove it.
                        moduleBits.remove( bit )
                        moduleChildren = NodeUtility.getFrameRootAllChildren( bit )
                        if moduleChildren is not None:
                            for child in moduleChildren:
                                moduleBits.remove( child )
        
        # Add the root bit to the list.
        if not moduleBits:
            moduleBits = [ self.moduleRootBit ]
        else:
            moduleBits.insert( 0, self.moduleRootBit )

        return moduleBits
        
    def getFirstParentWithinModule( self , inBit, inComponentClass ):
        '''
        Searches a module for the first parent with the correct component for the
        passed in child bit.
        
        @param inBit: String. Name of the child bit.
        @param inComponentClass: String. Name of the component type to search for.
        @return: None or component node of the parent bit.
        '''        
        moduleBits = self.getBits()
        #print '            {0}'.format( moduleBits )
        parents = getAllParents( inBit )
        #print '            {0}'.format( parents )
        bitParentsInModule = []
        
        if parents:
            bitParentsInModule = compareLists( moduleBits, parents )
            #print '            {0}'.format( bitParentsInModule )
            
        if bitParentsInModule:
            # The returned list of viable parents is generated from the root bit down.
            # So we reverse the list in order to start with the closest parent to the 
            # target child bit.
            for bit in reversed( bitParentsInModule ):
                compCheck = NodeUtility.checkBitForComponent( bit, inComponentClass )
                if compCheck is not None:
                    return compCheck
        
        return None
        
        
    def getFirstParentWithComponentClass( self, inBit, inComponentClass ):
        '''
        Searches through all of the bit's parents to find the first one
        with the given class.
        
        @param inBit: String. Name of a bit.
        @param inComponentClass: String. Name of the class.
        '''
        firstParentWithComponent = None
        
        # Get all the parents of the bit.
        parentBits = getAllParents( inBit )
        
        # Loop through the parent bits.
        if parentBits is not None:
            for parent in parentBits:
                jointComp = NodeUtility.checkBitForComponent( parent, inComponentClass )
                if jointComp is not None:
                    if firstParentWithComponent is None:
                        # We found the first joint component. Set the variable.
                        firstParentWithComponent = jointComp
        
        return firstParentWithComponent
    
                        
    def buildJoints( self ):
        '''
        Builds all the module's joints.
        '''        
        # Create module group. This is a temporary group used during module building to avoid
        # name clashes.
        bits = self.getBits()
        moduleGrpName = '{0}_BUILD'.format( self.moduleName )
        createSpacer( bits[0], inGroupName=moduleGrpName, inTargetObject=bits[0], inDoParent=False, inPrefix=None )
        builtJoints = []
        tempBuildDict = {}
        
        for index,bit in enumerate( bits ):
            # BUILD: JOINTS
            jointComp = NodeUtility.checkBitForComponent( bit, 'BasicJointComponent' )
            if jointComp is not None:
                # Make the joint.
                bitJoint = Components.BasicJointComponent( jointComp ).buildNode( jointComp )
                jointName = GeneralUtility.getMObjectName( bitJoint )
                
                # Now handle any hierarchy setup.
                # Check to see if there is a parent joint for this one.
                if index > 0:
                    # Hold the first parent bit with a joint component that we find in the
                    # hierarchy of the module.
                    firstParent = self.getFirstParentWithComponentClass( bit, 'BasicJointComponent' )
                    
                    # If there is a parent joint in the module then do the parenting.
                    if firstParent is not None:
                        parentJointName = cmds.getAttr( '{0}.jointName'.format( firstParent ) )
                        parentJointFullName = tempBuildDict[parentJointName]
                        cmds.parent( jointName, parentJointFullName )
                    else:
                        # If there is no parent joint in the module then we 
                        # parent it to the module group.
                        cmds.parent( jointName, moduleGrpName )
                
                # If there is only one bit in the module OR it's the first bit in the hierarchy then
                # we parent it to the group.
                if len( bits ) == 1 or index == 0:
                    cmds.parent( jointName, moduleGrpName )
                    
                # Add joint to the built joint list dict.
                fnDagPath = OpenMaya.MFnDagNode( bitJoint )
                tempBuildDict[jointName] = fnDagPath.fullPathName()
                builtJoints.append( { jointName:fnDagPath.fullPathName() } )
        
        if not builtJoints:
            builtJoints = None
                    
        return builtJoints
        

    def buildControls( self ):
        '''
        Builds all the module's controls.
        '''
        print '    BitModule.buildControls'
        
        # Create module group. This is a temporary group used during module building to avoid
        # name clashes.
        bits = self.getBits()
        moduleGrpName = '{0}_BUILD'.format( self.moduleName )
        groupSearch = GeneralUtility.searchSceneByName( moduleGrpName ) 
        if groupSearch is None:
            # If the module build group doesn't exist then make it.
            createSpacer( bits[0], inGroupName=moduleGrpName, inTargetObject=bits[0], inDoParent=False, inPrefix=None )
        
        builtControls = []
        
        for index,bit in enumerate( bits ):
            #print '        build: {0}'.format( bit )
            bitControl = None
            
            # NEED TO ADD ALL POSSIBLE CONTROL TYPES HERE!!!!!
            controlCurveComp = NodeUtility.checkBitForComponent( bit, 'CurveControlComponent' )
            if controlCurveComp is not None:
                # Make the curve control.
                bitControl = Components.CurveControlComponent( controlCurveComp ).buildNode( controlCurveComp )
                controlName = GeneralUtility.getMObjectName( bitControl )
                
                # Controls have a spacer group. This is what we need to parent later on.
                spacerGroup = cmds.listRelatives( controlName, parent=True )
                spacerGrpName = spacerGroup[0]
                
                # Get the first parent bit with a curve control component that we find in the
                # hierarchy of the module.
                firstParent = self.getFirstParentWithinModule( bit, 'CurveControlComponent' )
                #print '            firstParent: {0}'.format( firstParent )
                    
            if bitControl is not None:
                # Now handle any hierarchy setup.
                # Check to see if there is a parent joint for this one.
                if index > 0:
                    # If there is a parent control in the module then do the parenting.
                    if firstParent is not None:
                        parentControlName = cmds.getAttr( '{0}.controlName'.format( firstParent ) )
                        #print '                parentJointName: {0}'.format( parentJointName )
                        #print '                tempBuildDict: {0}'.format( tempBuildDict )
                        cmds.parent( spacerGrpName, parentControlName )
                    else:
                        # If there is no parent control in the module then we 
                        # parent it to the module group.
                        cmds.parent( spacerGrpName, moduleGrpName )
                
                # If there is only one bit in the module OR it's the first bit in the hierarchy then
                # we parent it to the group.
                if len( bits ) == 1 or index == 0:
                    cmds.parent( spacerGrpName, moduleGrpName )
                
                # Add joint to the built joint list dict.
                #fnDagPath = OpenMaya.MFnDagNode( bitControl )
                #tempBuildDict[controlName] = fnDagPath.fullPathName()
                #builtControls.append( { controlName:fnDagPath.fullPathName() } )
                
                # Control Name: Spacer Name
                builtControls.append( [ bit, controlName, spacerGrpName ] )
                
        if not builtControls:
            builtControls = None
                    
        return builtControls
        

    def buildModule( self, inSkeletonGroup=None, inRigGroup=None ):
        '''
        Build order:
            1) Joints
                -setup hierarchy
            2) Controls
                -spacers for each control
                -constrain joint to control if needed
                -channel box limitations
                -add to character set if one exists
            3) Deformers and Dependencies
                -highly customized. each thing should be it's own component with loads of options.
        '''
        # BUILD: JOINTS
        builtJoints = self.buildJoints()
        if inSkeletonGroup is not None and builtJoints is not None:
            # This module is being built as part of a character.
            # Move the joints to the character skeleton.
            firstParentWithJoint = self.getFirstParentWithComponentClass( self.moduleRootBit, 'BasicJointComponent' )
            
            # If there is a parent joint in the module then do the parenting.
            if firstParentWithJoint is not None:
                parentJointName = cmds.getAttr( '{0}.jointName'.format( firstParentWithJoint ) )              
                groupCheck = searchGroup( inSkeletonGroup, 'joint', parentJointName )
                if groupCheck is not None:
                    cmds.parent( builtJoints[0].values(), groupCheck )
            else:
                # If there is no parent joint in the module then we 
                # parent it to the character group.
                cmds.parent( builtJoints[0].values(), inSkeletonGroup )

        # BUILD: CONTROLS
        builtControls = self.buildControls()
        if inRigGroup is not None and builtControls is not None:
            # NEED TO HANDLE ALL KINDS OF CONTROL OBJECTS.
            for controlInfo in builtControls:
                bitName = controlInfo[0]                
                controlName = controlInfo[1]
                controlSpacer = controlInfo[2]
                print '        control name: {0}'.format( controlName )
                print '        control spacer: {0}'.format( controlSpacer )
                
                print '        bit name: {0}'.format( bitName )
                firstParentWithControl = self.getFirstParentWithComponentClass( bitName, 'CurveControlComponent' )
                print '        firstParentWithControl: {0}'.format( firstParentWithControl )
                
                if firstParentWithControl is not None:
                    parentControlName = cmds.getAttr( '{0}.controlName'.format( firstParentWithControl ) )
                    print '            parentControlName: {0}'.format( parentControlName )
                    
                    groupCheck = searchGroup( inRigGroup, None, parentControlName )
                    print '            groupCheck: {0}'.format( groupCheck )
                    
                    if groupCheck:
                        # Check to see if the object's parent is already correct.
                        mObj = NodeUtility.getDependNode( controlSpacer )
                        fn = OpenMaya.MFnDagNode()    
                        fn.setObject( mObj )
        
                        for index in xrange( fn.parentCount() ):
                            fnParent = OpenMaya.MFnDagNode()
                            parent = fn.parent( index )
                            fnParent.setObject( parent )
                            parentName = fnParent.name()
                            print '        parentName: {0}'.format( parentName )
                            
                            splitString = groupCheck.split( '|' )
                            testString = splitString[-1]
                            print testString
                            
                        # If the object's current parent is not the desired one then
                        # do the correct parenting.
                        if testString != parentName:
                            cmds.parent( controlSpacer, groupCheck )                    
                else:
                    cmds.parent( controlSpacer, inRigGroup )
                print '        END'
        
class BitCharacter( object ):
    def __init__( self, inCharacterNode=None ):
        self.characterNode = inCharacterNode


    @property
    def characterName( self ):
        return cmds.getAttr( '{0}.characterName'.format( self.characterNode ) )


    @property
    def skeletonGroupName( self ):
        return cmds.getAttr( '{0}.skeletonGroupName'.format( self.characterNode ) )


    @property
    def rigGroupName( self ):
        return cmds.getAttr( '{0}.rigGroupName'.format( self.characterNode ) )


    def getCharacterModules( self, sort=False, sortType='ascending' ):
        '''
        Get all the modules contained in the character.
        
        @param sort: Bool. Whether to sort the module list by priority.
        @param sortType: String. Type of sort. Can be 'ascending' or 'descending.'
        @return: Class BitModule[]. List of modules cast to BitModule.
        '''
        # Get all the modules in a character.
        characterConnections = cmds.connectionInfo( '{0}.{1}'.format( self.characterNode, 'modules' ), destinationFromSource=True )
        characterModules = []
        for module in characterConnections:
            # Loop through the list and retrieve the module component node name for each component.
            splitName = module.split( '.' )
            characterModules.append( splitName[0] )
            
        if sort:
            modulePriorities = NodeUtility.getModulePriorities( characterModules )
            characterModules = NodeUtility.sortModules( modulePriorities, sortType )
        
        # A character root must also have a module component on it's top most bit.
        # Check if this is true. If so, add it to the top of the module list.
        # Otherwise we kill the build and kick up an error.
        charBit = Components.BaseComponent( self.characterNode ).parentNode[0]
        charModule = NodeUtility.checkBitForComponent( charBit, 'ModuleRootComponent' )
        if charModule is not None:
            temp = [ charModule, 00 ]
            characterModules.insert( 0, temp )
        else:
            OpenMaya.MGlobal.displayError( 'The character\'s root module is missing a module component on it\'s top most bit.' )
            
        # Cast the modules to BitModule.
        returnList = []
        for module in characterModules:
            returnList.append( BitModule( module[0] ) )
            
        return returnList
        
    
    def buildCharacter( self ):
        '''
        Build the character.
        
        1) make character set
        
        '''
        print 'Building: {0}'.format( self.characterNode )
        
        # Build the character component.
        # Create character stuff.
        characterName = self.characterName
        
        groupSearch = GeneralUtility.searchSceneByName( self.skeletonGroupName ) 
        if groupSearch is None:
            skeletonGrp = cmds.group( em=True, name=self.skeletonGroupName )
        else:
            skeletonGrp = self.skeletonGroupName
        
        groupSearch = GeneralUtility.searchSceneByName( self.rigGroupName )
        if groupSearch is None:
            rigGrp = cmds.group( em=True, name=self.rigGroupName )
        else:
            rigGrp = self.rigGroupName
        
        characterModules = self.getCharacterModules( sort=True )
        
        # Build each module.
        for module in characterModules:
            print 'BUILDING: {0}'.format( module.moduleName )
            module.buildModule( inSkeletonGroup=skeletonGrp, inRigGroup=rigGrp )
            
'''
THINGS TO MOVE LATER!!!!
'''
def createSpacer( inBitName, inGroupName='newGroup', inTargetObject=None, inDoParent=False, inPrefix=None ):
    import marigold.utility.TransformUtility as TransformUtility
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

def getAllParents( inObjectName, inList=None ):
    '''
    Returns list of all parent objects to the passed in object.
    Returns None if the object has no parents.
    '''
    if inList == None:
        returnList = []
    else:
        returnList = inList
    
    mObj = NodeUtility.getDependNode( inObjectName )
    fn = OpenMaya.MFnDagNode()    
    fn.setObject( mObj )
    
    for index in xrange( fn.parentCount() ):
        fnParent = OpenMaya.MFnDagNode()
        parent = fn.parent( index )
        fnParent.setObject( parent )
            
        if fnParent.name() == 'world':
            if not returnList:
                return None
            else:
                return returnList
        else:
            returnList.append( fnParent.fullPathName() )
            return getAllParents( fnParent.fullPathName(), inList=returnList )

def searchGroup( inGroupName, inSearchType, inSearchString ):
    '''
    Searches a group for a given object.
    
    @param inGroupName: String. Name of the group to search.
    @param inSearchType: String. Type of object to search for. Possible types are: transform, joint
    @param inSearchString: String. Name of the object to find.
    @return: None or full path name of the found object.
    '''
    returnValue = None
    if inSearchType:
        children = cmds.listRelatives( inGroupName, type=inSearchType, allDescendents=True, fullPath=True )
    else:
        children = cmds.listRelatives( inGroupName, allDescendents=True, fullPath=True )
        
    for child in children:
        # These are full path names so we need to check against the
        # last bit of the string.
        splitString = child.split( '|' )
        testString = splitString[-1]
        if testString == inSearchString:
            returnValue = child
    return returnValue

def compareLists( list1, list2 ):
    tempList = []
    for val in list1:
        if val in list2:
            tempList.append( val )
    return tempList

#=====
#module = 'ModuleRootComponent5'
#thing = BitModule( module )
#thing.buildJoints()

characters = 'CharacterRootComponent'
character = BitCharacter( characters )
character.buildCharacter()

#thing = BitModule.getFirstParentWithComponentClass( inBit, inComponentClass)

#thing = BitModule( 'ModuleRootComponent2' )
#bits = thing.getBits()
#for bit in bits:
#    print bit
