import traceback
import sys
import os
import types

from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.ui.qtui_resources

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui

import marigold.ui.test_widget as test_widget

from marigold.ui import clearLayout
import marigold.ui.rigging.UIBitsTools as UIBitsTools
import marigold.ui.rigging.UIComponentsTools as UIComponentsTools
import marigold.ui.rigging.UILatticesTools as UILatticesTools
import marigold.ui.rigging.UICharactersTools as UICharactersTools

'''
C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe -py2 E:\maya\scripts\marigold\ui\qtui.qrc > E:\maya\scripts\marigold\ui\qtui_resources.py
pyside-rcc.exe E:\maya\scripts\marigold\ui\qtui.qrc -o E:\maya\scripts\marigold\ui\qtui_resources.py
'''

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtGui.QWidget )

class ExtendedQLabel(QtGui.QLabel):  
    '''
    Usage:
        self.test_btn = ExtendedQLabel( self )
        self.test_btn.setPixmap( QtGui.QPixmap( "E:\maya\scripts\marigold\ui\icons\icon_foot.png" ) )
    '''
    def __init(self, parent):  
        QtGui.QLabel.__init__(self, parent)  
  
    def mouseReleaseEvent(self, ev):  
        self.emit(QtCore.SIGNAL('clicked()')) 
        
class UIRiggingMain( QtGui.QDialog ):
    SCRIPT_JOB_NUMBER = -1
    SELECTED_ITEM = None
    
    def __init__( self, parent=maya_main_window() ):
        super( UIRiggingMain, self ).__init__( parent )
        
    def create( self ):
        self.setWindowTitle( 'Rig Builder' )
        self.setWindowFlags( QtCore.Qt.Tool )
        self.create_actions()
        self.create_main_menu()
        self.create_main_layout()
        self.update_gui()
    
    def closeEvent( self, event ):
        # Clean up the script job stuff prior to closing the dialog.
        if self.SCRIPT_JOB_NUMBER is not -1:
            cmds.scriptJob( kill=self.SCRIPT_JOB_NUMBER, force=True )
        super( UIRiggingMain, self ).closeEvent( event )
            
    def create_actions( self ):
        self.exit = QtGui.QAction( '&Exit', self, triggered=self.close() )
        
    def create_main_menu( self ):        
        # Mode combo box.
        self.combo_menu = QtGui.QComboBox()
        self.combo_items = [ 'Bits', 'Components', 'Modules', 'Characters' ]
        self.combo_menu.insertItems( 0, self.combo_items )
        self.combo_menu.setFixedWidth( 100 )
        self.combo_menu.activated.connect( self.update_gui )
        
    def create_main_layout( self ):
        # Combo box layout
        combo_layout = QtGui.QHBoxLayout()
        combo_layout.setContentsMargins( 2, 2, 2, 2 )
        combo_layout.setAlignment( QtCore.Qt.AlignLeft )
        combo_layout.addWidget( self.combo_menu )
        
        # Dynamic layout.
        self.sub_layout = QtGui.QVBoxLayout()
        self.sub_layout.setAlignment( QtCore.Qt.AlignTop )        
        
        # Main vertical layout. This is the parent of everything in the GUI.
        self.main_column = QtGui.QVBoxLayout()
        self.main_column.addLayout( combo_layout )
        self.main_column.addLayout( self.sub_layout )
        self.setLayout( self.main_column )
        
    def update_gui( self ):
        '''
        Updates the gui based on the combo box selection.
        '''
        currentComboIndex = self.combo_menu.currentIndex()
        currentComboText = self.combo_menu.currentText()
        
        if self.sub_layout.count() is not 0: clearLayout( self.sub_layout )
        
        buildClass = {0:UIBitsTools.UIBitsTools,
                      1:UIComponentsTools.UIComponentsTools,
                      2:UILatticesTools.UILatticeTools,
                      3:UICharactersTools.UICharacterTools}
        guiClass = buildClass[ currentComboIndex ]
        self.sub_layout.addWidget( guiClass() )
        
        if currentComboIndex == 1:
            # Set the script job number so we can delete it outside of the
            # component GUI. The script job can hang around if the main GUI
            # is closed using the X while the component section is active.
            componentsToolsUI = self.sub_layout.itemAt( 0 ).widget()
            self.SCRIPT_JOB_NUMBER = componentsToolsUI.SCRIPT_JOB_NUMBER
        
    def toggle_button_color( self ):
        sender = self.sender()
        if sender.isChecked():
            #sender.setFlat( True )
            #sender.setStyleSheet( 'border:1,background-color:#5e5e5e;')
            sender.setStyleSheet( 'border:1' )
            # Fill area with buttons.
        else:
            #sender.setFlat( False )
            sender.setStyleSheet( 'border:3' )
            #sender.setStyleSheet( 'background-color:#616161' )
            
    def getListWidgetItems( self, listWidget ):
        itemList = []
        for i in xrange( listWidget.count() ):
            item = listWidget.item( i )
            itemList.append( item.text() )
        print itemList
        return itemList

'''
@ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @
 @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @
'''

        
'''
    RUN THE WINDOW
'''
#THIS DOESN'T WORK THROUGH ECLIPSE. SO WE WORK AROUND IT WHEN SENDING TO MAYA
#FROM THE EDITOR.
#if __name__ == "__main__":
    
# Development workaround for PySide winEvent error (Maya 2014)
# Make sure the UI is deleted before recreating
try:
    test_ui.deleteLater()
except:
    pass

# Create minimal UI object
test_ui = UIRiggingMain()

# Delete the UI if errors occur to avoid causing winEvent
# and event errors (in Maya 2014)
try:
    test_ui.create()
    test_ui.show()
except:
    test_ui.deleteLater()
    traceback.print_exc()