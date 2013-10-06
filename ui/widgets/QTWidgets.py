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

def latticeCard( inLatticeType, inLattice, inLatticeDescription, parent=None ):
    from marigold.utility.XMLUtility import loadModule
    
    nameLabelHeight = 14
    cardHeight = 64
    cardBackgroundColor = {'roots':'383232',
                           'spines':'383832',
                           'arms':'323834',
                           'legs':'323638',
                           'hands':'343238',
                           'feet':'383237',
                           'heads':'383232',
                           'characters':'5f9056'}
        
    cardLabelColor = {'roots':'5d5353',
                      'spines':'5d5d53',
                      'arms':'535d56',
                      'legs':'53595d',
                      'hands':'57535d',
                      'feet':'5d535b',
                      'heads':'5d5353',
                      'characters':'5f9056'}
    
    cardButtonColor = {'roots':'4b4141',
                      'spines':'4b4b43',
                      'arms':'434b45',
                      'legs':'42474a',
                      'hands':'45424a',
                      'feet':'4a4249',
                      'heads':'4a4242',
                      'characters':'5f9056'}
    
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
    
    latticeButton = imageTextButton( None, ':/riggingUI/icons/icon_plus32.png', [32,32] )
    latticeButton.setMaximumSize( QtCore.QSize( 40, 40 ) )
    latticeButton.setStyleSheet( 'background-color:#{0}'.format( cardButtonColor[ inLatticeType ]) )
    latticeButton.clicked.connect( lambda a=inLatticeType, b=inLattice:loadModule( a, b ) )
    
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

class DropList( QtGui.QListWidget ):
    MIME_TYPE = 'application/x-qabstractitemmodeldatalist'
    
    def __init__( self, parent=None ):
        super( DropList, self ).__init__()
        
        self.parent = parent
        
        self.setStyleSheet('''
            color:black;
            background-color:lightgray;
            border-width:2px;
            border-style:solid;
            border-color:black;
            margin: 2px;''' )
        
        self.setAcceptDrops( True )
        self.setDragEnabled( True )
        self.setDragDropMode( QtGui.QAbstractItemView.InternalMove )
    
    def dropEvent( self, event ):
        super( DropList, self ).dropEvent( event )

        mimeData = event.mimeData()

        for item in self.selectedItems():
            print item.text()
            
class DropFrame( QtGui.QFrame ):
    def __init__( self, parent=None ):
        super( DropFrame, self ).__init__( parent )
        
        self.setStyleSheet('''
            background-color:lightgray;
            border-width:2px;
            border-style:solid;
            border-color:black;
            margin: 2px;''' )
            
        self.setAcceptDrops( True )
        
    def dragEnterEvent( self, event ):
        print 'drag event: {0}'.format( event )
        
    def dropEvent( self, event ):
        print 'drop event: {0}'.format( event )

class DragLabel( QtGui.QLabel ):
    def __init__( self, parent=None ):
        super( DragLabel, self ).__init__( parent )

        self.setStyleSheet('''
            background-color: black;
            color: white;
            font: bold;
            padding: 6px;
            border-width: 2px;
            border-style: solid;
            border-radius: 16px;
            border-color: white;''')

    def mousePressEvent( self, event ):
        print 'mouse press event: {0}'.format( event )