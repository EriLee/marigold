import maya.OpenMayaUI as omui
from shiboken import wrapInstance
from PySide import QtCore
from PySide import QtGui

def clearLayout( layout ):
    '''
    Clears all the sub-objects from the sub_layout.
    '''
    if layout is not None:
        while layout.count():
            item = layout.takeAt( 0 )
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout( item.layout() )
                
def mayaToQtObject( inMayaUI ):
    ptr = omui.MQtUtil.findControl( inMayaUI )
    if ptr is None:
        ptr = omui.MQtUtil.findLayout( inMayaUI )
    if ptr is None:
        ptr= omui.MQtUtil.findMenuItem( inMayaUI )
    if ptr is not None:
        return wrapInstance( long( ptr ), QtGui.QWidget )