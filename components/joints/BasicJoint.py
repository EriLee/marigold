import maya.cmds as cmds
from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.utility.FrameUtility as FrameUtility
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
        FrameUtility.addPlug( self.newNode, 'jointName', 'dataType', 'string' )
        
    @classmethod
    def buildNode( cls, nodeName ):
        '''
        Builds a joint.
        
        @param nodeName: String. Name of the node.
        '''
        jointName = cmds.getAttr( '{0}.jointName'.format( nodeName ) )
        transReference = NodeUtility.getNodeAttrSource( nodeName, 'parentName' )
        marigoldJoints.createJoint( jointName, transReference[0], inPrefix='j' )
        
    def componentGui( self, inNodeName ):        
        def on_context_menu( point, inNodeName ):
            popMenu = QtGui.QMenu()
            buildAction = QtGui.QAction( 'Build Joint', popMenu, triggered=lambda a=inNodeName:self.buildNode( a ) )
            popMenu.addAction( buildAction )
            
            deleteAction = QtGui.QAction( 'Delete Component', popMenu, triggered=lambda a=inNodeName:self.deleteComponentFromObject( a ) )
            popMenu.addAction( deleteAction )
            
            popMenu.exec_( componentLabel.mapToGlobal( point ) )
        
        mainWidget = QtGui.QWidget()
            
        verticalLayout = QtGui.QVBoxLayout( mainWidget )
        verticalLayout.setContentsMargins( 0,0,0,0 )
        verticalLayout.setSpacing( 0 )
        verticalLayout.setAlignment( QtCore.Qt.AlignTop )
        
        # Label for component
        componentLabel = QTWidgets.basicLabel( inNodeName, 'bold', 10, 'black', '6E9094', inIndent=20 )
        componentLabel.setMinimumHeight( 18 )    
        componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        componentLabel.customContextMenuRequested.connect( lambda point, nodeName=inNodeName:on_context_menu( point, nodeName ) )
        
        propertyFrame = QTWidgets.basicFrame()
        propertyFrame.setMinimumHeight( 40 )
        propertyFrame.setMaximumHeight( 40 )
        
        # Add string edit property
        propertyPlug = NodeUtility.getPlug( inNodeName, 'jointName' )
        propertyValue = NodeUtility.getPlugValue( propertyPlug )
        QTWidgets.stringProperty( 'Joint Name', propertyValue, inParent=propertyFrame )
        
        # Add everything to the vertical layout.
        verticalLayout.addWidget( componentLabel )
        verticalLayout.addWidget( propertyFrame )
        
        # Connections
        textBox = propertyFrame.findChild( QtGui.QLineEdit )
        textBox.editingFinished.connect( lambda inPlugName='jointName', inQTType='QLineEdit', inPlugValue=textBox, inNodeName=inNodeName
                                         :self.setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        return mainWidget