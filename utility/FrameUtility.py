import math
import os
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.utility.GeneralUtility as GeneralUtility

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
    # Convert the value.
    newValue = convertAttrString( inAttrDataType, inPlugValue )
    if inAttrDataType == 'typed':
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
    if inAttrDataType == 'long':
        return int( inValue )
    elif inAttrDataType == 'typed':
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
    tempDict = {}
    for attr in cmds.listAttr( inFrameBit, userDefined=True ):
        plug = NodeUtility.getPlug( inFrameBit, attr )
        plugValue = NodeUtility.getPlugValue( plug )
        tempDict[ attr ] = plugValue
    return tempDict

def getFrameRootAllChildren( inFrameRootName ):
    '''
    Gets all descendants of a frame root.
    
    @param inFrameRootName: String. Name of frame root object.
    @return: List of children. Ordered from highest to lowest in the hierarchy.
    '''
    children = cmds.listRelatives( inFrameRootName, type='transform', allDescendents=True )
    tempList = []
    for child in children:
        #print 'child: {0}'.format( child )
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
        print depFn.name()
        
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
    parentSplit = parent[0].split('|')
    parentSplit.pop(0)
    parentSplit.pop(0)
    return '|'+'|'.join( parentSplit )

def getAttrTypes( inNode, inAttr ):
    '''
    Gets the attribute's attr type and data type. These are needed for adding attributes
    to a node.
    
    @param inNode: String. Name of node.
    @param inAttr: String. Name of attribute.
    @return: List. Attribute Type and Attribute Data Type.
    '''
    attrDataType = cmds.addAttr( inNode+'.'+inAttr, query=True, attributeType=True )
    
    if attrDataType in [ 'long', 'double', 'bool', 'enum' ]: attrType = 'attributeType'
    elif attrDataType == 'typed': attrType = 'dataType'
    
    return [ attrType, attrDataType ]
    
def createFrameModuleXML():
    # Browse for file to replace or new file to make.
    moduleFilter = "*.xml"
    dialogResults = cmds.fileDialog2( fileFilter=moduleFilter, dialogStyle=2, startingDirectory=XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH ) )
    tempPath = dialogResults[0].split( '/' )
    fullFileName = tempPath[ len( tempPath )-1 ]
    filePath = dialogResults[0].rstrip( fullFileName )
    fileName = fullFileName.split( '.' )[0]
    
    print 'filename: {0}'.format(fullFileName)
    print 'filePath: {0}'.format(filePath)
    print 'objName: {0}'.format(fileName)
    
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
            xmlList.append( '\t\t<plug name=\"{0}\" connected=\"{1}\">{2}</plug>'.format( attr,
                                                                                          True,
                                                                                          connection[0]+'.'+connection[1] ) )
        else:
            xmlList.append( '\t\t<plug name=\"{0}\" connected=\"{1}\">{2}</plug>'.format( attr,
                                                                                          False,
                                                                                          NodeUtility.getPlugValue( plug ) ) )            
            
    xmlList.append( '\t</metanode>' )
    
    # Get the root bit of the frame module.
    rootBit = NodeUtility.getNodeAttrSource( node, 'rootBit' )
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
    xmlList.append( '\t</bit>')

    # Get all of the root's children.
    children = getFrameRootAllChildren( rootBit[0] )
    for child in children:
        # Bit name.
        bitName = child
        parent = cleanParentFullName( child )
        childFrameAttrs = getFrameBitSettings( child )
        
        xmlList.append( '\t<bit name=\"{0}\" parent=\"{1}\">'.format( bitName, parent ) )
    
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
            plugList.append( { 'name':plug.get('name'), 'connected':plug.get('connected'), 'value':plug.text } )
        returnDict[ 'metanode' ].update( { 'plugs':plugList } )
        
    # Process bit nodes.
    bitList = []
    for bit in xmlRoot.findall( 'bit' ):
        bitDict = { 'name':bit.get('name'), 'parent':bit.get('parent') }
        
        plugList = []
        for plug in bit.findall( 'plug' ):
            plugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        bitDict[ 'plugs' ] = plugList
        
        bitList.append( bitDict )
        
        returnDict[ 'bits' ] = bitList
    
    # Call the script.
    if inCallScript:
        pass
    else:    
        # Or just return the list.
        return returnDict

def buildFrameModule( inDir=None, inXMLFile=False ):
    # Imports
    import marigold.frames.bits.bits as Bits
    
    # Get the XML settings for the frame module.
    dirPath = XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH+inDir )
    fullPath = dirPath+'/'+inXMLFile+'.xml'
    xmlDict = readFrameModuleXML( fullPath )
    
    # Get the metanode.
    metanode = xmlDict['metanode']
    meta = metanode['name']
    metaPlugs = metanode['plugs']
    
    # Build the node.
    buildModule = GeneralUtility.importModule( 'marigold.frames.modules.'+inDir+'.'+inXMLFile )
    metanode = buildModule.MetaFrameFKIKArm()
    # Need the node created, which points to the custom class.
    # Till I figure a way to get the name through the API I'm going to use
    # the fact that the node is selected after creation.
    metanode = cmds.ls( selection=True )[0]
    
    # Get the bits.
    bits = xmlDict['bits']
    
    # Make a group for the module.
    for bit in bits:
        if bit['name'] == 'frame_root':
            for plug in bit['plugs']: 
                if plug['name'] == 'prefix':
                    modulePrefix = plug['value']
    moduleGroup = '|'+cmds.group( em=True, name=modulePrefix+'_fkikArm' )

    # Make each bit.
    tick = 0
    while tick < len(bits):
        bitName = bits[0]['name']
        bitParent = moduleGroup+bits[0]['parent']
        bitPlugs = bits[0]['plugs']
        for plug in bitPlugs:
            if plug['name'] == 'bitType':
                bitType = plug['value']
        
        # Make the bit.
        if bitParent == 'None' or cmds.objExists( bitParent ):
            newBit = Bits.frameBits( bitType, bitName )
            cmds.parent( newBit, bitParent )
            
            # From this point we use the long name for the bit. This avoids any
            # name clashes.
            fullBitName = bitParent+'|'+bitName 
            
            # Setup plugs.
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
                    if bitName+'.'+plug['name'] == mplug['value']:
                        inSourcePlug = fullBitName+'.'+plug['name']
                        inDestinationPlug = metanode+'.'+mplug['name']
                        NodeUtility.connectPlugs( inSourcePlug, inDestinationPlug )
            
            bits.remove( bits[0] )
        else:
            tick = tick+1
            pass