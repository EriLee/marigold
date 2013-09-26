import re
import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.FrameUtility as FrameUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.meta.componentNodes as componentNodes

class createModuleUI():    
    def __init__( self, winName='createModuleUI' ):
        self.winTitle = 'Module UI'
        self.winName = winName     
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 400
        self.winHeight = 600
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
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=True, resizeToFitChildren=True )
        
        # MENU
        self.menuBar = cmds.menuBarLayout()
        self.updateTopMenu( 'Bits' )
        cmds.setParent( '..' )#self.menuBar
        
        # MAIN BODY
        self.mainColumn = cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 5) )
        
        # OPTION MENU
        cmds.columnLayout( width=200 )
        self.modeSelect = cmds.optionMenu( width=100, changeCommand=lambda b:self.updateUI(b) )
        cmds.menuItem( label='Bits' )
        cmds.menuItem( label='Component' )
        cmds.menuItem( label='Module' )
        cmds.menuItem( label='Character' )
        cmds.setParent( '..' )
        
        # AUTO FILL AREA
        self.fillArea = cmds.columnLayout( adjustableColumn=True, columnAttach=( 'both', 0 ) )
        cmds.setParent( '..' )#self.fillArea
        
        cmds.setParent( '..' )#self.mainColumn
        
        # Show the window.
        # Set up initial fill area
        self.updateUI( 'Bits' )
        cmds.showWindow( self.winName )
        #allowedAreas = ['right', 'left']
        #cmds.dockControl( label=self.winTitle, area='right', floating=True, content=self.mainWindow, allowedArea=allowedAreas )
    
    def updateTopMenu( self, inMode ):
        # Delete the existing menu bar's content.
        barChildren = cmds.menuBarLayout( self.menuBar, query=True, menuArray=True )
        if barChildren is not None:
            for child in barChildren:
                cmds.deleteUI( child )        
        
        # Now fill the menu layout with the active set.
        if inMode == 'Bits':
            self.menuEdit = cmds.menu( parent=self.menuBar, label='Edit' )
            cmds.menuItem( parent=self.menuEdit, label='Copy Bit Settings',
                           annotation='Copy one bit\'s setting to another.',
                           command=lambda b:FrameUtility.copyBitSettings() )
            cmds.menuItem( parent=self.menuEdit, label='Add Child',
                           annotation='Add child bit to another bit.',
                           command=lambda b:FrameUtility.setBitChild() )
            cmds.menuItem( parent=self.menuEdit, label='Delete Child',
                           annotation='Remove child bit from selected bit.',
                           command=lambda b:FrameUtility.deleteBitChild() )
            
        elif inMode == 'Component':
            self.menuJoints = cmds.menu( parent=self.menuBar, label='Joints' )
            cmds.menuItem( parent=self.menuJoints, label='Joint', annotation='Creates a node of type jointComponentNode',
                           command=lambda b, a1='jointComponentNode':self.addComponentToObject(a1) )
            
            self.menuControls = cmds.menu( parent=self.menuBar, label='Controls' )
            cmds.menuItem( parent=self.menuControls, label='TEMP', annotation='TEMP' )
            
            self.menuDeformers = cmds.menu( parent=self.menuBar, label='Deformers' )
            cmds.menuItem( parent=self.menuDeformers, label='TEMP', annotation='TEMP' )
            
            self.menuConstraints = cmds.menu( parent=self.menuBar, label='Constraints' )
            cmds.menuItem( parent=self.menuConstraints, label='TEMP', annotation='TEMP' )
            
        elif inMode == 'Module':
            self.menuFile = cmds.menu( parent=self.menuBar, label='File' )
            cmds.menuItem( parent=self.menuFile, label='Save Module XML',
                           annotation='Save the selected frame module to XML.',
                           command=lambda b:FrameUtility.createFrameModuleXML() )
            
        elif inMode == 'Character':
            self.menuEdit = cmds.menu( parent=self.menuBar, label='Character Item' )
            cmds.menuItem( parent=self.menuEdit, label='TEMP', annotation='TEMP' )
    
    def addComponentToObject( self, inClassType ):
        '''
        '''
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) is 1:
            prevSel = selList[0]
            newNode = componentNodes.jointComponentNode().createCompNode( inClassType )
            # Add the component attribute to the object.
            FrameUtility.addPlug( selList[0], newNode.name(), 'attributeType', 'message' )
            #cmds.addAttr( inObject, longName='jointComponent', attributeType='message', storable=False )
            nodePlug = '{0}.parentName'.format( newNode.name() )
            objectPlug = '{0}.{1}'.format( selList[0], newNode.name() )
            NodeUtility.connectPlugs( objectPlug, nodePlug )
            cmds.select( prevSel )
            
    def updateUI( self, inSelection ):
        '''
        UPDATES THE TOP MENU WHEN THE DROPDOWN IS CHANGED.
        '''
        # Update the top menu.
        self.updateTopMenu( inSelection )
        
        # Update the body.
        # Clean up the compArea layout prior to adding new children by
        # removing the previously selected bit's information from the UI.
        mainChildren = cmds.columnLayout( self.fillArea, query=True, childArray=True )
        
        if mainChildren is not None:
            for child in mainChildren:
                cmds.deleteUI( child )
                
        if inSelection == 'Bits':
            self.bitsGUI()
        elif inSelection == 'Component':
            self.componentsGUI()
        elif inSelection == 'Module':
            self.moduleGUI()
        elif inSelection == 'Character':
            self.characterGUI()

# ===
# BIT GUI SECTION: START
# ===        
    def bitsGUI( self ):
        col = cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 5), parent=self.fillArea )
        cmds.separator( style='none', height=4, width=413 )
        
        # Primitives section.
        cmds.text( label='BIT PRIMITIVES', height=20, font='boldLabelFont', backgroundColor=[0.2,0.2,0.2] )
        cmds.separator( style='none', height=5 )
        cmds.gridLayout( numberOfColumns=5, cellWidthHeight=( 50, 50 ) )
        cmds.button( label='Sphere', command=lambda b, a1='glSphere': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Box', command=lambda b, a1='glBox': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Cylinder', command=lambda b, a1='glCylinder': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Cone', command=lambda b, a1='glCone': cmds.makeGLBit( objecttype=a1 ) )
        cmds.button( label='Torus', command=lambda b, a1='glTorus': cmds.makeGLBit( objecttype=a1 ) )
        cmds.setParent( '..' )#gridLayout
        cmds.separator( style='none', height=10 )
        
        # Transform section.
        cmds.text( label='TRANSFORM TOOLS', height=20, font='boldLabelFont', backgroundColor=[0.2,0.2,0.2] )
        cmds.separator( style='none', height=5 )
        cmds.gridLayout( numberOfColumns=3, cellWidthHeight=( 50, 50 ) )
        cmds.iconTextButton( annotation='match translation', style='iconOnly',
                             image1='icon_match_translation.png',
                             command=lambda a1='tran': TransformUtility.matchTransforms(a1) )
        cmds.iconTextButton( annotation='match rotation', style='iconOnly',
                             image1='icon_match_rotation.png',
                             label='match rotation', command=lambda a1='rot': TransformUtility.matchTransforms(a1) )
        cmds.iconTextButton( annotation='match all', style='iconOnly',
                             image1='icon_match_all.png',
                             label='match all', command=lambda a1='all': TransformUtility.matchTransforms(a1) )
        cmds.setParent( '..' )#gridLayout
        cmds.separator( style='none', height=10 )
        
        cmds.setParent( '..' )#col 

# ===
# BIT GUI SECTION: END
# ===

# ===
# COMPONENT GUI SECTION: START
# ===
    def componentsGUI( self, inBit=None ):
        '''
        Creates the components GUI.
        '''
        if inBit is None:
            components = None
        else:
            # Get the components of the selected bit.
            components = FrameUtility.getFrameBitSettings( inBit )
        
        # Clean up the compArea layout prior to adding new children by
        # removing the previously selected bit's information from the UI.
        mainChildren = cmds.columnLayout( self.fillArea, query=True, childArray=True )
        
        if mainChildren is not None:
            for child in mainChildren:
                cmds.deleteUI( child )
        
        col = cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 5), parent=self.fillArea )
        
        # HIGHLIGHTED
        cmds.separator( style='none', height=4, width=413 )
        self.selName = cmds.text( label=str.upper( 'nothing selected' ), height=20, font='boldLabelFont', backgroundColor=[0.2,0.2,0.2] )
        cmds.separator( style='none', height=10 )        
        
        # If the newly selected bit has components then update the UI to show them.
        # Check to see if any of the components are connected to a meta node.
        # We do this check so that we don't create a bunch of UI elements
        # unnecessarily.
        if components is not None and self.metaNodeCheck( inBit, components ):
            # Create the scroll layout.
            mainScroll = cmds.scrollLayout( parent=col )
            
            # Loop through each component on the bit.
            for comName in components:
                # Check to see if the component is connected to a meta node.
                metaNode = NodeUtility.getNodeAttrDestination( inBit, comName )
                if metaNode:
                    # It has a meta node.
                    # Get the meta node parameters.                
                    metaParameters = FrameUtility.getFrameBitSettings( metaNode[0] )
                    
                    # Make the component UI elements.
                    frameOne = cmds.frameLayout( parent=mainScroll, borderStyle='out', label=comName, collapsable=True )
                    
                    cmds.popupMenu()
                    #bit name, component name, meta node name
                    cmds.menuItem( label='Delete Component', command=lambda b, a1=inBit, a2=comName, a3=metaNode[0]:self.deleteComponent(a1, a2, a3) )
                    cmds.menuItem( label='Build Component', command=lambda b, a1=metaNode[0]:self.buildComponent(a1) )
                    
                    compColumn = cmds.rowColumnLayout( numberOfColumns=1 )
                    
                    # Loop through the parameters and add them to the component UI.
                    for param in metaParameters:
                        #print isinstance(param, unicode)
                        if not( param == u'parentName' or param == u'classType' ):
                            propRow = cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,100),(2,100),(3,40),(4,40)],
                                              columnSpacing=[(1,10),(2,10),(3,10),(4,2)] )
                            cmds.text( label=param, align='left' )
                            cmds.textField( text=metaParameters[param], enterCommand=lambda b, a1=metaNode[0], a2=param:self.updateComponentParameter(a1, a2, b) )
                            cmds.setParent( '..' )#propRow
                            
                    cmds.setParent( '..' )#compColumn
                    cmds.setParent( '..' )#frameOne                
                cmds.setParent( '..' )#mainScroll
        cmds.setParent( '..' )#col
        
        # Selection script job
        self.selJob = cmds.scriptJob( event=[ 'SelectionChanged', self.onSelectionChange ],
                                      parent=col, protected=True )
    
    def deleteComponent( self, inBit, inCompName, inCompNode ):
        '''
        Deletes the selected component from the object. Used in right-click menu
        for components GUI.
        @param inBit: String. Name of object.
        @param inCompName: String. Name of component plug.
        @param inCompNode: String. Name of component node.
        '''
        cmds.deleteAttr( '{0}.{1}'.format( inBit, inCompName ) )
        cmds.delete( inCompNode )
        cmds.select( inBit )
        # DISABLED FOR NOW. FOR SOME REASON THIS CRASHES MAYA. SEEMS LIKE IT MIGHT
        # BE A QT ERROR.
        #self.onSelectionChange()
        
    def buildComponent( self, inCompNode ):
        '''
        Runs the build function of the component node.
        @param inCompNode: String. Component class name.
        '''
        # Remove any appended number from the node name.
        number = re.search(r'\d+', inCompNode)
        if number:
            className = inCompNode.split( str(number.group()) )[0]
        else:
            className = inCompNode
        # Get the node's class.
        c = componentNodes.str_to_class( className )
        node = c( inCompNode )
        # Run it's build function.
        node.buildNode (node.name() )
        
    def onSelectionChange( self ):
        '''
        Function called by the scripted event in componentsGUI().
        Updates the componentGUI whenever the user selects a different object.
        '''
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) == 1:
            shortName = selList[0].split( '|' )
            self.componentsGUI( inBit=selList[0] )# Update the components GUI.
            cmds.text( self.selName, edit=True, label=shortName[ len(shortName)-1 ] )# Update the selected object text.
        elif len( selList ) > 1:
            self.componentsGUI( inBit=None )
            cmds.text( self.selName, edit=True, label=str.upper( 'select only one module bit' ) )
        else:
            self.componentsGUI( inBit=None )
            cmds.text( self.selName, edit=True, label=str.upper( 'nothing selected' ) )
            
    def metaNodeCheck( self, inObj, inComponents ):
        '''
        Checks if the component plug of an object has a meta node connected.
        @param inObj: String. Name of the selected object.
        @param inComponents: List of connected components to the selected object.
        '''
        for comName in inComponents:
            metaNode = NodeUtility.getNodeAttrDestination( inObj, comName )
            if metaNode:
                return True
        return False
    
    def updateComponentParameter( self, inCompNode, inParaName, newValue ):
        '''
        Updates the component node's parameter.
        @param inCompNode: String. Name of the component node.
        @param inParaName: String. Name of the parameter on the component node.
        @param newValue: STRING? Value of the parameter.
        '''
        node = componentNodes.baseComponentNode( node=inCompNode )
        node.setAttribute( inParaName, newValue, inNodeName=inCompNode )

# ===
# COMPONENT GUI SECTION: END
# ===

# ===
# MODULE GUI SECTION: START
# ===
    def moduleGUI( self ):
        col = cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 5), parent=self.fillArea )
        
        # Frame area.
        cmds.text( label='FRAMES', height=20, font='boldLabelFont', backgroundColor=[0.2,0.2,0.2] )
        cmds.separator( style='none', height=5 )
        
        # Frame template section.
        cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 40), (2, self.winWidth-40)] )
        # Left column.
        self.toggleColumn = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.symbolCheckBox( image='icon_root.png', value=0, annotation='roots', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_spine.png', value=0, annotation='spines', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_arm.png', annotation='arms', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_leg.png', annotation='legs', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_hand.png', annotation='hands', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_foot.png', annotation='feet', changeCommand=self.moduleButtons )
        cmds.symbolCheckBox( image='icon_head.png', annotation='heads', changeCommand=self.moduleButtons )
        cmds.setParent( '..' )#toggleColumn
        # Right column.
        cmds.scrollLayout( horizontalScrollBarThickness=16, verticalScrollBarThickness=16, height=100 )
        self.frameGrid = cmds.gridLayout( numberOfColumns=4, cellWidthHeight=( 50, 50 ) )
        self.moduleButtons()
        cmds.setParent( '..' )#frameGrid
        cmds.setParent( '..' )#scrollLayout
        cmds.setParent( '..' )#rowColumnLayout
        cmds.separator( style='none', height=10 )
        cmds.setParent( '..' )#col
        
    def moduleButtons( self, *args ):
        # This fills gridLayout with the appropriate buttons.        
        # Check if buttons already exist. If they do, delete them.
        gridChildren = cmds.gridLayout( self.frameGrid, query=True, childArray=True )
        if gridChildren is not None:
            for c in gridChildren:
                cmds.deleteUI( c )
        
        # Get the children of toggle buttons column.
        checkBoxChildren = cmds.rowColumnLayout( self.toggleColumn, query=True, childArray=True )
        for checkBox in checkBoxChildren:
            # Loop through the children to see if they are active.
            boxValue = cmds.symbolCheckBox( checkBox, query=True, value=True )
            if boxValue == True:
                # If the button is active then we need to make the appropriate frame
                # buttons in the grid layout.
                boxAnno = cmds.symbolCheckBox( checkBox, query=True, annotation=True )
                frameFiles = XMLUtility.getXMLInFolder( XMLUtility.FRAME_PRESETS_PATH+boxAnno+'/' )   
                for frame in frameFiles:
                    # Make the grid layout buttons. The label is the file name, while
                    # the annotation is the folder name.
                    cmds.button( parent=self.frameGrid, label=frame, annotation=boxAnno, command=lambda v, a1=frame, a2=boxAnno: buttonTest(v, a1, a2) )
# ===
# MODULE GUI SECTION: END
# ===        

# ===
# CHARACTER GUI SECTION: START
# ===
    def characterGUI( self ):
        pass
# ===
# CHARACTER GUI SECTION: END
# ===  
        
#REMOVE
createModuleUI()