'''
Utilities for creating XML configuration files for rig controllers.

TODO:
1. Write XML file.
2. Read XML file.
3. UI for saving/rewriting XML file.
'''
import os
import re
import types
import xml.etree.ElementTree as ET
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

CONTROLLER_PRESETS_PATH = 'controllers/presets/'
FRAME_PRESETS_PATH = 'frames/presets/'
FRAME_MODULES_PATH = 'frames/modules/'

def getPresetPath( inPresetPath=CONTROLLER_PRESETS_PATH ):
    scriptPaths = mel.eval( 'getenv MAYA_SCRIPT_PATH' ).split( ';' )
    for path in scriptPaths:
        if path.find( 'marigold' ) is not -1:
            return path+'/'+inPresetPath
    
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