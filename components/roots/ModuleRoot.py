from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets

from marigold.components.BaseComponent import BaseComponent
import marigold.utility.NodeUtility as NodeUtility

class ModuleRootComponent( BaseComponent ):
    nodeType = 'ModuleRootComponent'
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( ModuleRootComponent, self ).__init__( node=self.node )
    
    def requiredAttributes( self ):
        super( ModuleRootComponent, self ).requiredAttributes()
        NodeUtility.addPlug( self.newNode, 'moduleName', 'dataType', 'string' )
        NodeUtility.addPlug( self.newNode, 'buildPriority', 'attributeType', 'byte' )
        NodeUtility.addPlug( self.newNode, 'characterRoot', 'attributeType', 'message' )
        
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
        propertyFrame.setMinimumHeight( 40 )
        propertyFrame.setMaximumHeight( 40 )
        
        # Add string edit property
        modulePlug = NodeUtility.getPlug( nodeName, 'moduleName' )
        moduleValue = NodeUtility.getPlugValue( modulePlug )
        moduleTextLayout = QTWidgets.stringProperty( 'Module Name', moduleValue )
        
        '''
        ADD EDIT FIELDS FOR PRIORITY AND CHARACTER ROOT!!!!!!!!!
        '''
        
        # Add everything to the vertical layout.
        propertyStack.addLayout( moduleTextLayout )        
        propertyFrame.setLayout( propertyStack )
        
        verticalLayout.addWidget( componentLabel )
        verticalLayout.addWidget( propertyFrame )
        
        # Connections
        moduleTextBox = propertyFrame.findChild( QtGui.QLineEdit, 'Module Name' )
        moduleTextBox.editingFinished.connect( lambda inPlugName='moduleName', inQTType='QLineEdit', inPlugValue=moduleTextBox, inNodeName=nodeName
                                               :ModuleRootComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        
        #return mainWidget
        self.setLayout( verticalLayout )