def getBoxPoints():
    '''
    retrieves a meshes vertices.
    '''
    selList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList( selList )
    if selList.length() is 1:
        control = OpenMaya.MObject()
        selList.getDependNode( 0, control )    
        controlDagNode = OpenMaya.MFnDagNode( control )
        for c in xrange( controlDagNode.childCount() ):
            child = controlDagNode.child( c )
            if child.apiType() == OpenMaya.MFn.kMesh:
                deformMesh = OpenMaya.MFnMesh( child )
                print deformMesh
                vertexCount = OpenMaya.MIntArray()    
                vertexList = OpenMaya.MIntArray()
                deformMesh.getVertices( vertexCount, vertexList )
                print vertexCount
                print vertexList
                
                vertexArray = OpenMaya.MFloatPointArray()
                deformMesh.getPoints( vertexArray, OpenMaya.MSpace.kObject )
                print vertexArray
                for p in xrange( vertexArray.length() ):
                    print p
                    print vertexArray[p].x, vertexArray[p].y, vertexArray[p].z
                    
def createJointOLD( inBit, inParent=None, inJointRadius=4.0 ):
    '''
    Creates a single joint.
    
    @param inBit: String. Name of the frame bit.
    @param inParent: MObject. Parent MObject for the new joint.
    @return: The MObject of the joint created.
    '''
    if attributeCheck( inBit, 'jointName' ):
        # Create the joint.
        dagMod = OpenMaya.MDagModifier()
        if inParent:
            newJoint = dagMod.createNode( 'joint', inParent )
        else:
            newJoint = dagMod.createNode( 'joint' )
        dagMod.doIt()
        
        # Name the joint.
        depFn = OpenMaya.MFnDependencyNode( newJoint )
        bitSettings = getFrameBitSettings( inBit )
        jointName = 'j_'+bitSettings['jointName']
        depFn.setName( jointName )
        
        # Modify the joint.
        jointFn = OpenMayaAnim.MFnIkJoint()
        jointFn.setObject( newJoint )
        
        parentDepNode = OpenMaya.MFnDependencyNode( jointFn.parent( 0 ) )
        bitLocalMatrix = TransformUtility.getMatrix( inBit, 'matrix' )
        bitWorldMatrix = TransformUtility.getMatrix( inBit, 'worldMatrix' )
        
        # Set orientation.
        # TODO
        
        # Set position.
        bitWorldTranslationVector = TransformUtility.getMatrixTranslation( bitWorldMatrix, OpenMaya.MFn.kWorld )
        if parentDepNode.name() == 'world':
            # If the joint's parent is the world, then we take the translation vector straight
            # from the frame bit's world matrix.
            jointVector = bitWorldTranslationVector
        else:
            # If the joint's parent is another joint, then we need to get the parent's world
            # matrix and use it as a change of basis for the frame bit's world matrix.
            parentMatrix = TransformUtility.getMatrix( parentDepNode.name(), 'worldMatrix' )
            basisMatrix = bitWorldMatrix * parentMatrix.inverse()            
            jointVector = TransformUtility.getMatrixTranslation( basisMatrix, OpenMaya.MFn.kWorld )
        jointFn.setTranslation( jointVector, OpenMaya.MSpace.kTransform )
        
        # Set rotation order.
        # TODO
        
        # Set rotation.
        if parentDepNode.name() == 'world':
            print 'set world euler'
            bitEuler = TransformUtility.getMatrixRotation( bitWorldMatrix, 'euler' )
            jointFn.setRotation( bitEuler )
        else:
            print 'set local euler'
            bitEuler = TransformUtility.getMatrixRotation( bitLocalMatrix, 'euler' )                
            jointFn.setRotation( bitEuler )
        
        # Set preferred angle.
        # TODO
        
        # Set joint radius.
        cmds.setAttr( jointName+'.radius', inJointRadius )
        
        return newJoint

def createJointChain( inBits, inJointRadius=4.0 ):
    '''
    Creates a chain of joints.
    
    @param inBits: List. Frame bits to use to make a joint chain. List needs to 
        be ordered from top to bottom of the hierarchy.
    @param inJointRadius: Float. Size of the joint radius.
    '''
    # Loop through all the items in the list of frame bits. We want to build from 
    # the chain root on down. This is done in while loop so each built joint can
    # be removed from the list prior to the next iteration. 
    while len(inBits) > 0:
        parent = cmds.listRelatives( inBits[0], parent=True )
        if attributeCheck( parent[0], 'jointName' ):
            # This is the root joint.
            parentSettings = getFrameBitSettings( parent[0] )
            
            # Does the parent joint exist?
            parentJoint = 'j_'+parentSettings['jointName']
            if cmds.objExists( parentJoint ):   
                parentJointObj = NodeUtility.getDependNode( parentJoint )
                createJoint( inBits[0], parentJointObj, inJointRadius )
                inBits.remove( inBits[0] )
            else:
                # The joint's parent doesn't exist so we skip creating it and leave
                # it in the list.
                pass           
        else:
            # This is the chain's root joint. Make it without a parent.
            createJoint( inBits[0], None, inJointRadius )
            inBits.remove( inBits[0] )
            
def buildRigging():
    '''
    Naming Convention:
        Spacers = sp_
        Joints = j_
        Controls = ct_
        Auto Parts = auto_
        Spans = span_
        Constraints = con_
        IK = ik_
        UpVector = upv_
        Frame Part = frame_
            Frame Joint = frame_j_
            Frame Root = frame_root_
    
    FRAME BITS
        these are stand alone classes:
            frame root
                name prefix: frame_root_
                torus: 6, 0.2, 0, 8, 3
                attribs:
                    frameType, string, type of frame.
                    frameSubtype, string, subtype of frame.
                    frameRoot, boolean
                    buildPriority, int, priority in which to build the frame. high is sooner.
                    buildType, string, type of frame to build. etc: arms
                    buildSubtype, string, subtype of frame to build. etc: basicHuman
            JOINT BITs
                name prefix: frame_j_
                jointName, string, name of joint to create from this bit. only used if the bit makes a joint.
                controlType, string, name of the control to build for this bit.
                controlSubType, string, name of the control sub-type.
                controlName, string, name of the controller.
                
                ball joint
                    sphere: 4, 8, 4
                    notes:
                        
                hinge joint
                    cylinder: 1, 10, 6
                    notes:
                        -need to lock down the two unused position axes.
                        -need to lock down the two unused rotation axes.
        
    FRAME BUILD
        xml.
        store each bit of the frame.
        stats:
            type of bit
            name of bit
            position
            rotation
            parent of bit
            
    FRAME PRESETS
        xml.
        used to store settings for a frame.
    
    get tags
        need root and end
    
    get elbows
    
    create spacers for each joint
        pose to the joint
        
    create control skeleton
    
    create ik solver on control skeleton
        set its properties
        
    create fk controls
    
    create constraint ik/fk blend node
        create constraints on shadow skeleton
        hook up node
        
    add rigging to meta network
    
    add rigging to rig hierarchy
    '''
    
    # TEMP!!!!
    # Get all the frames in the scene.
    frames = getFramesInScene()
                
    # Put in build order.    
    
    # Loop through the frames.
    for frame in frames:
        #frameDag = NodeUtility.getDagPath( frame )
        #getFrameRootChildren( frameDag )
        children = getFrameRootAllChildren( frame )
        print 'children: {0}'.format( children )
        
        # Build shadow skeleton.
        frameBitSettings = getFrameBitSettings( frame )
        attributeCheck( frame, 'frameRoots' )
        #print '{0}.jointName: {1}'.format( frame, frameBitSettings['jointName'] )
        
        # Make the shadow skeleton.
        childrenWithJoints = []
        for child in children:
            if attributeCheck( child, 'jointName' ):
                childrenWithJoints.append( child )
        #createJointChain( childrenWithJoints )
        
        # Make the rig.
        controlBits = getFrameBitsByAttribute( children, 'controlType' )
        for bit in controlBits:
            bitSettings = getFrameBitSettings( bit )
            jointName = 'j_'+bitSettings[ 'jointName' ]
            controlType = bitSettings[ 'controlType' ]
            controlSubType = bitSettings[ 'controlSubType' ]
            controlName = bitSettings[ 'controlName' ]
            
            if cmds.objExists( jointName ):
                # Create the spacer.
                newSpacer = makeControl().createSpacer( bit, controlName, jointName, True )
                
                # Create the controller.
                makeControl().createController( controlType, controlSubType, controlName, newSpacer )
            
            #3. Make custom shit
            
# Get vectors for drawing lines between this node and it's children.
mPlug = OpenMaya.MPlug( self.thisMObject(), socketNode.attribute( 'targetWorldMatrix' ) )
childrenList = []
for c in xrange( mPlug.numChildren() ):
    childPlug = mPlug.child( c )
    mData = OpenMaya.MFnMatrixData( childPlug.asMObject() ).matrix()
    mTrans = OpenMaya.MTransformationMatrix( mData )
    childrenList.append( mTrans.getTranslation( OpenMaya.MSpace.kTransform ) )