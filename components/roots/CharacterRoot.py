from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets

from marigold.components.BaseComponent import BaseComponent
import marigold.utility.NodeUtility as NodeUtility

class CharacterRootComponent( BaseComponent ):
    nodeType = 'CharacterRootComponent'
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( CharacterRootComponent, self ).__init__( node=self.node )
    
    def requiredAttributes( self ):
        super( CharacterRootComponent, self ).requiredAttributes()
        NodeUtility.addPlug( self.newNode, 'characterName', 'dataType', 'string' )
        self.setAttribute( 'characterName', 'joe', self.newNode )
                
        NodeUtility.addPlug( self.newNode, 'skeletonGroupName', 'dataType', 'string' )
        self.setAttribute( 'skeletonGroupName', 'skeleton', self.newNode )
        
        NodeUtility.addPlug( self.newNode, 'rigGroupName', 'dataType', 'string' )
        self.setAttribute( 'rigGroupName', 'rig', self.newNode )
        
        NodeUtility.addPlug( self.newNode, 'modules', 'attributeType', 'message' )
        
    def componentGui( self, inNodeName, parent=None ):
            '''
            Creates the QT gui for this component.
            
            @return: QWidget.
            '''
            return componentWidget( inNodeName, parent=parent )
        
class componentWidget( QtGui.QWidget ):
    '''
    QT QWidget class for this component.
    '''    
    def __init__( self, nodeName, parent=None ):
        super( componentWidget, self ).__init__( parent )
        self.parent = parent
        
        def on_context_menu( point, inNodeName ):
            popMenu = QtGui.QMenu()
            deleteAction = QtGui.QAction( 'Delete Component', popMenu, triggered=lambda a=inNodeName:self.deleteComponentFromObject( a ) )
            popMenu.addAction( deleteAction )
            
            popMenu.exec_( self.componentLabel.mapToGlobal( point ) )
            
        # Setup layout.
        verticalLayout = QtGui.QVBoxLayout()
        verticalLayout.setContentsMargins( 0,0,0,0 )
        verticalLayout.setSpacing( 0 )
        verticalLayout.setAlignment( QtCore.Qt.AlignTop )
        
        # Label for component
        componentLabel = QTWidgets.basicLabel( nodeName, 'bold', 10, 'black', '6E9094', inIndent=20 )
        componentLabel.setMinimumHeight( 18 )    
        componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        componentLabel.customContextMenuRequested.connect( lambda point, nodeName=nodeName:on_context_menu( point, nodeName ) )
        
        
        # Properties
        propertyStack = QtGui.QVBoxLayout()
        
        propertyFrame = QTWidgets.basicFrame()
        propertyFrame.setMinimumHeight( 120 )
        propertyFrame.setMaximumHeight( 120 )
        
        # Add string edit property
        characterPlug = NodeUtility.getPlug( nodeName, 'characterName' )
        characterValue = NodeUtility.getPlugValue( characterPlug )
        characterTextLayout = QTWidgets.stringProperty( 'Character Name', characterValue )
        
        skelGroupPlug = NodeUtility.getPlug( nodeName, 'skeletonGroupName' )
        skelGroupValue = NodeUtility.getPlugValue( skelGroupPlug )
        skelGroupTextLayout = QTWidgets.stringProperty( 'Skeleton Group Name', skelGroupValue )
        
        rigGroupPlug = NodeUtility.getPlug( nodeName, 'rigGroupName' )
        rigGroupValue = NodeUtility.getPlugValue( rigGroupPlug )
        rigGroupTextLayout = QTWidgets.stringProperty( 'Rigging Group Name', rigGroupValue )
        
        '''
        ADD MODULES BUTTON. PROBABLY HAVE A POPUP LISTING UNCONNECTED MODULES IN THE SCENE??
        '''
        
        # Add everything to the vertical layout.
        propertyStack.addLayout( characterTextLayout )
        propertyStack.addLayout( skelGroupTextLayout )
        propertyStack.addLayout( rigGroupTextLayout )
        
        propertyFrame.setLayout( propertyStack )
        
        verticalLayout.addWidget( componentLabel )
        verticalLayout.addWidget( propertyFrame )
        
        # Connections
        charTextBox = propertyFrame.findChild( QtGui.QLineEdit, 'Character Name' )
        charTextBox.editingFinished.connect( lambda inPlugName='characterName', inQTType='QLineEdit', inPlugValue=charTextBox, inNodeName=nodeName
                                             :CharacterRootComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        
        skelTextBox = propertyFrame.findChild( QtGui.QLineEdit, 'Skeleton Group Name' )
        skelTextBox.editingFinished.connect( lambda inPlugName='skeletonGroupName', inQTType='QLineEdit', inPlugValue=skelTextBox, inNodeName=nodeName
                                             :CharacterRootComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        
        rigTextBox = propertyFrame.findChild( QtGui.QLineEdit, 'Rigging Group Name' )
        rigTextBox.editingFinished.connect( lambda inPlugName='rigGroupName', inQTType='QLineEdit', inPlugValue=rigTextBox, inNodeName=nodeName
                                            :CharacterRootComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        
        #return mainWidget
        self.setLayout( verticalLayout )