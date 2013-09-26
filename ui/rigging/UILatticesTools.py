'''
UI LATTICES TOOLS

Creates a QtGui.QWidget object containing all the UI and functionality for
creating/editing lattices.

By: Austin Baker
Date: 9/7/2013
'''
from PySide import QtCore
from PySide import QtGui
import maya.cmds as cmds
from marigold.ui import clearLayout
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.utility.XMLUtility as XMLUtility
import marigold.utility.NodeUtility as NodeUtility
import marigold.components as Components

class UILatticeTools( QtGui.QWidget ):        
    def __init__( self ):
        super( UILatticeTools, self ).__init__()
    
        layout = QtGui.QVBoxLayout( self )
        
        # LATTICES SECTIONS
        latticesLabel = QTWidgets.basicLabel( 'Lattices', 'bold', 14, 'white', '2B2B30', inIndent=10 )
        latticesLabel.setMinimumHeight( 30 )
        latticesLabel.setAlignment( QtCore.Qt.AlignCenter )
        
        # Grid that holds the toggle buttons for lattice types in the first column, and the
        # scroll layout for the list of lattices in the second column.
        latticesGrid = QtGui.QGridLayout()
        latticesGrid.setContentsMargins( 0, 0, 0, 0 )
        latticesGrid.setHorizontalSpacing( 0 )
        latticesGrid.setAlignment( QtCore.Qt.AlignTop )
        latticesGrid.setVerticalSpacing( 0 )
        
        # Toggle button layout.
        self.togLayout = QtGui.QVBoxLayout()
        self.togLayout.setAlignment( QtCore.Qt.AlignTop )
        iconSize = [26,26]
        rootTog = QTWidgets.toggleButton( 'roots', ':/riggingUI/icons/icon_root.png', iconSize )
        spineTog = QTWidgets.toggleButton( 'spines', ':/riggingUI/icons/icon_spine.png', iconSize )
        armTog = QTWidgets.toggleButton( 'arms', ':/riggingUI/icons/icon_arm.png', iconSize )
        legTog = QTWidgets.toggleButton( 'legs', ':/riggingUI/icons/icon_leg.png', iconSize )
        handTog = QTWidgets.toggleButton( 'hands', ':/riggingUI/icons/icon_hand.png', iconSize )
        footTog = QTWidgets.toggleButton( 'feet', ':/riggingUI/icons/icon_foot.png', iconSize )
        headTog = QTWidgets.toggleButton( 'heads', ':/riggingUI/icons/icon_head.png', iconSize )

        rootTog.toggled.connect( lambda toggleState:self.updateCards() )
        spineTog.toggled.connect( lambda toggleState:self.updateCards() )
        armTog.toggled.connect( lambda toggleState:self.updateCards() )
        legTog.toggled.connect( lambda toggleState:self.updateCards() )
        handTog.toggled.connect( lambda toggleState:self.updateCards() )
        footTog.toggled.connect( lambda toggleState:self.updateCards() )
        headTog.toggled.connect( lambda toggleState:self.updateCards() )
        
        self.togLayout.addWidget( rootTog )
        self.togLayout.addWidget( spineTog )
        self.togLayout.addWidget( armTog )
        self.togLayout.addWidget( legTog )
        self.togLayout.addWidget( handTog )
        self.togLayout.addWidget( footTog )
        self.togLayout.addWidget( headTog )
        self.togLayout.addStretch( 1 )
        
        # Scroll area for lattice list.
        self.scrollLayout = QtGui.QVBoxLayout()
        self.scrollLayout.setAlignment( QtCore.Qt.AlignTop )
        self.scrollLayout.setContentsMargins( 8,8,8,8 )
        self.scrollLayout.setSpacing( 4 )
        scrollArea = QTWidgets.scrollArea( self.scrollLayout )
        
        # Put the toggle buttons and lattice scroll list in the main grid layout.
        latticesGrid.addLayout( self.togLayout, 0, 0 )
        latticesGrid.addWidget( scrollArea, 0, 1 )        
        
        # TOOLS SECTION
        toolsLabel = QTWidgets.basicLabel( 'Lattice Tools', 'bold', 14, 'white', '2B2B30', inIndent=10 )
        toolsLabel.setMinimumHeight( 30 )
        toolsLabel.setAlignment( QtCore.Qt.AlignCenter )
        
        latticeToolsGrid = QtGui.QGridLayout()
        latticeToolsGrid.setColumnMinimumWidth( 0, 100 )
        latticeToolsGrid.setColumnMinimumWidth( 1, 100 )
        latticeToolsGrid.setColumnMinimumWidth( 2, 100 )
        latticeToolsGrid.setSpacing( 2 )
        latticeToolsGrid.setContentsMargins( 0,0,0,0 )
        
        # Buttons
        saveModeluBtn = QTWidgets.imageTextButton( 'Save Module', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        saveModeluBtn.clicked.connect( lambda:self.saveModulePrompt() )
        latticeToolsGrid.addWidget( saveModeluBtn, 0, 0 )        
        
        # Build the widget
        layout.addWidget( latticesLabel )
        layout.addLayout( latticesGrid )
        layout.addWidget( toolsLabel )
        layout.addLayout( latticeToolsGrid )
    
    def updateCards( self ):
        # Clear the lattice list first.
        clearLayout( self.scrollLayout )
        
        # Get all the active toggle buttons.
        for index in xrange( self.togLayout.count() ):
            button = self.togLayout.itemAt( index ).widget()
            if isinstance( button, QtGui.QToolButton ):
                if button.isChecked():
                    buttonType = button.text()
                    presetsPath = '{0}{1}/'.format( XMLUtility.FRAME_PRESETS_PATH, buttonType )
                    latticePresets = XMLUtility.getXMLInFolder( presetsPath )
                    for lattice in latticePresets:
                        description = 'From here you can search these documents. Enter your search words into the box below and click /"search/".'
                        self.scrollLayout.addWidget( latticeCard( buttonType, lattice, description, parent=self.scrollLayout ) )
    
    def saveModulePrompt( self ):
        self.dialog = ModuleTypePrompt( self )
        self.dialog.show()
        
    def saveModule( self ):
        '''
        Save the module into an XML file for re-use.
        We assume that the root node of the module is the one with the module root meta node.
        This means it and all of it's children will be saved in the XML.
        '''
        # Get the selected module
        item = cmds.ls( long=True, selection=True )[0]
        
        # Try to get the module meta component.
        moduleComp = Components.searchModule( item, 'ModuleRootComponent' )
        
        if moduleComp:
            # Get the module info and save it as an XML.
            modulePlug = NodeUtility.getPlug( moduleComp[1], 'moduleName' )
            moduleName = NodeUtility.getPlugValue( modulePlug )
            XMLUtility.writeModuleXML( moduleComp[0], self.SELECTED_ITEM, moduleName )
            
class ModuleTypePrompt( QtGui.QWidget ):
    def __init__( self, parent=None ):
        super( ModuleTypePrompt, self ).__init__()
        
        self.parent = parent
        
        moduleList = ['roots', 'spines', 'arms', 'legs', 
                      'hands', 'feet', 'heads']
        
        self.setWindowTitle( 'Select Module Type' )
        self.setFixedSize( 250, 200 )
        
        self.accept_button = QtGui.QPushButton( 'Accept' )
        self.accept_button.clicked.connect( lambda:self.returnSelection() )
        self.cancel_button = QtGui.QPushButton( 'Cancel' )
        self.cancel_button.clicked.connect( lambda:self.close() )
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.setSpacing( 2 )
        button_layout.addStretch()
        button_layout.addWidget( self.accept_button )
        button_layout.addWidget( self.cancel_button )
        
        self.list = QtGui.QListWidget()
        self.list.addItems( moduleList )
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.setSpacing( 2 )
        main_layout.addWidget( self.list )
        main_layout.addLayout( button_layout )
        
        self.setLayout( main_layout )
        
    def returnSelection( self ):
        for x in self.list.selectedItems():
            self.parent.SELECTED_ITEM = x.text()
            self.parent.saveModule()
            self.close()

def latticeCard( inLatticeType, inLattice, inLatticeDescription, parent=None ):
    nameLabelHeight = 14
    cardHeight = 64
    cardBackgroundColor = {'roots':'383232',
                           'spines':'383832',
                           'arms':'323834',
                           'legs':'323638',
                           'hands':'343238',
                           'feet':'383237',
                           'heads':'383232'}
        
    cardLabelColor = {'roots':'5d5353',
                      'spines':'5d5d53',
                      'arms':'535d56',
                      'legs':'53595d',
                      'hands':'57535d',
                      'feet':'5d535b',
                      'heads':'5d5353'}
    
    cardButtonColor = {'roots':'4b4141',
                      'spines':'4b4b43',
                      'arms':'434b45',
                      'legs':'42474a',
                      'hands':'45424a',
                      'feet':'4a4249',
                      'heads':'4a4242'}
    
    latticeName = QtGui.QLabel()
    latticeName.setIndent( 10 )
    latticeName.setText( str.upper( str( inLattice ) ) )
    latticeName.setAlignment( QtCore.Qt.AlignLeft )
    latticeName.setMaximumHeight( nameLabelHeight )
    latticeName.setStyleSheet( 'font:{0}; font-size:{1}px; color:{2}; background-color:#{3}'.format( 'bold',
                                                                                                     10,
                                                                                                     'white',
                                                                                                     cardLabelColor[ inLatticeType ] ) )
    
    latticeDescription = QtGui.QLabel()
    latticeDescription.setMinimumHeight( 45 )
    latticeDescription.setMaximumHeight( 45 )
    latticeDescription.setWordWrap( True )
    latticeDescription.setText( inLatticeDescription )
    
    latticeButton = QTWidgets.imageTextButton( None, ':/riggingUI/icons/icon_plus32.png', [32,32] )
    latticeButton.setMaximumSize( QtCore.QSize( 40, 40 ) )
    latticeButton.setStyleSheet( 'background-color:#{0}'.format( cardButtonColor[ inLatticeType ]) )
    latticeButton.clicked.connect( lambda a=inLatticeType, b=inLattice:XMLUtility.loadModule( a, b ) )
    
    latticeGrid = QtGui.QGridLayout()
    latticeGrid.setAlignment( QtCore.Qt.AlignTop )
    latticeGrid.setContentsMargins( 0, 0, 0, 0 )
    latticeGrid.setHorizontalSpacing( 0 )
    
    latticeGrid.addWidget( latticeDescription, 0, 0 )
    latticeGrid.addWidget( latticeButton, 0, 1 )
    latticeGrid.setColumnMinimumWidth( 1, 40 )
    
    latticeRow = QtGui.QVBoxLayout()
    latticeRow.setSpacing( 0 )
    latticeRow.setContentsMargins( 0,0,0,0 )
    latticeRow.addWidget( latticeName )
    latticeRow.addLayout( latticeGrid )

    frame = QtGui.QFrame()
    frame.setFrameShadow( QtGui.QFrame.Sunken )
    frame.setFrameShape( QtGui.QFrame.StyledPanel )
    frame.setLineWidth( 2 )
    frame.setStyleSheet( 'padding:1px; background-color:#{0}'.format( cardBackgroundColor[ inLatticeType ] ) )
    frame.setMinimumHeight( cardHeight )
    frame.setLayout( latticeRow )
    
    return frame