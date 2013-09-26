'''
Utilities for creating XML configuration files for rig controllers.

TODO:
1. Write XML file.
2. Read XML file.
3. UI for saving/rewriting XML file.
'''
import math
import os
import types
import xml.etree.ElementTree as ET
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.components as components


CONTROLLER_PRESETS_PATH = 'controllers/presets/'
FRAME_PRESETS_PATH = 'frames/presets/'
FRAME_MODULES_PATH = 'frames/modules/'

def getPresetPath( inPresetPath=CONTROLLER_PRESETS_PATH ):
    scriptPaths = mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( ';' )
    for path in scriptPaths:
        if path.find( 'marigold' ) is not -1:
            return path+'/'+inPresetPath

def getObjectShortName( inObjectName ):
    '''
    Converts a long name to a short name.
    
    @return: String. Short name of the object.
    '''
    splitName = inObjectName.split( '|' )
    return splitName[ len( splitName )-1 ]

def writeModuleXML( inRootObjectName, inModuleType, inModuleName ):
    '''
    Function for writing module xml.
    
    @param inRootObjectName: String. Name of module root object.
    @param inModuleType: String. Type of module. This determines which sub-folder the XML is saved.
    @param inModuleName: String. Name of the module XML file.
    '''
    # Get list of the module hierarchy. Root is always first
    hierarchyList = NodeUtility.getFrameRootAllChildren( inRootObjectName )
    hierarchyList.insert( 0, inRootObjectName )
    
    # START: Writing XML
    xmlLines = []
    xmlLines.append( '<data>' )
    
    for item in hierarchyList:        
        # BIT INFO
        itemName = getObjectShortName( item )        
        itemParent = NodeUtility.cleanParentFullName( item )
        itemMatrix = TransformUtility.getMatrix( item, 'matrix' )
        itemPosition = TransformUtility.getMatrixTranslation( itemMatrix, OpenMaya.MSpace.kTransform )        
        itemRotation = TransformUtility.getMatrixRotation( itemMatrix, 'eulerVector' )
        
        # START: Bit
        xmlLines.append( '\t<bit name=\"{0}\" parent=\"{1}\">'.format( itemName, itemParent ) )        
        xmlLines.append( '\t\t<plug name=\"translateX\">{0}</plug>'.format( itemPosition.x ) )
        xmlLines.append( '\t\t<plug name=\"translateY\">{0}</plug>'.format( itemPosition.y ) )
        xmlLines.append( '\t\t<plug name=\"translateZ\">{0}</plug>'.format( itemPosition.z ) )    
        xmlLines.append( '\t\t<plug name=\"rotateX\">{0}</plug>'.format( math.degrees(itemRotation.x) ) )
        xmlLines.append( '\t\t<plug name=\"rotateY\">{0}</plug>'.format( math.degrees(itemRotation.y) ) )
        xmlLines.append( '\t\t<plug name=\"rotateZ\">{0}</plug>'.format( math.degrees(itemRotation.z) ) )
        
        # SHAPE
        itemShape = NodeUtility.getDagPath( itemName ).child( 0 )
        depFn = OpenMaya.MFnDependencyNode( itemShape )
        shapeType = depFn.typeName()
        if shapeType.find( 'gl' ) != -1:
            itemShapeName = cmds.listRelatives( itemName, shapes=True, fullPath=True )[0]
            # Start shape
            xmlLines.append( '\t\t<shape name=\"{0}\">'.format( shapeType ) )
            
            # Get the shape's local position and scale.
            for attr in cmds.listAttr( itemShapeName, channelBox=True ):
                types = NodeUtility.getAttrTypes( itemShapeName, attr )
                aPlug = NodeUtility.getPlug( itemShapeName, attr )
                xmlLines.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr, types[0], types[1], NodeUtility.getPlugValue(aPlug) ) )
            
            # Get the shape's custom attributes.
            for attr in cmds.listAttr( itemShapeName, multi=True, keyable=True ):
                if attr.find( '[' ) is not -1:
                    # Special case handle array attributes. The [] needs to be removed so we can get
                    # the base name for the attribute. From there we can then loop through it's children.
                    # First we get the connection since these plugs won't return a value, but rather a
                    # connected node.
                    connection = NodeUtility.getNodeAttrSource( itemShapeName, attr )
                    bitChildren = cmds.listRelatives( itemName, type='transform', children=True, fullPath=True )
                    for child in bitChildren:
                        if child.find( connection[0] ):
                            plugValue = child
                    
                    # Now we get the compound attribute's name by removing the index brackets.
                    attrSplit = attr.split('[')
                    attr = attrSplit[0]
                else:
                    aPlug = NodeUtility.getPlug( itemShapeName, attr )
                    plugValue = NodeUtility.getPlugValue( aPlug )
                    
                types = NodeUtility.getAttrTypes( itemShapeName, attr )
                if types[0] is not False:
                    xmlLines.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr, types[0], types[1], plugValue ) )
            # End shape
            xmlLines.append( '\t\t</shape>' )
            
        # BIT COMPONENTS
        bitComponents = components.getComponents( item )
        for comp in bitComponents:
            # Component info
            compName = ''.join(i for i in comp if not i.isdigit())

            # Start component.
            xmlLines.append( '\t\t<component name=\"{0}\">'.format( compName ) )
            
            compSettings = NodeUtility.getModuleComponentSettings( comp )
            for attr in compSettings:
                types = NodeUtility.getAttrTypes( comp, attr )
                aPlug = NodeUtility.getPlug( comp, attr )
                plugValue = NodeUtility.getPlugValue( aPlug )
                xmlLines.append( '\t\t\t<plug name=\"{0}\" attrType=\"{1}\" attrDataType=\"{2}\">{3}</plug>'.format( attr, types[0], types[1], plugValue ) )
    
            xmlLines.append( '\t\t</component>' )
        # END: Bit
        xmlLines.append( '\t</bit>' )
        
    # END: Writing XML
    xmlLines.append( '</data>' )
    
    # Create the file
    startingDirectory = getPresetPath( FRAME_PRESETS_PATH )
    filePath = '{0}{1}'.format( startingDirectory, inModuleType )
    fileName = '{0}.xml'.format( inModuleName )

    newfile = file( os.path.join( filePath, fileName ), 'w')      
    for i in xmlLines:
        newfile.write( i+'\n' )
    newfile.close()

# Function for reading module xml.
def readModuleXML( inFile ):
    '''
    Processes an XML file to get the parts/settings for the module.
    
    @param inFullPath: Full directory path + filename + extension of the XML file.
    @return: A dictionary.
    '''
    returnDict = {}
    xmlDoc = ET.parse( inFile )
    xmlRoot = xmlDoc.getroot()
    
    bitList = []# List of each bit.
    for bit in xmlRoot.findall( 'bit' ):
        # Get bit shape
        shape = bit.findall( 'shape' )
        shapeType = shape[0].get('name')
        
        bitDict = { 'name':bit.get('name'), 'parent':bit.get('parent'), 'shapeType':shapeType }
        
        # Get all the bit's plugs.
        plugList = []
        for plug in bit.findall( 'plug' ):
            plugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        bitDict[ 'plugs' ] = plugList
        
        # Get all the shape's plugs.
        shapePlugList = []
        for plug in shape[0].findall( 'plug' ):
            shapePlugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
        bitDict[ 'shape' ] = shapePlugList
        
        # Get all the components on the bit.
        components = bit.findall( 'component' )
        componentList = []
        for comp in components:
            comps = { 'name':comp.get('name') }
            componentPlugList = []
            for plug in comp.findall( 'plug' ):
                componentPlugList.append( { 'name':plug.get('name'), 'attrType':plug.get('attrType'), 'attrDataType':plug.get('attrDataType'), 'value':plug.text } )
            comps['plugs'] = componentPlugList
            componentList.append( comps )
        bitDict[ 'components' ] = componentList
        
        # Add the bit to the bit list.
        bitList.append( bitDict )
        
    returnDict[ 'bits' ] = bitList
    
    return returnDict

def loadModule( inFolder, inFileName ):
    '''
    Loads a module into the scene.
    
    @param inFolder: String. Name for the sub-folder the module XML is located.
    @param inFileName: String. Name of the module XML. 
    '''
    dirPath = getPresetPath( FRAME_PRESETS_PATH+inFolder )
    fullPath = dirPath+'/'+inFileName+'.xml'
    xmlFile = readModuleXML( fullPath )
    
    # Create a temp group to put the module inside while creating.
    moduleGroup = '|{0}'.format( cmds.group( em=True, name='TEMP' ) )
    
    # Grab all the bits.
    bits = xmlFile['bits']
    
    # Make each bit.
    tick = 0
    storeBitConnections = []

    while tick < len(bits):
        if bits[0]['parent'] == 'None':
            bitParent = moduleGroup
        else:
            bitParent = moduleGroup+bits[0]['parent']
        
        bitName = bits[0]['name']
        bitPlugs = bits[0]['plugs']
        shapePlugs = bits[0]['shape']
        bitComponents = bits[0]['components']
        
        # Make the bit.
        if cmds.objExists( bitParent ):
            newBit = cmds.makeGLBit( name=bitName, objecttype=bits[0]['shapeType'] )            
            cmds.parent( newBit, bitParent )
            
            # From this point we use the long name for the bit. This avoids any
            # name clashes.
            fullBitName = '{0}{1}'.format( bitParent, newBit )
            
            # Setup plugs for transform and custom attributes.
            for plug in bitPlugs:
                if not NodeUtility.attributeCheck( fullBitName, plug['name'] ):
                    NodeUtility.addPlug( fullBitName, plug['name'], plug['attrType'], plug['attrDataType'] )
                    if plug['value'] is not None:
                        NodeUtility.setPlug( fullBitName, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
                else:          
                    # Setup position and rotation.
                    NodeUtility.setPlug( fullBitName, plug['name'], plug['value'] )
            
            # Setup plugs for shape attributes.
            shapeName = cmds.listRelatives( fullBitName, shapes=True )
            fullShapeName = '{0}|{1}'.format( fullBitName, shapeName[0] )
            for plug in shapePlugs:
                if plug['attrDataType'] == 'TdataCompound':
                    # We skip compound nodes at this stage. They are for the child arrow drawing and must be
                    # hooked up after all the objects are created.
                    connectionChild = '{0}{1}'.format( moduleGroup, plug['value'] )
                    storeBitConnections.append( { 'parent':fullBitName, 'child':connectionChild } )
                else:
                    NodeUtility.setPlug( fullShapeName, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
            
            # Setup bit components.
            for comp in bitComponents:
                compType = comp['name']
                
                # We have to special case components that have additional kwargs.
                if compType == 'CurveControlComponent':
                    # Handle curve control component type.
                    for plug in comp['plugs']:
                        if plug['name'] == 'curveType':
                            curveType = plug['value']
                    newComp = components.addComponentToObject( compType, inObject=fullBitName, curveType=curveType )
                else:
                    # Handle basic component.
                    newComp = components.addComponentToObject( compType, inObject=fullBitName )

                for plug in comp['plugs']:
                    NodeUtility.setPlug( newComp.name(), plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
                    
            # Remove the bit from the list
            bits.remove( bits[0] )
            
    # Now do the hook ups for the child arrows.
    for i in storeBitConnections:
        NodeUtility.setBitChild( i['parent'], i['child'] )

'''

OLD XML SHIT. REMOVE!!!!!!!!

'''
def createControlXML():
    '''
    Creates/updates module XML file.
    '''
    # Controller attributes.
    cAttr = [ 'color',
              'localPosition',
              'rotate',
              'transparency',
              'backAlpha',
              'lineWidth',
              'width',
              'height',
              'depth',
              'drawType',
              'topFrontRight',
              'topFrontLeft',
              'topBackRight',
              'topBackLeft',
              'botFrontRight',
              'botFrontLeft',
              'botBackRight',
              'botBackLeft' ]
        
    # Browse for file to replace or new file to make.
    moduleFilter = "*.xml"
    dialogResults = cmds.fileDialog2( fileFilter=moduleFilter, dialogStyle=2, startingDirectory=getPresetPath( CONTROLLER_PRESETS_PATH ) )
    tempPath = dialogResults[0].split( '/' )
    fileName = tempPath[ len( tempPath )-1 ]
    filePath = dialogResults[0].rstrip( fileName )
    objName = fileName.split( '.' )[0]

    # Get the selected object. Only takes one object.
    sel = cmds.ls( selection=True, dagObjects=True, allPaths=True, transforms=True )
    
    # Build a list for each line in an XML file.
    xmlList = []
    xmlList.append( '<data>' )

    # Grab the shape node.
    transNode = NodeUtility.getDagPath( sel[0] )
    shapeNode = transNode.child( 0 )
    MFnDagNode = OpenMaya.MFnDagNode()
    MFnDagNode.setObject( shapeNode )

    # Get the attributes and format them for the XML file.
    if MFnDagNode.typeName() == 'ControlBox':
        # Create a <control>.
        xmlList.append( '\t<control name=\"{0}\" type=\"{1}\">'.format( sel[0], MFnDagNode.typeName() ) )
        xmlList.append( '\t</control>' )
        
        for a in cAttr:
            # Get the attributes.
            xmlList.insert( len( xmlList ) - 1, '\t\t<attr name=\"{0}">'.format( a ) )
            plug = NodeUtility.getPlug( MFnDagNode.name(), a )
            plugValue = NodeUtility.getPlugValue( plug )
            if isinstance( plugValue, types.ListType ):
                for i in plugValue:
                    xmlList.insert( len( xmlList ) - 1, '\t\t\t<value>{0}</value>'.format( i ) )
            else:
                xmlList.insert( len( xmlList ) - 1, '\t\t\t<value>{0}</value>'.format( plugValue ) )
            xmlList.insert( len( xmlList ) - 1, '\t\t</attr>' )
        
    # close the data tag
    xmlList.append( '</data>' )

    # create new file
    newfile = file( os.path.join( filePath, fileName ), 'w')      
    for i in xmlList:
        newfile.write( i+'\n' )
    newfile.close()

def readControlXML( inFile=None ):
    '''
    Processes an XML file to get the parts/settings for the module.
    
    @param inFullPath: Full directory path + filename + extension of the XML file.
    @return: A dictionary.
    
    <data>
        <control name="" type="">
            <attr name="">
                <value>#</value>
            </attr>
        </control>
    </data>
    '''
    if inFile is None:
        # Browse for file to replace or new file to make.
        moduleFilter = "*.xml"
        dialogResults = cmds.fileDialog2( fileFilter=moduleFilter, dialogStyle=2, startingDirectory=getPresetPath( CONTROLLER_PRESETS_PATH ) )
    else:
        dialogResults = [ inFile ]
    
    returnDict = {}
    xmlDoc = ET.parse( dialogResults[0]  )
    xmlRoot = xmlDoc.getroot()
    for object in xmlRoot.findall( 'control' ):
        # Add the control name to the list.
        returnDict[ 'controller' ] = { 'name':object.get( 'name' ), 'type':object.get( 'type' ) }
        for attr in object.findall( 'attr' ):
            numValues = attr.findall( 'value' )
            if len( numValues ) > 1:
                valueList = []
                for value in numValues:
                    valueList.append( value.text )
            else:
                valueList = numValues[0].text
            returnDict[ attr.get( 'name' ) ] = { 'value':valueList }
                
    # return the list.
    return returnDict

def createControlFromXML( inType=None, inSubType=None, inControlName=None ):
    if inType is None:    
        # Read the XML file.
        attrList = readControlXML()
    else:
        startingDirectory = getPresetPath( CONTROLLER_PRESETS_PATH )
        presetPath = startingDirectory+inType+'/'+inSubType+'.xml'
        attrList = readControlXML( presetPath )
        
    # Create the control.
    if inControlName is None:
        ctName = attrList[ 'controller' ][ 'name' ]
    else:
        ctName = inControlName
        
    # Create the control.
    cmds.rigController( name=ctName, 
                    position=( float( attrList[ 'localPosition' ][ 'value' ][0] ), float( attrList[ 'localPosition' ][ 'value' ][1] ), float( attrList[ 'localPosition' ][ 'value' ][2] ) ),
                    lineWidth=int( attrList[ 'lineWidth' ][ 'value' ] ),
                    rotate=( float( attrList[ 'rotate' ][ 'value' ][0] ), float( attrList[ 'rotate' ][ 'value' ][1] ), float( attrList[ 'rotate' ][ 'value' ][2] ) ),
                    alpha=float( attrList[ 'transparency' ][ 'value' ] ),
                    backAlpha=float( attrList[ 'backAlpha' ][ 'value' ] ),
                    color=( float( attrList[ 'color' ][ 'value' ][0] ), float( attrList[ 'color' ][ 'value' ][1] ), float( attrList[ 'color' ][ 'value' ][2] ) ),
                    drawType=int( attrList[ 'drawType' ][ 'value' ] ),
                    width=float( attrList[ 'width' ][ 'value' ] ),
                    height=float( attrList[ 'height' ][ 'value' ] ),
                    depth=float( attrList[ 'depth' ][ 'value' ] ),
                    topFrontRight=( float( attrList[ 'topFrontRight' ][ 'value' ][0] ), float( attrList[ 'topFrontRight' ][ 'value' ][1] ), float( attrList[ 'topFrontRight' ][ 'value' ][2] ) ),
                    topFrontLeft=( float( attrList[ 'topFrontLeft' ][ 'value' ][0] ), float( attrList[ 'topFrontLeft' ][ 'value' ][1] ), float( attrList[ 'topFrontLeft' ][ 'value' ][2] ) ),
                    topBackRight=( float( attrList[ 'topBackRight' ][ 'value' ][0] ), float( attrList[ 'topBackRight' ][ 'value' ][1] ), float( attrList[ 'topBackRight' ][ 'value' ][2] ) ),
                    topBackLeft=( float( attrList[ 'topBackLeft' ][ 'value' ][0] ), float( attrList[ 'topBackLeft' ][ 'value' ][1] ), float( attrList[ 'topBackLeft' ][ 'value' ][2] ) ),
                    botFrontRight=( float( attrList[ 'botFrontRight' ][ 'value' ][0] ), float( attrList[ 'botFrontRight' ][ 'value' ][1] ), float( attrList[ 'botFrontRight' ][ 'value' ][2] ) ),
                    botFrontLeft=( float( attrList[ 'botFrontLeft' ][ 'value' ][0] ), float( attrList[ 'botFrontLeft' ][ 'value' ][1] ), float( attrList[ 'botFrontLeft' ][ 'value' ][2] ) ),
                    botBackRight=( float( attrList[ 'botBackRight' ][ 'value' ][0] ), float( attrList[ 'botBackRight' ][ 'value' ][1] ), float( attrList[ 'botBackRight' ][ 'value' ][2] ) ),
                    botBackLeft=( float( attrList[ 'botBackLeft' ][ 'value' ][0] ), float( attrList[ 'botBackLeft' ][ 'value' ][1] ), float( attrList[ 'botBackLeft' ][ 'value' ][2] ) ) )
    
def applyXMLtoControl():
    # Get the selected object. Only takes one object.
    sel = cmds.ls( selection=True, dagObjects=True, allPaths=True, transforms=True )
    
    # Get the XML file.
    attrList = readControlXML()
    
    # Grab the shape node.
    transNode = NodeUtility.getDagPath( sel[0] )
    MFnDepNode = OpenMaya.MFnDependencyNode()
    MFnDepNode.setObject( transNode.child( 0 ) )
    
    if MFnDepNode.typeName() == 'ControlBox':        
        # Update plugs with values, if any, from the command.
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'color' ),
                                  [ float( attrList[ 'color' ][ 'value' ][0] ), float( attrList[ 'color' ][ 'value' ][1] ), float( attrList[ 'color' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'localPosition' ),
                                  [ float( attrList[ 'localPosition' ][ 'value' ][0] ), float( attrList[ 'localPosition' ][ 'value' ][1] ), float( attrList[ 'localPosition' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'rotate' ),
                                  [ float( attrList[ 'rotate' ][ 'value' ][0] ), float( attrList[ 'rotate' ][ 'value' ][1] ), float( attrList[ 'rotate' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'transparency' ), float( attrList[ 'transparency' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'backAlpha' ), float( attrList[ 'backAlpha' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'lineWidth' ), int( attrList[ 'lineWidth' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'width' ), float( attrList[ 'width' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'height' ), float( attrList[ 'height' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'depth' ), float( attrList[ 'depth' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'drawType' ), int( attrList[ 'drawType' ][ 'value' ] ) )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'topFrontRight' ),
                                  [ float( attrList[ 'topFrontRight' ][ 'value' ][0] ), float( attrList[ 'topFrontRight' ][ 'value' ][1] ), float( attrList[ 'topFrontRight' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'topFrontLeft' ),
                                  [ float( attrList[ 'topFrontLeft' ][ 'value' ][0] ), float( attrList[ 'topFrontLeft' ][ 'value' ][1] ), float( attrList[ 'topFrontLeft' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'topBackRight' ),
                                  [ float( attrList[ 'topBackRight' ][ 'value' ][0] ), float( attrList[ 'topBackRight' ][ 'value' ][1] ), float( attrList[ 'topBackRight' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'topBackLeft' ),
                                  [ float( attrList[ 'topBackLeft' ][ 'value' ][0] ), float( attrList[ 'topBackLeft' ][ 'value' ][1] ), float( attrList[ 'topBackLeft' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'botFrontRight' ),
                                  [ float( attrList[ 'botFrontRight' ][ 'value' ][0] ), float( attrList[ 'botFrontRight' ][ 'value' ][1] ), float( attrList[ 'botFrontRight' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'botFrontLeft' ),
                                  [ float( attrList[ 'botFrontLeft' ][ 'value' ][0] ), float( attrList[ 'botFrontLeft' ][ 'value' ][1] ), float( attrList[ 'botFrontLeft' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'botBackRight' ),
                                  [ float( attrList[ 'botBackRight' ][ 'value' ][0] ), float( attrList[ 'botBackRight' ][ 'value' ][1] ), float( attrList[ 'botBackRight' ][ 'value' ][2] ) ] )
        NodeUtility.setPlugValue( MFnDepNode.findPlug( 'botBackLeft' ),
                                  [ float( attrList[ 'botBackLeft' ][ 'value' ][0] ), float( attrList[ 'botBackLeft' ][ 'value' ][1] ), float( attrList[ 'botBackLeft' ][ 'value' ][2] ) ] )

def getXMLInFolder( inPresetPath ):
    '''
    Finds all XML files in a directory.
    @param inPresetPath: Preset path to search.
    @return: List of module names.
    '''
    # Search the dir for all files of type XML
    fileExt = '.xml'
    fileList = []
    fullPath = getPresetPath( inPresetPath )
    for files in os.listdir( fullPath ):
        if files.endswith( fileExt ): fileList.append( files )
    
    # Get rid of the file extension
    tempList = []
    for i in fileList:
        tempName = i.split( '.' )
        tempList.append( tempName[0] )
        
    # Return the list of names
    return tempList