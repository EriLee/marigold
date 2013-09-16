from PySide import QtCore
from PySide import QtGui

class test_ui( QtGui.QWidget ):
    def __init__( self, parent ):
        super( test_ui, self ).__init__( parent )
        
        self.layout = QtGui.QVBoxLayout( self )
        self.text_box = QtGui.QTextEdit()
        self.layout.addWidget( self.text_box )