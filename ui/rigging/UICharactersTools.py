from PySide import QtCore
from PySide import QtGui

import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.components as Components
from marigold.ui import clearLayout
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.ui.rigging.UIEditCharacterModules as UIEditCharacterModules
import marigold.ui.rigging.UICharacterPriorityPrompt as UICharacterPriorityPrompt

class UICharacterTools( QtGui.QWidget ):
    SAVE_SELECTED_CHARACTER = None
    
    def __init__( self ):
        super( UICharacterTools, self ).__init__()

        layout = QtGui.QVBoxLayout( self )

        # PRESETS
        presetsLabel = QTWidgets.basicLabel( 'Character Presets', 'bold', 14, 'white', '2B2B30', inIndent=10 )
        presetsLabel.setMinimumHeight( 30 )
        presetsLabel.setAlignment( QtCore.Qt.AlignCenter )
        
        self.scrollLayout = QtGui.QVBoxLayout()
        self.scrollLayout.setAlignment( QtCore.Qt.AlignTop )
        self.scrollLayout.setContentsMargins( 8,8,8,8 )
        self.scrollLayout.setSpacing( 4 )
        scrollArea = QTWidgets.scrollArea( self.scrollLayout )
        self.updateCards()
        
        # TOOLS
        #--Label
        toolsLabel = QTWidgets.basicLabel( 'Tools', 'bold', 14, 'white', '2B2B30', inIndent=10 )
        toolsLabel.setMinimumHeight( 30 )
        toolsLabel.setAlignment( QtCore.Qt.AlignCenter )
        
        #--Combo menu
        comboRow = QtGui.QHBoxLayout()
        comboRow.setAlignment( QtCore.Qt.AlignLeft )
        
        self.characterNameList = []
        self.characterDict = {}
        for char in NodeUtility.getCharactersInScene():
            charName = cmds.getAttr( '{0}.characterName'.format( char ) )
            self.characterNameList.append( charName )
            self.characterDict[charName] = char

        self.characterCombo = QtGui.QComboBox()
        self.updateCharacterCombo()
        self.characterCombo.setFixedWidth( 100 )
        self.characterCombo.activated.connect( self.setActiveCharacter )
        
        comboRefreshBtn = QTWidgets.imageTextButton( None, ':/riggingUI/icons/icon_refresh20.png', [16,16] )
        comboRefreshBtn.setMaximumWidth( 20 )
        comboRefreshBtn.setMaximumHeight( 20 )
        comboRefreshBtn.clicked.connect( self.updateCharacterCombo )
        
        comboRow.addWidget( self.characterCombo )
        comboRow.addWidget( comboRefreshBtn )
        
        #--Buttons
        modulePrioritiesBtn = QTWidgets.imageTextButton( 'Module Priorities', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        modulePrioritiesBtn.clicked.connect( lambda:self.characterPriorityPromptTrigger() )
        
        saveCharacterBtn = QTWidgets.imageTextButton( 'Save Character', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        saveCharacterBtn.clicked.connect( lambda:self.saveCharacter() )
        
        buildCharacterBtn = QTWidgets.imageTextButton( 'Build Character', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        buildCharacterBtn.clicked.connect( lambda:self.buildCharacter() )
        
        editModulesBtn = QTWidgets.imageTextButton( 'Edit Character Modules', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        editModulesBtn.clicked.connect( lambda:self.characterModulePromptTrigger() )
        
        #--Button grid layout.
        toolsGrid = QtGui.QGridLayout()
        toolsGrid.setColumnMinimumWidth( 0, 100 )
        toolsGrid.setColumnMinimumWidth( 1, 100 )
        toolsGrid.setColumnMinimumWidth( 2, 100 )
        toolsGrid.setSpacing( 2 )
        toolsGrid.setContentsMargins( 0,0,0,0 )
        toolsGrid.addWidget( modulePrioritiesBtn, 0, 0 )
        toolsGrid.addWidget( saveCharacterBtn, 0, 1 )
        toolsGrid.addWidget( buildCharacterBtn, 0, 2 )
        toolsGrid.addWidget( editModulesBtn, 1, 0 )
        
        
        # SETUP LAYOUT
        layout.addWidget( presetsLabel )
        layout.addWidget( scrollArea )
        layout.addWidget( toolsLabel )
        layout.addLayout( comboRow )
        layout.addLayout( toolsGrid )

    def characterModulePromptTrigger(self):
        '''
        Triggers the prompt window for editing a character's modules.
        '''
        charNode = self.characterDict[self.SAVE_SELECTED_CHARACTER]
        self.dialog =  UIEditCharacterModules.EditCharacterModules( inCharacterNode=charNode ).show()   
        
    def setActiveCharacter( self ):
        '''
        Sets the global variable the tracks the active character.
        '''
        currentComboText = self.characterCombo.currentText()
        self.SAVE_SELECTED_CHARACTER = currentComboText
    
    def updateCharacterCombo( self ):
        '''
        Updates the character combo box so it lists all the characters in the scene.
        '''
        self.characterCombo.clear()

        self.characterNameList = []
        self.characterDict = {}
        
        for char in NodeUtility.getCharactersInScene():
            charName = cmds.getAttr( '{0}.characterName'.format( char ) )
            self.characterNameList.append( charName )
            self.characterDict[charName] = char

        if len( self.characterNameList ) == 0:
            self.characterCombo.insertItem( 0, 'No Characters' )
            self.SAVE_SELECTED_CHARACTER = None
        else:
            self.characterCombo.insertItems( 0, self.characterNameList )
            self.SAVE_SELECTED_CHARACTER = self.characterNameList[0]
        
    def updateCards( self ):
        '''
        Updates the character cards.
        '''
        # Clear the lattice list first.
        clearLayout( self.scrollLayout )

        presetsPath = '{0}{1}/'.format( XMLUtility.FRAME_PRESETS_PATH, 'characters' )
        latticePresets = XMLUtility.getXMLInFolder( presetsPath )
        for lattice in latticePresets:
            description = 'From here you can search these documents. Enter your search words into the box below and click /"search/".'
            self.scrollLayout.addWidget( QTWidgets.latticeCard( 'characters', lattice, description, parent=self.scrollLayout ) )
        
    def characterPriorityPromptTrigger( self ):
        '''
        Triggers prompt window for editing character's module priorities.
        '''
        charNode = self.characterDict[self.SAVE_SELECTED_CHARACTER]
        dialog = UICharacterPriorityPrompt.CharacterPriorityPrompt( inCharNode=charNode ).show()
        
    def saveCharacter( self ):
        '''
        Save the character into an XML file for re-use.
        '''        
        charNode = self.characterDict[self.SAVE_SELECTED_CHARACTER]
        charBitName = Components.CharacterRootComponent( charNode ).parentNode[0]
        XMLUtility.writeModuleXML( charBitName, 'characters', self.SAVE_SELECTED_CHARACTER )
        
    def buildCharacter( self ):
        '''
        Build the character selected by the user.
        '''
        print 'BUILDING: {0}'.format( self.SAVE_SELECTED_CHARACTER )