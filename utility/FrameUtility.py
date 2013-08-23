import math
import os
import sys
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.utility.GeneralUtility as GeneralUtility
import marigold.meta.metaNode as metaNode

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
        targetShapeMObj = NodeUtility.getDependNode( targetShape )
        depFn.setObject( targetShapeMObj )
        targetShapeType = depFn.typeName()
        
        # Second object is source.
        sourceShape = cmds.listRelatives( selList[1], shapes=True, fullPath=True )[0]
        sourceShapeMObj = NodeUtility.getDependNode( sourceShape )
        depFn.setObject( sourceShapeMObj )
        sourceShapeType = depFn.typeName()
        
        if targetShapeType == sourceShapeType:        
            # The types match. Do the copy of attribute settings.
            for attr in cmds.listAttr( sourceShape, multi=True, keyable=True ):
                # Get the plugs.
                sourcePlug = NodeUtility.getPlug( sourceShape, attr )
                targetPlug = NodeUtility.getPlug( targetShape, attr )
                
                # Get the source plug value.
                sourcePlugValue = NodeUtility.getPlugValue( sourcePlug )
                
                # Set the target's plug value.
                NodeUtility.setPlugValue( targetPlug, sourcePlugValue )
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
        child = inChild
        parent = inParent
            
    # Get the parent shape's child matrix attribute.
    pShape = cmds.listRelatives( parent, type='shape', allDescendents=False )[0]
    shapeName = '{0}|{1}'.format( parent, pShape )
    parentChildPlug = NodeUtility.getPlug( shapeName, 'targetWorldMatrix' )
    
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
        connections = NodeUtility.getNodeAttrDestination( i, 'matrix' )
        parent = '{0}.{1}'.format( connections[0], connections[1] )
        for plug in connections:
            if plug.find( 'targetWorldMatrix' ) is not -1:
                cmds.removeMultiInstance( parent, b=True )
        cmds.parent( i, world=True )
        
def addPlug( inBit, inPlugName, inAttrType, inAttrDataType ):
    '''
    Adds a plug to the frame bit.
    
    @param inBit: String. Name of the bit to add the attribute to.
    @param inPlugName: String. Name of the plug to add.
    @param inAttrType: String. Type of attribute to add.
    @param inAttrDataType: String. The attribute data type.
    '''
    if inAttrType == 'attributeType':
        cmds.addAttr( inBit, longName=inPlugName, attributeType=inAttrDataType )
    else:
        if inAttrDataType == 'typed':
            # Make it a string.
            inAttrDataType = 'string'
        cmds.addAttr( inBit, longName=inPlugName, dataType=inAttrDataType )

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

def convertAttrString( inAttrDataType, inValue ):
    '''
    Converts a string into the appropriate type.
     
    @param inAttrDataType: String. The attribute data type.
    @param inValue: String. Value to convert.
    @return: Correct value.
    '''
    if inAttrDataType in [ 'long', 'enum' ]:
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
            plug = NodeUtility.getPlug( inFrameBit, attr )
            plugValue = NodeUtility.getPlugValue( plug )
            tempDict[ attr ] = plugValue
    else:
        tempDict = None
    return tempDict

def getFrameRootAllChildren( inFrameRootName ):
    '''
    Gets all descendants of a frame root.
    
    @param inFrameRootName: String. Name of frame root object.
    @return: List of children. Ordered from highest to lowest in the hierarchy.
    '''
    children = cmds.listRelatives( inFrameRootName, type='transform', allDescendents=True, fullPath=True )
    tempList = []
    for child in children:
        tempList.insert( 0, child )
    return tempList
    
def getFrameRootChildren( inFrameDagNode ):
    '''
    Gets the direct children of a frame root.
    
    @param inFrameDagNode: Frame root dag node.
    @return: 
    '''
    depFn = OpenMaya.MFnDependencyNode()
    for c in xrange( inFrameDagNode.childCount() ):
        child = inFrameDagNode.child( c )
        depFn.setObject( child )
        
def getFramesInSceneWIP():
    # Get all the meta nodes in the scene.
    metaNodes = NodeUtility.getMetaNodesInScene()
    print metaNodes
    
    if not metaNodes:
        return None
    else:
        for node in metaNodes:
            # Get the root bit of the frame module.
            rootBit = NodeUtility.getNodeAttrSource( node, 'rootBit' )
            # Get the parent's full path. We need to remove the group name from the beginning as well.
            parent = cleanParentFullName( rootBit[0] )
            print parent

def getFramesInScene():
    # NEED TO HANDLE A SCENE WITH NO FRAMES.
    '''
    Finds all frame roots in the active scene.
 
    @return: A list of frame root names in string format.
    '''
    # Build a selection list of all frame roots in the scene.
    search = 'frame_root*'
    selList = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getSelectionListByName( search, selList )
    
    # Get an iterable list of the frame roots.
    iter = OpenMaya.MItSelectionList( selList )
    depFn = OpenMaya.MFnDependencyNode()
    mObj = OpenMaya.MObject()
    
    # Loop through them.
    tempList = []
    while not iter.isDone():
        iter.getDependNode( mObj )
        if mObj.apiType() == OpenMaya.MFn.kTransform:
            depFn.setObject( mObj )
            if depFn.hasAttribute( 'frameRoot' ):
                tempList.append( depFn.name() )
        iter.next()
    return tempList

def getFrameBitsByAttribute( inList, inAttrib ):
    '''
    Gets all the frame bits with a given attribute.
    
    @param inList: String List. Names of frame bits to check.
    @param inAttrib: String. Name of attribute to check each bit for.
    @return: List of frame bits that match the search criteria.
    '''
    tempList = []
    for frameBit in inList:
        if NodeUtility.attributeCheck( frameBit, inAttrib ):
            tempList.append( frameBit )
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
    
    
def createFrameModuleXML():
    # Browse for file to replace or new file to make.
    moduleFilter = "*.xml"
    dialogResults = cmds.fileDialog2( fileFilter=moduleFilter, dialogStyle=2, startingDirectory=XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH ) )
    tempPath = dialogResults[0].split( '/' )
    fullFileName = tempPath[ len( tempPath )-1 ]
    filePath = dialogResults[0].rstrip( fullFileName )
    fileName = fullFileName.split( '.' )[0]
    
    # Get the name of the selected node and it's plugs.
    selList = cmds.ls( selection=True )
    node = selList[0]
    nodeAttrs = getFrameBitSettings( node )
    
    # Build a list with each entry representing a line in the XML file.
    xmlList = []
    xmlList.append( '<data>' ) # Set the first line
    
    # Meta node.
    xmlList.append( '\t<metanode name=\"{0}\" metaType=\"{1}\" metaClass=\"{2}\">'.format( node, nodeAttrs['metaType'], nodeAttrs['metaClass'] ) )
    
    # Loop through the attributes.
    for attr in nodeAttrs:
        plug = NodeUtility.getPlug( node, attr )
        if plug.isConnected():
            connection = NodeUtility.getNodeAttrSource( node, attr )
            types = getAttrTypes( node, attr )
            xmlList.append( '\t\t<plug name=\"{0}\" connected=\"{1}\" attrType=\"{2}\" attrDataType=\"{3}\">{4}</plug>'.format( attr,
                                                                                                                                True,
                                                                                                                                types[0],
                                                                                                                                types[1],
                                                                                                                                connection[0]+'.'+connection[1] ) )
        else:
            types = getAttrTypes( node, attr )
            xmlList.append( '\t\t<plug name=\"{0}\" connected=\"{1}\" attrType=\"{2}\" attrDataType=\"{3}\">{4}</plug>'.format( attr,
                                                                                                                                False,
                                                                                                                                types[0],
                                                                                                                                types[1],
                                                                                                                                NodeUtility.getPlugValue( plug ) ) )
    xmlList.append( '\t</metanode>' )
    
    # Get the root bit of the frame module.
    rootBit = NodeUtility.getNodeAttrSource( node, 'rootBit' )
    if not rootBit:
        raise ValueError( 'The meta node\'s ({0}) ROOT BIT attribute is not connected.'.format(node) )

    # Get the parent's full path. We need to remove the group name from the beginning as well.
    parent = cleanParentFullName( rootBit[0] )

    
    xmlList.append( '\t<bit name=\"{0}\" parent=\"{1}\">'.format( rootBit[0], parent ) )
    rootAttrs = getFrameBitSettings( rootBit[0] )
    for attr in rootAttrs:
        types = getAttrTypes( rootBit[0], attr )
        plug = NodeUtility.getPlug( rootBit[0], attr )
        xmlList.append( '\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                          types[0],
                                                                                                          types[1],
                                                                                                          NodeUtility.getPlugValue( plug ) ) )
    
    wmRootBit = TransformUtility.getMatrix( rootBit[0], 'matrix' )
    pos = TransformUtility.getMatrixTranslation( wmRootBit )
    rot = TransformUtility.getMatrixRotation( wmRootBit, 'eulerVector' )
    xmlList.append( '\t\t<plug name=\"translateX\">{0}</plug>'.format( pos.x ) )
    xmlList.append( '\t\t<plug name=\"translateY\">{0}</plug>'.format( pos.y ) )
    xmlList.append( '\t\t<plug name=\"translateZ\">{0}</plug>'.format( pos.z ) )
        
    xmlList.append( '\t\t<plug name=\"rotateX\">{0}</plug>'.format( math.degrees(rot.x) ) )
    xmlList.append( '\t\t<plug name=\"rotateY\">{0}</plug>'.format( math.degrees(rot.y) ) )
    xmlList.append( '\t\t<plug name=\"rotateZ\">{0}</plug>'.format( math.degrees(rot.z) ) )
    
    # Shape nodes attributes.
    rootShape = NodeUtility.getDagPath( rootBit[0] ).child( 0 )
    depFn = OpenMaya.MFnDependencyNode( rootShape )
    shapeName = cmds.listRelatives( rootBit[0], shapes=True, fullPath=True )[0]
    shapeType = depFn.typeName()
    xmlList.append( '\t\t<shape name=\"{0}\">'.format( shapeType ) )
    
    # Get the shape's local position and scale.
    for attr in cmds.listAttr( shapeName, channelBox=True ):
        types = getAttrTypes( shapeName, attr )
        aPlug = NodeUtility.getPlug( shapeName, attr )
        xmlList.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                            types[0],
                                                                                                            types[1],
                                                                                                            NodeUtility.getPlugValue(aPlug) ) )
        
    # Get the shape's custom attributes.
    for attr in cmds.listAttr( shapeName, multi=True, keyable=True ):
        if attr.find( '[' ) is not -1:
            # Special case handle array attributes. The [] needs to be removed so we can get
            # the base name for the attribute. From there we can then loop through it's children.
            # First we get the connection since these plugs won't return a value, but rather a
            # connected node.
            connection = NodeUtility.getNodeAttrSource( shapeName, attr )
            bitChildren = cmds.listRelatives( rootBit[0], type='transform', children=True, fullPath=True )
            for child in bitChildren:
                if child.find( connection[0] ):
                    plugValue = child
            
            # Now we get the compound attribute's name by removing the index brackets.
            attrSplit = attr.split('[')
            attr = attrSplit[0]
        else:
            aPlug = NodeUtility.getPlug( shapeName, attr )
            plugValue = NodeUtility.getPlugValue( aPlug )
            
        types = getAttrTypes( shapeName, attr )
        if types[0] is not False:
            xmlList.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                                types[0],
                                                                                                                types[1],
                                                                                                                plugValue ) )
    xmlList.append( '\t\t</shape>' )
    xmlList.append( '\t</bit>')

    # Get all of the root's children.
    children = getFrameRootAllChildren( rootBit[0] )
    for child in children:
        # Bit name.
        bitName = child
        parent = cleanParentFullName( child )
        childFrameAttrs = getFrameBitSettings( child )
        xmlList.append( '\t<bit name=\"{0}\" parent=\"{1}\">'.format( bitName, parent ) )
    
        # Transform nodes attributes.
        if childFrameAttrs is not None:
            for attr in childFrameAttrs:
                types = getAttrTypes( child, attr )
                plug = NodeUtility.getPlug( child, attr )
                xmlList.append( '\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                                  types[0],
                                                                                                                  types[1],
                                                                                                                  NodeUtility.getPlugValue( plug ) ) )
        
        # Get the position and rotation.
        wmBit = TransformUtility.getMatrix( child, 'matrix' )
        pos = TransformUtility.getMatrixTranslation( wmBit )
        rot = TransformUtility.getMatrixRotation( wmBit, 'eulerVector' )
        
        xmlList.append( '\t\t<plug name=\"translateX\">{0}</plug>'.format( pos.x ) )
        xmlList.append( '\t\t<plug name=\"translateY\">{0}</plug>'.format( pos.y ) )
        xmlList.append( '\t\t<plug name=\"translateZ\">{0}</plug>'.format( pos.z ) )
        xmlList.append( '\t\t<plug name=\"rotateX\">{0}</plug>'.format( math.degrees(rot.x) ) )
        xmlList.append( '\t\t<plug name=\"rotateY\">{0}</plug>'.format( math.degrees(rot.y) ) )
        xmlList.append( '\t\t<plug name=\"rotateZ\">{0}</plug>'.format( math.degrees(rot.z) ) )
        
        # Shape nodes attributes.
        childShape = NodeUtility.getDagPath( child ).child( 0 )
        depFn = OpenMaya.MFnDependencyNode( childShape )
        shapeName = cmds.listRelatives( child, shapes=True, fullPath=True )[0]
        shapeType = depFn.typeName() 
        xmlList.append( '\t\t<shape name=\"{0}\">'.format( shapeType ) )
        
        # Get the shape's local position and scale.
        for attr in cmds.listAttr( shapeName, channelBox=True ):
            types = getAttrTypes( shapeName, attr )
            aPlug = NodeUtility.getPlug( shapeName, attr )
            xmlList.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                                types[0],
                                                                                                                types[1],
                                                                                                                NodeUtility.getPlugValue(aPlug) ) )
            
        # Get the shape's custom attributes.
        for attr in cmds.listAttr( shapeName, multi=True, keyable=True ):
            if attr.find( '[' ) is not -1:
                # Special case handle array attributes. The [] needs to be removed so we can get
                # the base name for the attribute. From there we can then loop through it's children.
                # First we get the connection since these plugs won't return a value, but rather a
                # connected node.
                connection = NodeUtility.getNodeAttrSource( shapeName, attr )
                bitChildren = cmds.listRelatives( child, type='transform', children=True, fullPath=True )
                for c in bitChildren:
                    if c.find( connection[0] ):
                        plugValue = c
                
                # Now we get the compound attribute's name by removing the index brackets.
                attrSplit = attr.split('[')
                attr = attrSplit[0]
            else:
                aPlug = NodeUtility.getPlug( shapeName, attr )
                plugValue = NodeUtility.getPlugValue( aPlug )
                
            types = getAttrTypes( shapeName, attr )
            if types[0] is not False:
                xmlList.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr,
                                                                                                                    types[0],
                                                                                                                    types[1],
                                                                                                                    plugValue ) )
        xmlList.append( '\t\t</shape>' )  
        
        # Close the bit.
        xmlList.append( '\t</bit>' )
            
    # Close the data tag.
    xmlList.append( '</data>' )
    
    # Create the new file.
    newfile = file( os.path.join( filePath, fullFileName ), 'w')      
    for i in xmlList:
        newfile.write( i+'\n' )
    newfile.close()
    
def readFrameModuleXML( inFile=None, inCallScript=False ):
    '''
    Processes an XML file to get the parts/settings for the module.
    
    @param inFullPath: Full directory path + filename + extension of the XML file.
    @return: A dictionary.
    '''
    import xml.etree.ElementTree as ET
    
    if inFile is None:
        # Browse for file to replace or new file to make.
        moduleFilter = "*.xml"
        dialogResults = cmds.fileDialog2( fileFilter=moduleFilter, dialogStyle=2, startingDirectory=XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH ) )
    else:
        dialogResults = [ inFile ]
    
    returnDict = {}
    xmlDoc = ET.parse( dialogResults[0] )
    xmlRoot = xmlDoc.getroot()

    # Process meta nodes.
    for metanode in xmlRoot.findall( 'metanode' ):
        metaType = metanode.get( 'metaType' )
        returnDict[ 'metanode' ] = { 'name':metanode.get('name'), 'metaType':metanode.get('metaType'), 'metaClass':metanode.get('metaClass') }
        
        plugList = []
        for plug in metanode.findall( 'plug' ):
            plugList.append( { 'name':plug.get('name'), 'connected':plug.get('connected'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        returnDict[ 'metanode' ].update( { 'plugs':plugList } )
        
    # Process bit nodes.
    bitList = []
    for bit in xmlRoot.findall( 'bit' ):
        # Get shape type.
        shape = bit.findall( 'shape' )
        shapeType = shape[0].get('name')
        
        bitDict = { 'name':bit.get('name'), 'parent':bit.get('parent'), 'shapeType':shapeType }
        
        plugList = []
        for plug in bit.findall( 'plug' ):
            plugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        bitDict[ 'plugs' ] = plugList
        
        shapePlugList = []
        for plug in shape[0].findall( 'plug' ):
            shapePlugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        bitDict[ 'shape' ] = shapePlugList
        
        bitList.append( bitDict )
        
        returnDict[ 'bits' ] = bitList
    
    # Call the script.
    if inCallScript:
        pass
    else:    
        # Or just return the list.
        return returnDict

def buildFrameModule( inDir=None, inXMLFile=None ):
    # Get the XML settings for the frame module.
    dirPath = XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH+inDir )
    fullPath = dirPath+'/'+inXMLFile+'.xml'
    xmlDict = readFrameModuleXML( fullPath )
    
    # Get the metanode.
    metanode = xmlDict['metanode']
    meta = metanode['name']
    metaPlugs = metanode['plugs']
    metaType = metanode['metaType']
    metaClass = metanode['metaClass']
    
    metanode = metaNode.MetaNode( inNodeName=meta, inNodeMetaType=metaType )
    metanode = cmds.ls( selection=True )[0]
    
    metaPlugs = xmlDict['metanode']['plugs']
    for plug in metaPlugs:
        if not NodeUtility.attributeCheck( metanode, plug['name'] ):
            addPlug( metanode, plug['name'], plug['attrType'], plug['attrDataType'] )
        if plug['connected'] == 'False':
            setPlug( metanode, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
    
    # Get the bits.
    bits = xmlDict['bits']
    
    # Make a group for the module.
    for bit in bits:
        if bit['name'] == 'frame_root':
            for plug in bit['plugs']:
                if plug['name'] == 'prefix':
                    modulePrefix = plug['value']
                    break
                
    moduleGroup = '|{0}'.format( cmds.group( em=True, name=modulePrefix+'_'+metaClass ) )

    # Make each bit.
    tick = 0
    storeBitConnections = []

    while tick < len(bits):
        bitName = bits[0]['name']
        if bits[0]['parent'] == 'None':
            # This is the root bit. The | is there to represent this. We don't need it now.
            # Plus it causes problems with the full path name stuff (double ||). So we
            # remove it.
            bitParent = moduleGroup
        else:
            bitParent = moduleGroup+bits[0]['parent']
        bitPlugs = bits[0]['plugs']
        bitShape = bits[0]['shape']
        
        # Make the bit.
        if cmds.objExists( bitParent ):
            newBit = cmds.makeGLBit( name=bitName, objecttype=bits[0]['shapeType'] )            
            cmds.parent( newBit, bitParent )
            
            # From this point we use the long name for the bit. This avoids any
            # name clashes.
            fullBitName = '{0}{1}'.format( bitParent, newBit )
            # Get the frame_root for the module. We want to return this at the very end.
            if bitName == 'frame_root':
                rootFullName = fullBitName
            
            # Setup plugs for transform and custom attributes.
            for plug in bitPlugs:
                if not NodeUtility.attributeCheck( fullBitName, plug['name'] ):
                    addPlug( fullBitName, plug['name'], plug['attrType'], plug['attrDataType'] )
                    if plug['value'] is not None:
                        setPlug( fullBitName, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
                else:          
                    # Setup position and rotation.
                    setPlug( fullBitName, plug['name'], plug['value'] )
            
                # Connect plug to meta node.
                for mplug in metaPlugs:
                    if '{0}.{1}'.format(bitName, plug['name']) == mplug['value']:
                        inSourcePlug = fullBitName+'.'+plug['name']
                        inDestinationPlug = metanode+'.'+mplug['name']
                        NodeUtility.connectPlugs( inSourcePlug, inDestinationPlug )
                        
            # Setup plugs for shape attributes.
            shapeName = cmds.listRelatives( fullBitName, shapes=True )
            fullShapeName = '{0}|{1}'.format( fullBitName, shapeName[0] )
            for plug in bitShape:
                if plug['attrDataType'] == 'TdataCompound':
                    # We skip compound nodes at this stage. They are for the child arrow drawing and must be
                    # hooked up after all the objects are created.
                    connectionChild = '{0}{1}'.format( moduleGroup, plug['value'] )
                    storeBitConnections.append( { 'parent':fullBitName, 'child':connectionChild } )
                else:
                    setPlug( fullShapeName, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
                           
            bits.remove( bits[0] )
        else:
            tick = tick+1
            pass
    
    # Now do the hook ups for the child arrows.
    for i in storeBitConnections:
        setBitChild( i['parent'], i['child'] )
    
    return rootFullName

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
        sourceWorldMatrix = TransformUtility.getMatrix( inSourceObj, 'worldMatrix' )
        
        # Get the source's translation vector.
        sourceWorldTranslation = TransformUtility.getMatrixTranslation( sourceWorldMatrix )
        
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
    
        targetInverseMatrix = TransformUtility.getMatrix( inTargetObj, 'parentInverseMatrix' )
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
        targetRootBit = buildFrameModule( metaBuildFolderValue, metaClassValue )
    
        # Loop through each object in the source module.
        metaRootBit = NodeUtility.getNodeAttrSource( metaNode, 'rootBit' )[0]
        
        sourceChildBits = getFrameRootAllChildren( metaRootBit )
        targetChildBits = getFrameRootAllChildren( targetRootBit )
        
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