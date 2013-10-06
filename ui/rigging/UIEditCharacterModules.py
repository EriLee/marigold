from PySide import QtCore
from PySide import QtGui
from shiboken import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui

import marigold.utility.NodeUtility as NodeUtility
import marigold.components as Components


def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtGui.QWidget )

def getCharacterChildrenModules( inCharNode ):
    '''
    Gets all the children of a character node.
    
    @return: String[]. Each module component node name.
    '''
    # Get the children
    bitName = Components.CharacterRootComponent( inCharNode ).parentNode[0]
    
    children = cmds.listRelatives( bitName, type='transform', allDescendents=True, fullPath=True )
    modules = []
    for child in children:
        childComponents = NodeUtility.getModuleComponentSettings( child )
        for comp in childComponents:
            if NodeUtility.attributeCheck( comp, 'characterRoot' ):
                aType = cmds.getAttr( '{0}.classType'.format( comp ) )
                if aType == 'ModuleRootComponent':
                    modules.append( comp )
                
    return modules

class EditCharacterModules( QtGui.QDialog ):
    '''
    Creates prompt window for reordering build priority within
    a character.
    '''
    def __init__( self, parent=maya_main_window(), inCharacterNode=None ):
        super( EditCharacterModules, self ).__init__( parent )
        
        self.parent = parent
        self.charNode = inCharacterNode
        
        self.setWindowTitle( 'Select Module Type' )
        
        # MODULE LISTS: Two lists, left is connected modules.
        # Right is disconnected.
        self.buildLists()
        self.conList = QtGui.QListWidget()
        self.conList.setSelectionMode( QtGui.QAbstractItemView.MultiSelection )
        self.conList.addItems( self.conMods.keys() )
        
        self.disList = QtGui.QListWidget()
        self.disList.setSelectionMode( QtGui.QAbstractItemView.MultiSelection )
        self.disList.addItems( self.disMods.keys() )
        #--disCon Layout
        listLayout = QtGui.QHBoxLayout()
        listLayout.addWidget( self.conList )
        listLayout.addWidget( self.disList )
        
        
        # BUTTON ROW: Dis/Con Module Buttons
        #--Buttons
        disconnectModuleBtn = QtGui.QPushButton( '>>>' )
        disconnectModuleBtn.clicked.connect( self.disconnectModules )
        connectModuleBtn = QtGui.QPushButton( '<<<' )
        connectModuleBtn.clicked.connect( self.connectModules )
        #--Button Row
        disConGrid = QtGui.QGridLayout()
        disConGrid.setSpacing( 2 )
        disConGrid.setContentsMargins( 0,0,0,0 )
        disConGrid.addWidget( disconnectModuleBtn, 0, 0 )
        disConGrid.addWidget( connectModuleBtn, 0, 1 )
        
        
        # BUTTON ROW: Close Button
        #--Close Button
        closeBtn = QtGui.QPushButton( 'Close' )
        closeBtn.setMinimumSize( 80, 30 )
        closeBtn.clicked.connect( lambda:self.close() )
        #--Close Button Row
        btnlayout = QtGui.QHBoxLayout()
        btnlayout.setSpacing( 2 )
        btnlayout.addStretch()
        btnlayout.addWidget( closeBtn )
    
    
        # MAIN LAYOUT
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setSpacing( 2 )
        mainLayout.addLayout( listLayout )
        mainLayout.addLayout( disConGrid )
        mainLayout.addLayout( btnlayout )
        
        self.setLayout( mainLayout )
        
    def buildLists( self ):
        '''
        Builds a list of all modules in a character.
        '''
        modList = getCharacterChildrenModules( self.charNode )
        self.conMods = {}
        self.disMods = {}
        
        for mod in modList:
            charRoot = NodeUtility.getNodeAttrSource( mod, 'characterRoot' )
            moduleName = cmds.getAttr( '{0}.moduleName'.format( mod ) )
            if charRoot is not None:
                self.conMods[moduleName] = mod
            else:
                self.disMods[moduleName] = mod
    
    def updateLists(self):
        '''
        Updates the list of modules to reflect user changes.
        '''
        self.conList.clear()
        self.disList.clear()
        self.buildLists()
        self.conList.addItems( self.conMods.keys() )
        self.disList.addItems( self.disMods.keys() )
        
    def disconnectModules(self):
        '''
        Disconnect a module from the character component.
        '''
        # Get modules selected from conList.
        selList = self.conList.selectedItems()
        for module in selList:
            NodeUtility.disconnectNodes( self.charNode, 'modules', self.conMods[module.text()], 'characterRoot' )
            
        # Refresh the lists.
        self.updateLists()
    
    def connectModules(self):
        '''
        Connects a module to the character component.
        '''
        # Get modules selected from disList
        selList = self.disList.selectedItems()
        for module in selList:
            NodeUtility.connectNodes( self.charNode, 'modules', self.disMods[module.text()], 'characterRoot' )
            
        # Refresh the lists.
        self.updateLists()