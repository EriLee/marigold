from PySide import QtCore
from PySide import QtGui
from shiboken import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui

import marigold.utility.NodeUtility as NodeUtility
import marigold.ui.widgets.QTWidgets as QTWidgets

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtGui.QWidget )

def getCharacterModules( inCharNode ):
    '''
    Gets all modules that are children of a character.
    
    @param inCharNode: String. Name of the character node.
    @return: String[]. List of modules.
    '''
    characterConnections = cmds.connectionInfo( '{0}.{1}'.format( inCharNode, 'modules' ), destinationFromSource=True )
    print 'getCharacterModules>characterConnections: {0}'.format( characterConnections )
    characterModules = []
    for module in characterConnections:
        splitName = module.split( '.' )
        characterModules.append( splitName[0] )
        
    #modulePriorities = NodeUtility.getModulePriorities( characterModules )
    #sortedModules = NodeUtility.sortModules( modulePriorities, 'ascending' )
    print '__characterModules: {0}'.format( characterModules )
    return characterModules

class CharacterPriorityPrompt( QtGui.QDialog ):
    '''
    Creates prompt window for reordering build priority within
    a character.
    '''
    def __init__( self, parent=maya_main_window(), inCharNode=None ):

        super( CharacterPriorityPrompt, self ).__init__(parent  )
        
        self.parent = parent
            
        # Build a list of the character's modules.
        print 'CharacterPriorityPrompt>inCharNode: {0}'.format( inCharNode )
        modules = getCharacterModules( inCharNode )
        print '__modules: {0}'.format( modules )
        modPriorityDict = NodeUtility.getModulePriorities( modules )
        modulesSorted = NodeUtility.sortModules( modPriorityDict )
        print '__modulesSorted: {0}'.format( modulesSorted )
        
        self.dropList = QTWidgets.DropList()
        self.modDict = {}
        for module in modulesSorted:
            moduleName = cmds.getAttr( '{0}.moduleName'.format( module[0] ) )
            print '____moduleName: {0}'.format( moduleName )
            self.modDict[moduleName] = [ module[0], int(module[1]) ]
            self.dropList.addItem( moduleName )
            
        self.setWindowTitle( 'Change Build Priority' )
        self.setFixedSize( 250, 200 )
        
        self.accept_button = QtGui.QPushButton( 'Set Priorities' )
        self.accept_button.clicked.connect( lambda:self.setPriorities() )
        self.cancel_button = QtGui.QPushButton( 'Cancel' )
        self.cancel_button.clicked.connect( lambda:self.close() )
        
        button_layout = QtGui.QHBoxLayout()
        button_layout.setSpacing( 2 )
        button_layout.addStretch()
        button_layout.addWidget( self.accept_button )
        button_layout.addWidget( self.cancel_button )
        
        main_layout = QtGui.QVBoxLayout()
        main_layout.setSpacing( 2 )
        main_layout.addWidget( self.dropList )
        main_layout.addLayout( button_layout )
        
        self.setLayout( main_layout )
        
    def setPriorities( self ):
        '''
        Applies the user adjusted priorities to all the modules of a character.
        '''
        for index in xrange( self.dropList.count() ):
            moduleName = self.dropList.item( index ).text()
            moduleComponent = self.modDict[moduleName][0]
            priorityPlug = NodeUtility.getPlug( moduleComponent, 'buildPriority' )
            NodeUtility.setPlugValue( priorityPlug, index )
            
        self.close()