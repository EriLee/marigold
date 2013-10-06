import types
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

def connectPlugs( inSourcePlug, inDestinationPlug ):
    '''
    Connects one plug to another.
    
    @param inSourcePlug: String. Name of the source plug. Node.Plug.
    @param inDestinationPlug: String. Name of the destination plug. Node.Plug.
    '''
    cmds.connectAttr( inSourcePlug, inDestinationPlug, force=True )
    
def attributeCheck( inObj, inAttribute ):
    '''
    Check an object for a given attribute.
    
    @param inObj: String. Name of an object.
    @param inAttribute: String. Name of an attribute. 
    @return: True if the attribute exists. Otherwise False.
    '''
    depNode = getDependNode( inObj )
    depFn = OpenMaya.MFnDependencyNode()
    depFn.setObject( depNode )
    return depFn.hasAttribute( inAttribute )

def connectNodes( inParentObj, inParentPlug, inChildObj, inChildPlug ):
    '''
    @param inParentObj: String. Name of parent node.
    @param inParentPlug: String. Name of plug on parent node.
    @param inChildObj: String. Name of child node.
    @param inChildPlug: String. Name of plug on child node.
    '''
    parentPlug = getPlug( inParentObj, inParentPlug )
    childPlug = getPlug( inChildObj, inChildPlug )
    MDGMod = OpenMaya.MDGModifier()
    MDGMod.connect( parentPlug, childPlug )
    MDGMod.doIt()
    
def disconnectNodes( inParentObj, inParentPlug, inChildObj, inChildPlug ):
    parentPlug = getPlug( inParentObj, inParentPlug )
    childPlug = getPlug( inChildObj, inChildPlug )
    MDGMod = OpenMaya.MDGModifier()
    MDGMod.disconnect( parentPlug, childPlug )
    MDGMod.doIt()

def getAttrMessageValue( inNode, inAttr ):
    '''
    Retrieves the connections to/from a message attribute.
    
    @param string inNode: Node with the desired attribute.
    @param string inAttr: Name of source attribute.
    @return: String for unicode. String[] for list.
    '''
    destCheck = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), isDestination=True )
    sourceCheck = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), isSource=True )
    if destCheck:
        attrConnection = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), sourceFromDestination=True )
    elif sourceCheck:
        attrConnection = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), destinationFromSource=True )
    else:
        return None
    return attrConnection

def getNodeAttrDestination( inNode, inAttr ):
    '''
    Gets the destination of an attribute on the given node.
    
    @param string inNode: Node with the desired attribute.
    @param string inAttr: Name of source attribute.
    @return: Returns list containing the destination attribute and it's node.
    '''        
    attrConnection = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), destinationFromSource=True )
    if len( attrConnection ) == 1:
        return attrConnection[0].split( '.' )
    elif len( attrConnection ) > 1:
        return attrConnection
    else:
        return None

def getNodeAttrSource( inNode, inAttr ):
    '''
    Gets the source of an attribute on the given node.
    
    @param string inNode: Node with the desired attribute.
    @param string inAttr: Name of source attribute.
    @return: Returns list containing the source attribute and it's node.
    '''        
    attrConnection = cmds.connectionInfo( '{0}.{1}'.format( inNode, inAttr ), sourceFromDestination=True )
    if not attrConnection:
        return None
    elif isinstance( attrConnection, list ):
        return attrConnection
    elif isinstance( attrConnection, unicode ):
        destInfo = attrConnection.split( '.' )
        return destInfo

def getDependNode( inObj ):
    '''
    @param inObj: String.
    @return MObject.
    '''
    selList = OpenMaya.MSelectionList()
    selList.add( inObj )
    mObj = OpenMaya.MObject()
    selList.getDependNode( 0, mObj )
    return mObj

def getDagPath( inObjName ):
    '''
    Takes an object name as a string and returns
    its dag path.
    '''
    # make an empty selection list
    selList = OpenMaya.MSelectionList()
    # add the object to the list
    selList.add( inObjName )
    # create an empty dagpath and fill it with the object's
    mDagPath = OpenMaya.MDagPath()
    selList.getDagPath( 0, mDagPath )
    return mDagPath

def isValidMPlug( inObj ):
    '''
    Checks to see if the passed in object is an instance of MPlug.
    
    @param inObj: Maya object.
    @return: Bool.
    '''
    if isinstance( inObj, OpenMaya.MPlug ):
        return True
    else:
        return False

def addPlug( inBit, inPlugName, inAttrType, inAttrDataType ):
    '''
    Adds a plug to the frame bit.
    
    @param inBit: String. Name of the bit to add the attribute to.
    @param inPlugName: String. Name of the plug to add.
    @param inAttrType: String. Type of attribute to add.
    @param inAttrDataType: String. The attribute data type.
    '''
    if inAttrType == 'attributeType':
        if inAttrDataType == 'float3':
            cmds.addAttr( inBit, longName=inPlugName, attributeType=inAttrDataType )
            cmds.addAttr( longName='{0}X'.format( inPlugName ), attributeType='float', parent=inPlugName )
            cmds.addAttr( longName='{0}Y'.format( inPlugName ), attributeType='float', parent=inPlugName )
            cmds.addAttr( longName='{0}Z'.format( inPlugName ), attributeType='float', parent=inPlugName )
        else:
            cmds.addAttr( inBit, longName=inPlugName, attributeType=inAttrDataType )
    elif inAttrType == 'dataType':
        if inAttrDataType == 'typed':
            # Make it a string.
            inAttrDataType = 'string'
        cmds.addAttr( inBit, longName=inPlugName, dataType=inAttrDataType )
    elif inAttrType == 'matrixType':
        mObj = getDependNode( inBit )
        dgModifier = OpenMaya.MDGModifier()
        mAttr = OpenMaya.MFnMatrixAttribute()
        controlMatrix = mAttr.create( inPlugName, inPlugName, OpenMaya.MFnMatrixAttribute.kDouble )
        dgModifier.addAttribute( mObj, controlMatrix )
        dgModifier.doIt()

def convertAttrString( inAttrDataType, inValue ):
    '''
    Converts a string into the appropriate type.
     
    @param inAttrDataType: String. The attribute data type.
    @param inValue: String. Value to convert.
    @return: Correct value.
    '''
    if inAttrDataType in [ 'long', 'enum', 'byte' ]:
        return int( inValue )
    elif inAttrDataType in [ 'doubleLinear', 'float', 'double' ]:
        return float( inValue )
    elif inAttrDataType == 'string':
        return str( inValue )
    elif inAttrDataType == 'bool':
        return bool( inValue )
    elif inAttrDataType == None:
        # This is kinda funky, but the position and rotation return no attribute data types.
        # So the function that gathers that data for writing the XML file fills in None.
        return float( inValue )
    
def setPlug( inBit, inPlugName, inPlugValue, inAttrDataType=None ):
    '''
    Sets the value of the plug.
    
    @param inBit: String. Name of the bit with the plug.
    @param inPlugName: String. Name of the plug to add.
    @param inPlugValue: String. The value of the plug.
    @param inAttrDataType: String. The attribute data type.
    '''
    lockState = cmds.getAttr( '{0}.{1}'.format( inBit, inPlugName), lock=True )
    if lockState is False and inPlugValue != 'None':
        # Convert the value.
        newValue = convertAttrString( inAttrDataType, inPlugValue )
        if inAttrDataType == 'string':
            # It's a string so...
            cmds.setAttr( '{0}.{1}'.format( inBit, inPlugName ), newValue, type='string', lock=False )
        else:
            # Everything else is a number!
            cmds.setAttr( '{0}.{1}'.format( inBit, inPlugName ), newValue, lock=False )
               
def getPlug( inObj, inPlugName ):
    '''
    @param inObj: String.
    @param inPlugName: String.
    @return MPlug.
    '''
    mObj = getDependNode( inObj )
    #print mObj.apiTypeStr()
    depFn = OpenMaya.MFnDependencyNode()
    depFn.setObject( mObj )
    plug = depFn.findPlug( inPlugName )
    return plug#.node()
    
def getPlugValue( inPlug ):
    '''
    @param inPlug: MPlug. The node plug.
    @return: The value of the passed in node plug.
    '''
    pAttribute = inPlug.attribute()
    apiType = pAttribute.apiType()
    
    # Float Groups - rotate, translate, scale; Compounds
    if apiType in [ OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float, OpenMaya.MFn.kCompoundAttribute ]:
        result = []
        if inPlug.isCompound():
            for c in xrange( inPlug.numChildren() ):
                result.append( getPlugValue( inPlug.child( c ) ) )
            return result
    
    # Distance
    elif apiType in [ OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute ]:
        return inPlug.asMDistance().asCentimeters()
    
    # Angle
    elif apiType in [ OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute ]:
        return inPlug.asMAngle().asDegrees()
    
    # TYPED
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        pType = OpenMaya.MFnTypedAttribute( pAttribute ).attrType()
        
        # Matrix
        if pType == OpenMaya.MFnData.kMatrix:
            return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
        
        # String
        elif pType == OpenMaya.MFnData.kString:
            return inPlug.asString()
        
    # MATRIX
    elif apiType == OpenMaya.MFn.kMatrixAttribute:
        return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
    
    # NUMBERS
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()

        if pType == OpenMaya.MFnNumericData.kBoolean:
            return inPlug.asBool()
        elif pType in [ OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong, OpenMaya.MFnNumericData.kByte ]:
            return inPlug.asInt()
        elif pType in [ OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr ]:
            return inPlug.asDouble()
        
    # Enum
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        return inPlug.asInt()
        
def setPlugValue( inPlug, inValue ):
    '''
    @param inPlug: MPlug. The node plug.
    '''
    pAttribute = inPlug.attribute()
    apiType = pAttribute.apiType()
    #print pAttribute.apiTypeStr()
    #print inPlug.info()
    # Float Groups - rotate, translate, scale
    if apiType in [ OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float ]:
        result = []
        if inPlug.isCompound():
            if isinstance( inValue, types.ListType ):
                for c in xrange( inPlug.numChildren() ):
                    result.append( setPlugValue( inPlug.child( c ), inValue[ c ] ) )
                return result
            elif type( inValue ) == OpenMaya.MEulerRotation:
                setPlugValue( inPlug.child( 0 ), inValue.x )
                setPlugValue( inPlug.child( 1 ), inValue.y )
                setPlugValue( inPlug.child( 2 ), inValue.z )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type list.'.format( inPlug.info(), inValue, type( inValue ) ) )
    
    # Distance
    elif apiType in [ OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute ]:
        if isinstance( inValue, types.FloatType ):
            value =  OpenMaya.MDistance( inValue, OpenMaya.MDistance.kCentimeters )
            inPlug.setMDistance( value )
        else:
            OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
    
    # Angle
    elif apiType in [ OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute ]:
        if isinstance( inValue, types.FloatType ):
            value = OpenMaya.MAngle( inValue, OpenMaya.MAngle.kDegrees )
            inPlug.setMAngle( value )
        else:
            OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
            
    # Typed - matrix WE DON'T HANDLE THIS CASE YET!!!!!!!!!
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        pType = OpenMaya.MFnTypedAttribute( pAttribute ).attrType()
        if pType == OpenMaya.MFnData.kMatrix:
            #OpenMaya.MGlobal.displayError( 'Matrix setting hasn\'t been setup yet.' )
            #return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
            if isValidMPlug(inValue):
                # inValue must be a MPlug!
                '''
                sourceValueAsMObject = OpenMaya.MFnMatrixData( inValue.asMObject() ).object()
                blarg = TransformUtility.getMatrixTranslation( OpenMaya.MFnMatrixData( inValue.asMObject() ).matrix() )
                print 'blarg: {0},{1},{2}'.format( blarg.x,blarg.y,blarg.z )
                
                tlarg = TransformUtility.getMatrixTranslation( OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix() )
                print 'tlarg: {0},{1},{2}'.format( tlarg.x,tlarg.y,tlarg.z )
                
                print 'sourceValueAsMObject: {0}'.format( sourceValueAsMObject )
                #inPlug.setMObject( sourceValueAsMObject )
                dgModifier = OpenMaya.MDGModifier()
                dgModifier.newPlugValue( inPlug, sourceValueAsMObject )
                dgModifier.doIt()
                '''
                
                '''
                MFnTrans = OpenMaya.MFnTransform()
                MFnTrans.setObject( inPlug.asMObject() )
                newMatrix = OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
                transMatrix = OpenMaya.MTransformationMatrix( newMatrix ).asMatrix()
                MFnTrans.set( transMatrix )
                '''
                pass
            else:
                plugNode = inPlug.node()
                
                MFnTrans = OpenMaya.MFnTransform( plugNode )
                
                sourceMatrix = OpenMaya.MTransformationMatrix( inValue )#.asMatrix()
                MFnTrans.set( sourceMatrix )
        
        # String
        elif pType == OpenMaya.MFnData.kString:
            value = inValue
            inPlug.setString( value )
    
    # MATRIX
    elif apiType == OpenMaya.MFn.kMatrixAttribute:
        if isValidMPlug(inValue):
            # inValue must be a MPlug!
            sourceValueAsMObject = OpenMaya.MFnMatrixData( inValue.asMObject() ).object()
            inPlug.setMObject( sourceValueAsMObject )
        else:
            OpenMaya.MGlobal.displayError( 'Value object is not an MPlug. To set a MMatrix value, both passed in variables must be MPlugs.' )
    
    # Numbers
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()
        if pType == OpenMaya.MFnNumericData.kBoolean:
            if isinstance( inValue, types.BoolType ):
                inPlug.setBool( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type bool.'.format( inPlug.info(), inValue, type( inValue ) ) )
        elif pType in [ OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong, OpenMaya.MFnNumericData.kByte ]:
            if isinstance( inValue, types.IntType ):
                inPlug.setInt( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type int.'.format( inPlug.info(), inValue, type( inValue ) ) )
        elif pType in [ OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr ]:
            if isinstance( inValue, types.FloatType ):
                inPlug.setDouble( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
                
    # Enums
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        inPlug.setInt( inValue )
        
def getMetaNodesInScene( inNodeType=None ):
    '''
    Finds all nodes of a given type that exist in the active scene.
    
    @param string: Meta type to search for in the scene.
    @return list: All meta nodes in the scene of the given meta type. 
    '''
    nodes = cmds.ls( type='network' )
    nodeList = []
    for node in nodes:
        if attributeCheck( node, 'version' ):
            if inNodeType is not None:
                aType = cmds.getAttr( '{0}.metaType'.format( node ) )
                if aType == inNodeType:
                    tempList = ( node )
                    nodeList.append( tempList )
            else:
                nodeList.append( node )
    return nodeList

def getFrameBitSettings( inFrameBit ):
    '''
    Retrieves the settings for the frame bit.
    
    @param inFrameBit: String. Name of frame bit.
    @return: Dictionary. All the custom attributes on the frame bit.
    '''    
    attrList = cmds.listAttr( inFrameBit, userDefined=True )
    if attrList is not None:
        tempDict = {}
        for attr in attrList:
            plug = getPlug( inFrameBit, attr )
            plugValue = getPlugValue( plug )
            tempDict[ attr ] = plugValue
    else:
        tempDict = None
    return tempDict

def copyBitSettings():
    '''
    Copies the bit shape settings (OpenGL stuff) from the second object to the
    first (in selection order).
    '''
    selList = cmds.ls( selection=True, long=True )
    depFn = OpenMaya.MFnDependencyNode()
    
    if len(selList) == 2:
        # First object is target.
        targetShape = cmds.listRelatives( selList[0], shapes=True, fullPath=True )[0]
        targetShapeMObj = getDependNode( targetShape )
        depFn.setObject( targetShapeMObj )
        targetShapeType = depFn.typeName()
        
        # Second object is source.
        sourceShape = cmds.listRelatives( selList[1], shapes=True, fullPath=True )[0]
        sourceShapeMObj = getDependNode( sourceShape )
        depFn.setObject( sourceShapeMObj )
        sourceShapeType = depFn.typeName()
        
        if targetShapeType == sourceShapeType:        
            # The types match. Do the copy of attribute settings.
            for attr in cmds.listAttr( sourceShape, multi=True, keyable=True ):
                # Get the plugs.
                sourcePlug = getPlug( sourceShape, attr )
                targetPlug = getPlug( targetShape, attr )
                
                # Get the source plug value.
                sourcePlugValue = getPlugValue( sourcePlug )
                
                # Set the target's plug value.
                setPlugValue( targetPlug, sourcePlugValue )
        else:
            raise ValueError( '{0} and {1} do not match.'.format( selList[0], selList[1] ) )
    
def setBitChild( inParent=None, inChild=None ):
    '''
    Connects the child object's matrix plug to the parent object's
    targetWorldMatrix array plug. This plug's data is used by the parent's
    draw() to render the hierarchy arrows.
    
    @param inParent: String. Name of the parent object.
    @param inChild: String. Name of the child object.
    '''
    if inParent is None or inChild is None:
        # Get selection and return the longnames of the objects.
        selList = cmds.ls( selection=True, long=True )
        if len(selList) is 2:
            # The child is the first object.
            # The parent is the second object.
            child = selList[0]
            parent = selList[1]
        else:
            return
    else:
        child = inChild
        parent = inParent
            
    # Get the parent shape's child matrix attribute.
    pShape = cmds.listRelatives( parent, type='shape', allDescendents=False )[0]
    shapeName = '{0}|{1}'.format( parent, pShape )
    parentChildPlug = getPlug( shapeName, 'targetWorldMatrix' )
    
    # This will connect the first time attempted.
    attrName = 'targetWorldMatrix[{0}]'.format( parentChildPlug.numElements() )
    fullParent = '{0}.{1}'.format( shapeName, attrName )
    fullChild = '{0}.matrix'.format( child )
    cmds.connectAttr( fullChild, fullParent, force=True )
    
    # Do any parenting now.
    # Get the child's current parent.
    childParent = cmds.listRelatives( child, parent=True, fullPath=True )
    if childParent is None:
        # Child object has no parent. Do parenting.
        cmds.parent( child, parent )
    else:
        if childParent[0] != parent:
            # Has different parent currently. Do parenting
            cmds.parent( child, parent )
        
def deleteBitChild():
    # Disconnected the child from it's parent.
    selList = cmds.ls( selection=True, long=True )
    for i in selList:
        connections = getNodeAttrDestination( i, 'matrix' )
        parent = '{0}.{1}'.format( connections[0], connections[1] )
        for plug in connections:
            if plug.find( 'targetWorldMatrix' ) is not -1:
                cmds.removeMultiInstance( parent, b=True )
        cmds.parent( i, world=True )
        
def getFrameRootAllChildren( inFrameRootName ):
    '''
    Gets all descendants of a frame root.
    
    @param inFrameRootName: String. Name of frame root object.
    @return: List of children. Ordered from highest to lowest in the hierarchy.
    '''
    children = cmds.listRelatives( inFrameRootName, type='transform', allDescendents=True, fullPath=True )
    tempList = []
    if children is not None:
        for child in children:
            tempList.insert( 0, child )
    else:
        tempList = None
    return tempList

def cleanParentFullName( inBitName ):
    '''
    Removes the first | and the group name from a bit's parent's full path name.
    
    @param inBitName: String. Name of the bit to get the parent full path name.
    @return: String. Cleaned up parent full path name.
    '''
    parent = cmds.listRelatives( inBitName, parent=True, fullPath=True )
    if parent == None:
        retParent = 'None'
    else:
        retParent = parent[0]
    return retParent

def getAttrTypes( inNode, inAttr ):
    '''
    Gets the attribute's attr type and data type. These are needed for adding attributes
    to a node.
    
    @param inNode: String. Name of node.
    @param inAttr: String. Name of attribute.
    @return: List. Attribute Type and Attribute Data Type.
    '''
    attrString = '{0}.{1}'.format( inNode, inAttr )
    attrDataType = cmds.getAttr( attrString, type=True )
    
    if attrDataType in [ 'string', 'matrix', 'TdataCompound' ]: attrType = 'dataType'
    elif attrDataType in [ 'long', 'double', 'bool', 'enum', 'doubleLinear', 'float', 'byte', 'message' ]: attrType = 'attributeType'
    # Certain attributes we don't want. So I pass a False flag which signals other functions
    # to skip the attribute.
    else: attrType = False
    return [ attrType, attrDataType ]

def getModuleComponentSettings( inModuleBit ):
    '''
    Gets an object's component settings.
    
    @param inModuleBit: String. Name of the bit from which to get the components.
    @return: List. List of components.
    '''
    attrList = cmds.listAttr( inModuleBit, userDefined=True )
    returnList = []
    
    if attrList is not None:
        for attrName in attrList:
            # The attributes come in order from top to bottom.
            # They also are recursive. So we use that to our advantage.
            # We only need the attribute names that are used by code.
            # Any attribute that is just a container for other attributes can be skipped.
            attrChildren = cmds.attributeQuery( attrName, node=inModuleBit, listChildren=True )
            
            if attrChildren is None:
                # Single attribute.
                returnList.append( attrName )
    else:
        returnList = None
            
    return returnList

def getCharactersInScene():
    '''
    Retrieve a list of all character components in a scene.
    
    @return: string[]
    '''
    nodes = cmds.ls( type='network' )
    nodeList = []
    for node in nodes:
        if attributeCheck( node, 'modules' ):
            aType = cmds.getAttr( '{0}.classType'.format( node ) )
            if aType == 'CharacterRootComponent':
                nodeList.append( node )
    return nodeList

def getModulesInScenes():
    '''
    Finds all module roots in the active scene.
    '''
    nodes = cmds.ls( type='network' )
    nodeList = []
    for node in nodes:
        if attributeCheck( node, 'characterRoot' ):
            aType = cmds.getAttr( '{0}.classType'.format( node ) )
            if aType == 'ModuleRootComponent':
                nodeList.append( node )
    return nodeList

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

def getModulePriorities( inModules ):
    '''
    Gets all the priorities for a list of module roots.
    
    @param inModules: List. List of module roots.
    '''
    modulesDict = {}
    for item in inModules:
        plug = getPlug( item, 'buildPriority' )
        plugValue = getPlugValue( plug )
        modulesDict[item] = plugValue
    return modulesDict

def getModulesByPriority( inOrder='ascending' ):
    '''
    Gets modules in a scene based on their priority.
    
    @param inOrder: String. Ascending or descending.
    '''
    modules = getModulesInScenes()
    modulesWithPriority = getModulePriorities( modules )
    return sortModules( modulesWithPriority, inOrder )

def getModuleName( inNodeName ):
    '''
    Gets a module name from it's node name.
    
    @param inNodeName: String. Name of a module root node.
    '''
    plug = getPlug( inNodeName, 'moduleName' )
    plugValue = getPlugValue( plug )
    return plugValue

def getModulePriority( inNodeName ):
    '''
    Gets the priority number of a module.
    
    @param inNodeName: String. Module node name.
    '''
    plug = getPlug( inNodeName, 'buildPriority' )
    plugValue = getPlugValue( plug )
    return plugValue

def componentCheck( inComponentList, inComponentType ):
    for component in inComponentList:
        plug = getPlug( component, 'classType' )
        plugValue = getPlugValue( plug )
        if plugValue == inComponentType:
            return component
    return None

def checkBitForComponent( inBitName, inComponentName ):
    '''
    @param inBitName: String. Bit name.
    @param inComponentName: String. Name of the component class.
    @returns: 
    '''
    bitComponents = getModuleComponentSettings( inBitName )
    if bitComponents is not None:
        for component in bitComponents:
            plug = getPlug( component, 'classType' )
            plugValue = getPlugValue( plug )
            if plugValue == inComponentName:
                return component
        return None
    else:
        return None