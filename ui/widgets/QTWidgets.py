from PySide import QtCore
from PySide import QtGui
import marigold.ui.qtui_resources
#from marigold.utility.XMLUtility import loadModule

def imageButton( inText, inIconPath, inIconSize ):
    '''
    inText: String. Name of the button.
    inIconPath: String. Resource path for icon.
    inIconSize: List. Two INTs used to set the icon size
    '''
    button = QtGui.QToolButton()
    #button.setStyleSheet( 'border:0' )
    button.setAutoRaise( True )
    button.setIcon( QtGui.QIcon( inIconPath ) )
    button.setIconSize( QtCore.QSize( inIconSize[0], inIconSize[1] ) )
    if inText is not None:
        button.setText( inText )
    
    return button

def imageTextButton( inText, inIconPath, inIconSize ):
    '''
    inText: String. Label of the button.
    inIconPath: String. Resource path for icon.
    inIconSize: List. Two INTs used to set the icon size
    '''
    button = QtGui.QPushButton()
    button.setIcon( QtGui.QIcon( inIconPath ) )
    button.setIconSize( QtCore.QSize( inIconSize[0], inIconSize[1] ) )
    if inText is not None:
        button.setText( inText )
        button.setStyleSheet( 'text-align: left; padding: 4px' )
    
    return button
    
def toggleButton( inLabel, inIconPath, inIconSize ):
    button = QtGui.QToolButton()
    button.setAutoRaise( True )
    button.setCheckable( True )
    #':/riggingUI/icons/bit_sphere.png'
    button.setIcon( QtGui.QIcon( inIconPath ) )
    button.setIconSize( QtCore.QSize( inIconSize[0], inIconSize[1] ) )
    button.setText( inLabel )
    
    return button

def scrollArea( inLayout ):
    scrollWidget = QtGui.QWidget()
    scrollWidget.setLayout( inLayout )
    scrollArea = QtGui.QScrollArea()
    scrollArea.setFrameShadow( QtGui.QFrame.Sunken )
    scrollArea.setFrameShape( QtGui.QFrame.Box )
    scrollArea.setLineWidth( 1 )
    scrollArea.setWidgetResizable(True)
    scrollArea.setEnabled(True)
    scrollArea.setWidget( scrollWidget )
    
    return scrollArea

def basicFrame():
    frame = QtGui.QFrame()
    frame.setFrameShadow( QtGui.QFrame.Sunken )
    frame.setFrameShape( QtGui.QFrame.Box )
    frame.setLineWidth( 1 )
    frame.setStyleSheet( 'padding:1px;' )
    
    return frame
    
def stringProperty( inLabel, inPropertyValue, inParent=None ):
    if inParent is not None:
        propertyRow = QtGui.QHBoxLayout( inParent )
    else:
        propertyRow = QtGui.QHBoxLayout()
    
    textBox = QtGui.QLineEdit()
    textBox.setObjectName( inLabel )
    textBox.setAlignment( QtCore.Qt.AlignLeft )
    textBox.setMinimumHeight( 20 )
    if inPropertyValue:
        textBox.setText( inPropertyValue )
    
    textBoxLabel = QtGui.QLabel()
    textBoxLabel.setText( inLabel )
    textBoxLabel.setAlignment( QtCore.Qt.AlignCenter )
    textBoxLabel.setMinimumHeight( 12 )
    
    propertyRow.addWidget( textBox )
    propertyRow.addWidget( textBoxLabel )
    
    return propertyRow

def basicLabel( inLabel, inFontWeight, inFontSize, inFontColor, inBackgroundColor, inIndent=0 ):
    label = QtGui.QLabel()
    label.setText( inLabel )
    label.setIndent( inIndent )
    #label.setAlignment( QtCore.Qt.AlignVCenter )
    #label.setAlignment( QtCore.Qt.AlignLeft )
    label.setStyleSheet( 'font:{0}; font-size:{1}px; color:{2}; background-color:#{3}'.format( inFontWeight,
                                                                                               inFontSize,
                                                                                               inFontColor,
                                                                                               inBackgroundColor ) )
    return label