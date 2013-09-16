'''
UI LATTICES TOOLS

Creates a QtGui.QWidget object containing all the UI and functionality for
creating/editing lattices.

By: Austin Baker
Date: 9/7/2013
'''
from PySide import QtCore
from PySide import QtGui
from marigold.ui import clearLayout
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.utility.XMLUtility as XMLUtility

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
        #matchTranslationBtn.clicked.connect( lambda a='tran':TransformUtility.matchTransforms( a ) )
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
                        
                        card = QTWidgets.latticeCard( buttonType, lattice, description )                        
                        self.scrollLayout.addWidget( card )