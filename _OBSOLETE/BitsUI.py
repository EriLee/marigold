import sys
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.NodeUtility as NodeUtility
import marigold.ui.deleteAttrUI as deleteAttrUI
import xml.etree.ElementTree as ET
import marigold.utility.XMLUtility as XMLUtility
import marigold.meta.metaNode as metaNode
import marigold.ui.SelectMetaUI as SelectMetaUI

'''
'''

class createBitsUI():
    def __init__( self, winName='createBitzUI' ):
        self.winTitle = 'Bit Editing Tools'
        self.winName = winName
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 206
        self.winHeight = 400
        self.iconWidth = 32
        self.iconHeight = 32
        
        # Window colors
        self.rowColors = [[0.4,0.4,0.4],[0.5,0.5,0.5]]
        
        # Clean up old uis before opening a new one.
        try:
            cmds.deleteUI( self.winName )
        except:
            pass
        
        # Setup the form layout.
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=False, resizeToFitChildren=False )
        self.form = cmds.formLayout()
        self.tabs = cmds.tabLayout( innerMarginWidth=5, innerMarginHeight=5 )
                
        # Attach the tabs layout to the form layout.
        cmds.formLayout( self.form, edit=True, attachForm=( (self.tabs, 'top', 0), (self.tabs, 'left', 0), (self.tabs, 'bottom', 0), (self.tabs, 'right', 0) ) )
        
        # Create each of the tabs.
        # TAB: META NODES: START
        self.tabMeta = cmds.rowColumnLayout( numberOfRows=2, width=self.winWidth )
        
        self.colMeta = cmds.rowColumnLayout( numberOfColumns=1, height=self.winHeight/2 )
        cmds.text( label='Meta Nodes', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.gridMeta = cmds.gridLayout( numberOfColumns=4, cellWidthHeight=( 50, 50 ) )        
        cmds.button( label='Basic', command=lambda b, a1='frameModule': metaNode.MetaNode( inNodeMetaType=a1 ) )
        cmds.button( label='Character', command=lambda b, a1=False: metaNode.MetaCharacter( doModel=a1 ) )
        cmds.setParent( '..' )#self.gridMeta
        cmds.setParent( '..' )#self.colMeta
        
        self.colMetaTools = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.rowMetaTools = cmds.rowColumnLayout( numberOfRows=1 )
        cmds.button( label='Meta Node List', annotation='meta node list',
                     command=lambda b: SelectMetaUI.selectMetaUI() )                       
        cmds.setParent( '..' )#self.rowMetaTools
        cmds.setParent( '..' )#self.colMetaTools

        cmds.setParent( '..' )#self.tabMeta
        # TAB: META NODES: END
        
        # TAB: BITS, START
        self.tabBits = cmds.rowColumnLayout( numberOfRows=3, width=self.winWidth )
        
        self.bitsCol = cmds.rowColumnLayout( numberOfColumns=1, height=self.winHeight/3 )
        cmds.text( label='Bit Primitives', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.bitsGrid = cmds.gridLayout( numberOfColumns=4, cellWidthHeight=( 50, 50 ) )
        cmds.button( label='Sphere', command=lambda b, a1='glSphere': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Box', command=lambda b, a1='glBox': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Cylinder', command=lambda b, a1='glCylinder': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Cone', command=lambda b, a1='glCone': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Torus', command=lambda b, a1='glTorus': cmds.makeGLBit( objecttype=a1 ) )
        cmds.setParent( '..' )#self.bitsGrid
        cmds.setParent( '..' )#self.bitsCol
        
        self.toolsCol = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Transform Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.toolRow = cmds.rowColumnLayout( numberOfRows=1 )
        cmds.iconTextButton( annotation='match translation', style='iconOnly',
                             width=self.winWidth/3, image1='icon_match_translation.png',
                             command=lambda a1='tran': TransformUtility.matchTransforms(a1) )
        cmds.iconTextButton( annotation='match rotation', style='iconOnly',
                             width=self.winWidth/3, image1='icon_match_rotation.png',
                             label='match rotation', command=lambda a1='rot': TransformUtility.matchTransforms(a1) )
        cmds.iconTextButton( annotation='match all', style='iconOnly',
                             width=self.winWidth/3, image1='icon_match_all.png',
                             label='match all', command=lambda a1='all': TransformUtility.matchTransforms(a1) )                             
        cmds.setParent( '..' )#self.toolRow
        cmds.setParent( '..' )#self.toolsCol

        self.childCol = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='General Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.childRow = cmds.rowColumnLayout( numberOfColumns=2 )
        cmds.button( label='Add Child', command=lambda b: NodeUtility.setBitChild() )
        cmds.button( label='Remove Child', command=lambda b: NodeUtility.deleteBitChild() )
        cmds.button( label='Copy Settings', command=lambda b: NodeUtility.copyBitSettings() )
        cmds.setParent( '..' )#self.childRow
        cmds.setParent( '..' )#self.childCol
        
        cmds.setParent( '..' )#self.tabBits
        # TAB: BITS, END
        
        # TAB: ATTRIBUTES, START
        self.tabAttrs = cmds.rowColumnLayout( numberOfRows=2 )
        
        # Top
        self.attrTop = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Attribute List', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        
        # Top rows.
        self.attrList = cmds.scrollLayout( horizontalScrollBarThickness=16, verticalScrollBarThickness=16, height=150 )
        self.fillAttrList()
        cmds.setParent( '..' )#attrList
        # Bottom buttons
        cmds.rowColumnLayout( numberOfColumns=2 )
        #cmds.button( label='Add Custom Attribute' )
        cmds.button( label='Delete Attributes', command=lambda b: deleteAttrUI.createDeleteAttrUI() )
        cmds.button( label='Add Selected', command=lambda b: self.addAttrsFromList() )
        cmds.separator( style='none', height=10 )
        cmds.setParent( '..' )#button columns
        cmds.setParent( '..' )#self.attrTop
        
        self.attrPresets = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Attribute Presets', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        self.presets = cmds.gridLayout( numberOfColumns=4, cellWidthHeight=( 50, 50 ) )
        self.fillAttrPresets()
        cmds.setParent( '..' )#self.presets
        cmds.setParent( '..' )#self.attrPresets
        
        cmds.setParent( '..' )#self.tabAttrs
        # TAB: ATTRIBUTES, END
        
        # TAB: XML: START
        self.tabXML = cmds.rowColumnLayout( numberOfRows=2, width=self.winWidth )
        
        self.colXML = cmds.rowColumnLayout( numberOfColumns=1, height=self.winHeight/2 )
        cmds.text( label='XML Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )        
        cmds.button( label='Save Frame Module XML', command=lambda b: FrameUtility.createFrameModuleXML() )
        cmds.setParent( '..' )#self.colXML

        cmds.setParent( '..' )#self.tabXML
        # TAB: XML: END
        
        # Added the tabs to the tab layout.
        cmds.tabLayout( self.tabs, edit=True, tabLabel=( (self.tabMeta, 'Metas'),
                                                         (self.tabBits, 'Bits'),
                                                         (self.tabAttrs, 'Attributes'),
                                                         (self.tabXML, 'XML') ) )

        # Show the window.
        cmds.showWindow( self.winName )
        
    def fillAttrList( self ):
        # Clean up UI elements for refreshing the list.
        lChildren = cmds.scrollLayout( self.attrList, query=True, childArray=True )
        if lChildren is not None:
            for c in lChildren:
                cmds.deleteUI( c )

        # Build list for UI.
        previousColor = 2
        
        attList = getAttrXML()
        for attr in attList:
            attr = [{ 'attrName':attr['name'], 'attrType':attr['attrType'], 'attrDataType':attr['attrDataType'] }]
            
            # Set the row color.
            color = 1
            if previousColor is 1:
                color = 2
                previousColor = 2
            else:
                color = 1
                previousColor = 1
                
            # Make the row.
            self.attrListColumn = cmds.rowColumnLayout( parent=self.attrList, numberOfColumns=3,
                                                       columnWidth=[(1,104),(2,50),(3,20)],
                                                       columnSpacing=[(1,2),(2,2),(3,2)],
                                                       backgroundColor=self.rowColors[color-1] )
            cmds.text( label=attr[0]['attrName'] )
            cmds.iconTextButton( annotation='Add', style='iconOnly',
                             width=16, image1='icon_plus16.png',
                             command=lambda a1=attr: addAttr( a1 ) )
            self.checkBox = cmds.checkBox( label='' )
            cmds.setParent( '..' )#self.attrListColumn

    def fillAttrPresets( self ):
        # This fills gridLayout with the appropriate buttons.        
        # Check if buttons already exist. If they do, delete them.
        gridChildren = cmds.gridLayout( self.presets, query=True, childArray=True )
        if gridChildren is not None:
            for c in gridChildren:
                cmds.deleteUI( c )
        
        presetList = getAttrXML( presets=True )
        for preset in presetList:
            presetName = preset['presetName']
            cmds.button( parent=self.presets, label=presetName,
                         annotation='Add attributes for a {0}'.format( presetName ),
                         command=lambda b, a1=presetName: self.addAttrPreset( a1 ) )
                    
    def addAttrPreset( self, inPresetName ):
        presetList = getAttrXML( presets=True )
        attrList = getAttrXML()
        for preset in presetList:
            if preset['presetName'] == inPresetName:
                presetAttrs = preset['attrs']
                for pAttr in presetAttrs:
                    for attr in attrList:
                        if pAttr == attr['name']:
                            addAttr( [{ 'attrName':attr['name'], 'attrType':attr['attrType'], 'attrDataType':attr['attrDataType'] }] )
                            pass

    def addAttrsFromList( self ):
        # Get the attribute list items in the UI.
        rows = cmds.scrollLayout( self.attrList, query=True, childArray=True )
        
        # Get the rows that are active (check box is True) and put them in a list.
        activeRows = []
        for row in rows:
            for element in cmds.rowColumnLayout( row, query=True, childArray=True ):
                elementType = cmds.objectTypeUI( element )
                if elementType == 'checkBox':
                    if cmds.checkBox( element, query=True, value=True ):
                        activeRows.append( row )
        
        # Get the attribute list from the XML file. This is used to pull the settings for a given
        # attribute type.
        attList = getAttrXML()
        
        # Now we loop through all the active items from the the list and add them to the selected
        # object.
        for row in activeRows:
            rowChildren = cmds.rowColumnLayout( row, query=True, childArray=True )
            for child in rowChildren:
                elementType = cmds.objectTypeUI( child )
                if elementType == 'staticText':
                    label = cmds.text( child, query=True, label=True )
                    for attr in attList:
                        if attr['name'] == label:
                            addAttr( [{ 'attrName':attr['name'], 'attrType':attr['attrType'], 'attrDataType':attr['attrDataType'] }] )
        
def addAttr( inAttrs ):
    selList = cmds.ls( selection=True )
    if len(selList) == 1:
        for attr in inAttrs:
            attrName = attr['attrName']
            attrType = attr['attrType']
            attrDataType = attr['attrDataType']
            if NodeUtility.attributeCheck( selList[0], attrName ):
                sys.stderr.write( 'Skip adding {0} because it already exists'.format( attrName ) )
            else:
                FrameUtility.addPlug( selList[0], attrName, attrType, attrDataType )
    
def getAttrXML( presets=False ):    
    presetPath = XMLUtility.getPresetPath( '' )
    fullPath = '{0}frames/bits/bitAttributes.xml'.format( presetPath )
    returnList = []
    xmlDoc = ET.parse( fullPath )
    xmlRoot = xmlDoc.getroot()
    
    if presets:
        presetList = xmlRoot.find( 'presets' )
        for preset in presetList.findall( 'preset' ):
            tempList = { 'presetName':preset.get('name') }
            tempList['attrs'] = []
            for attr in preset.findall( 'attr' ):
                tempList['attrs'].append( attr.get('name') )
            returnList.append( tempList )
    else:
        attrList = xmlRoot.find( 'attributes' )
        for attr in attrList.findall( 'attr' ):
            returnList.append( { 'name':attr.get('name'), 'attrType':attr.get('attrType'), 'attrDataType':attr.get('attrDataType') } )    
    return returnList
    
createBitsUI()