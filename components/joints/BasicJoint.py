import maya.cmds as cmds
from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.utility.NodeUtility as NodeUtility
import marigold.skeleton.marigoldJoints as marigoldJoints
from marigold.components.BaseComponent import BaseComponent

class BasicJointComponent( BaseComponent ):
    nodeType = 'BasicJointComponent'
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( BasicJointComponent, self ).__init__( node=self.node )
    
    def requiredAttributes( self ):
        super( BasicJointComponent, self ).requiredAttributes()
        NodeUtility.addPlug( self.newNode, 'jointName', 'dataType', 'string' )
        
    @classmethod
    def buildNode( cls, nodeName ):
        '''
        Builds a joint.
        
        @param nodeName: String. Name of the node.
        '''
        jointName = cmds.getAttr( '{0}.jointName'.format( nodeName ) )
        transReference = NodeUtility.getNodeAttrSource( nodeName, 'parentName' )
        return marigoldJoints.createJoint( jointName, transReference[0] )
        
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
            buildAction = QtGui.QAction( 'Build Joint', popMenu, triggered=lambda a=inNodeName:self.buildNode( a ) )
            popMenu.addAction( buildAction )
            
            deleteAction = QtGui.QAction( 'Delete Component', popMenu, triggered=lambda a=inNodeName:self.deleteComponentFromObject( a ) )
            popMenu.addAction( deleteAction )
            
            popMenu.exec_( componentLabel.mapToGlobal( point ) )
        
        # Setup layout.
        verticalLayout = QtGui.QVBoxLayout()
        verticalLayout.setContentsMargins( 0,0,0,0 )
        verticalLayout.setSpacing( 0 )
        verticalLayout.setAlignment( QtCore.Qt.AlignTop )
                
        # Label for component
        componentLabel = QTWidgets.basicLabel( nodeName, 'bold', 10, 'black', '6E9094', inIndent=20 )
        componentLabel.setMinimumHeight( 18 )    
        componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        componentLabel.customContextMenuRequested.connect( lambda point, node=nodeName:on_context_menu( point, node ) )
        
        # Properties
        propertyStack = QtGui.QVBoxLayout()
        
        propertyFrame = QTWidgets.basicFrame()
        propertyFrame.setMinimumHeight( 40 )
        propertyFrame.setMaximumHeight( 40 )
        
        # Add string edit property
        propertyPlug = NodeUtility.getPlug( nodeName, 'jointName' )
        propertyValue = NodeUtility.getPlugValue( propertyPlug )
        jointTextLayout = QTWidgets.stringProperty( 'Joint Name', propertyValue )
        
        propertyStack.addLayout( jointTextLayout )        
        propertyFrame.setLayout( propertyStack )
        
        verticalLayout.addWidget( componentLabel )
        verticalLayout.addWidget( propertyFrame )

        # Connections
        textBox = propertyFrame.findChild( QtGui.QLineEdit )
        textBox.editingFinished.connect( lambda inPlugName='jointName', inQTType='QLineEdit', inPlugValue=textBox, inNodeName=nodeName
                                         :BasicJointComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        
        self.setLayout( verticalLayout )