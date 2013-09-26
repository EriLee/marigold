import maya.cmds as cmds
import marigold.utility.XMLUtility as XMLUtility
import marigold.utility.GeneralUtility as GeneralUtility

class createRigUI():
    def __init__( self, winName='createRigUI' ):
        self.winTitle = 'Rigging Tools'
        self.winName = winName
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 306
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
        # TAB LAYOUT TOOLS
        self.tabLayout = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Frame Templates', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        
        # Frame template section.
        cmds.rowColumnLayout( numberOfColumns=2, columnWidth=[(1, 40), (2, self.winWidth-40)] )
        # Left column.
        self.toggleColumn = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.symbolCheckBox( image='icon_root.png', value=0, annotation='roots', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_spine.png', value=0, annotation='spines', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_arm.png', annotation='arms', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_leg.png', annotation='legs', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_hand.png', annotation='hands', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_foot.png', annotation='feet', changeCommand=self.fillButtons )
        cmds.symbolCheckBox( image='icon_head.png', annotation='heads', changeCommand=self.fillButtons )
        cmds.setParent( '..' )#toggleColumn

        # Right column.
        cmds.scrollLayout( horizontalScrollBarThickness=16, verticalScrollBarThickness=16, height=100 )
        self.frameGrid = cmds.gridLayout( numberOfColumns=4, cellWidthHeight=( 50, 50 ) )
        self.fillButtons()
        cmds.setParent( '..' )#frameGrid
        cmds.setParent( '..' )#scrollLayout
        cmds.setParent( '..' )#rowColumnLayout
        
        # Other
        cmds.button( label='Save Selected Frame')
        cmds.button( label='Link Frames' )
        cmds.button( label='Delete Frame' )
        cmds.setParent( '..' )#tabLayout

        # TAB FRAME TOOLS
        self.tabFrame = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Frame Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        
        # Top rows.
        self.moduleList = cmds.scrollLayout( horizontalScrollBarThickness=16, verticalScrollBarThickness=16, height=100 )
        self.fillModuleList()
        cmds.setParent( '..' )#moduleList    
        # Bottom buttons
        cmds.button( label='Refresh List', command=self.fillModuleList )
        cmds.button( label='Build All' )
        cmds.setParent( '..' )#tabFrame
        
        # TAB RIGGING TOOLS
        self.tabRig = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Rig Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        cmds.button()
        cmds.button()
        cmds.button()
        cmds.setParent( '..' )#tabRig
        
        # Added the tabs to the tab layout.
        cmds.tabLayout( self.tabs, edit=True, tabLabel=( (self.tabLayout, 'Layout'), (self.tabFrame, 'Frame'), (self.tabRig, 'Rig') ) )

        # Show the window.
        cmds.showWindow( self.winName )
                
    def fillButtons( self, *args ):
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

    def fillModuleList( self, *args ):
        from marigold.utility.NodeUtility import getMetaNodesInScene
        from marigold.utility.FrameUtility import getFrameBitSettings
        
        # Clean up UI elements for refreshing the list.
        lChildren = cmds.scrollLayout( self.moduleList, query=True, childArray=True )
        if lChildren is not None:
            for c in lChildren:
                cmds.deleteUI( c )
                #self.aRows = []
        
        # Build module list for ui.
        moduleList = getMetaNodesInScene( 'frameModule' )
        print moduleList
        
        previousColor = 2
        warningPip = False
        for i, module in enumerate( moduleList ):
            print i, module
            
            # Get the required plug data.
            moduleData = {}
            nodeAttrs = getFrameBitSettings( module )    
            moduleData['priority'] = nodeAttrs['buildPriority']
            moduleData['frameName'] = module
            moduleData['modFolder'] = nodeAttrs['buildFolder']
            moduleData['modFile'] = nodeAttrs['metaClass']
            
            # Set the row color.
            color = 1
            if previousColor is 1:
                color = 2
                previousColor = 2
            else:
                color = 1
                previousColor = 1
                
            # Make the row.
            self.modListColumn = cmds.rowColumnLayout( parent=self.moduleList, numberOfColumns=6,
                                                       columnWidth=[(1,26),(2,30),(3,90),(4,50),(5,50),(6,20)],
                                                       columnSpacing=[(1,2),(2,2),(3,2),(4,2),(5,2),(6,2)],
                                                       backgroundColor=self.rowColors[color-1] )
            cmds.intField( editable=False, value=moduleData['priority'] )
            cmds.image( image='icon_warning_pip.png', visible=warningPip )
            cmds.text( label=moduleData['frameName'] )
            cmds.button( label='options' )
            cmds.button( label='build', command=lambda v, a1=moduleData['modFolder'], a2=moduleData['modFile']: buttonBuildTemp( v, a1, a2 ) )
            cmds.checkBox( label='' )            
            cmds.setParent( '..' )#self.modListColumn
        
def buttonBuildTemp( *args ):
    # Import the correct module via a string.
    importPath = 'marigold/'+XMLUtility.FRAME_MODULES_PATH+args[1]+'/'+args[2]
    pathFinal = importPath.replace( '/', '.' )
    module = GeneralUtility.importModule( pathFinal )
    module.buildModule()
                       
def buttonTest( *args ):
    import marigold.utility.FrameUtility as FrameUtility
    # There are three arguments coming in.
    # Arg1: The value of the button pressed. This is automatically sent and ignored.
    # Arg2: The name of the XML file to open.
    # Arg3: The name of the folder the XML file is located.
    FrameUtility.buildFrameModule( args[2], args[1] )
    '''
    dirPath = XMLUtility.getPresetPath( XMLUtility.FRAME_MODULES_PATH+args[2] )
    fullPath = dirPath+'/'+args[1]+'.py'
    print fullPath
    #exec(compile(open("somefile.py").read(), "somefile.py", 'exec'), global_vars, local_vars)
    #exec( compile( open( fullPath ).read(), args[1]+'.py', 'exec' ) )
    '''

createRigUI()