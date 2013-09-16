from PySide import QtCore
from PySide import QtGui
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.NurbsCurveUtility as NurbsCurveUtility
import marigold.utility.FrameUtility as FrameUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.ui.widgets.QTWidgets as QTWidgets
from marigold.components.BaseComponent import BaseComponent

class CurveControlComponent( BaseComponent ):
    nodeType = 'CurveControlComponent'
    CONTROL = None
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( CurveControlComponent, self ).__init__( node=self.node )
        
    def requiredAttributes( self, *args, **kwargs ):
        print 'kwargs: {0}'.format( kwargs['curveType'] )
        super( CurveControlComponent, self ).requiredAttributes()
        FrameUtility.addPlug( self.newNode, 'controlName', 'dataType', 'string' )
        FrameUtility.addPlug( self.newNode, 'curveType', 'dataType', 'string' )
        self.setAttribute( 'curveType', kwargs['curveType'], self.newNode )
        
        # Add attributes for the curve CVs.
        tempCurve = self.createCurveControl( '{0}TempCurve'.format( self.newNode ), kwargs['curveType'] )
        tempCurveName = OpenMaya.MDagPath.getAPathTo( tempCurve ).fullPathName()
        tempCurvePoints = NurbsCurveUtility.getCurveCvs( tempCurveName )
        NurbsCurveUtility.addCurveValues( self.newNode, tempCurvePoints )
        cmds.delete( tempCurveName )
    
    @property
    def curveType( self ):
        '''
        @return: String. Curve type of the meta node.
        '''
        if cmds.attributeQuery( 'curveType', node=self.node, exists=True ):
            return cmds.getAttr( '{0}.curveType'.format( self.node ) )
        
    def createCurveControl( self, inName, inShape ):
        '''
        @param inName: String. Name of the control curve to create.
        @param inShape: String. Type of shape to create.
        @return: MObject. Control curve.
        '''
        # Point locations for shapes. These are created on the XZ plane.
        square = ( [-1,0,-1], [1,0,-1], [1,0,1], [-1,0,1], [-1,0,-1] )
        
        triangle = ( [0,0,1], [1,0,-1], [-1,0,-1], [0,0,1] )
        
        arrow = ( [0,0,-2], [1,0,0], [0.5,0,0], [0.5,0,2], [-0.5,0,2], [-0.5,0,0], [-1,0,0], [0,0,-2] )
        
        plus = ( [-0.5,0,-2], [0.5,0,-2], [0.5,0,-0.5], [2,0,-0.5], [2,0,0.5], [0.5,0,0.5],
                [0.5,0,2], [-0.5,0,2], [-0.5,0,0.5], [-2,0,0.5], [-2,0,-0.5], [-0.5,0,-0.5], [-0.5,0,-2] )
        
        pyramid = ( [-1,0,-1], [1,0,-1], [1,0,1], [-1,0,1], [-1,0,-1], [0,2,0], [1,0,-1], [1,0,1], [0,2,0], [-1,0,1] )
        
        
        # Grab the points for the passed in shape.
        points = {'square':square,
                  'triangle':triangle,
                  'arrow':arrow,
                  'plus':plus,
                  'pyramid':pyramid}
        
        # Create the shape.
        if inShape == 'circle':
            control = NurbsCurveUtility.createCurveCircle( inName )
        elif inShape == 'ringDirection':
            rdCircle = NurbsCurveUtility.createCurveCircle( inName )
            rdTriangle = NurbsCurveUtility.createCurve( 'triangle', points['triangle'], 1, inForm=False, inOffset=[0,0,1.5], inScale=0.25 )
            cirName = OpenMaya.MDagPath.getAPathTo( rdCircle ).fullPathName()
            triName = OpenMaya.MDagPath.getAPathTo( rdTriangle ).fullPathName()
            control = NurbsCurveUtility.createCompoundCurve( [cirName, triName] )
        else:
            control = NurbsCurveUtility.createCurve( inName, points[inShape], inForm=False )
            
        return control

    def componentGui( self, inNodeName ):        
        def on_context_menu( point, inNodeName ):
            popMenu = QtGui.QMenu()
            deleteAction = QtGui.QAction( 'Delete Component', popMenu, triggered=lambda a=inNodeName:self.deleteComponentFromObject( a ) )
            popMenu.addAction( deleteAction )
            
            popMenu.exec_( self.componentLabel.mapToGlobal( point ) )
        
        mainWidget = QtGui.QWidget()
            
        verticalLayout = QtGui.QVBoxLayout( mainWidget )
        verticalLayout.setContentsMargins( 0,0,0,0 )
        verticalLayout.setSpacing( 0 )
        verticalLayout.setAlignment( QtCore.Qt.AlignTop )
        
        # Label for component
        self.componentLabel = QTWidgets.basicLabel( inNodeName, 'bold', 10, 'black', '6E9094', inIndent=20 )
        self.componentLabel.setMinimumHeight( 18 )    
        self.componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.componentLabel.customContextMenuRequested.connect( lambda point, nodeName=inNodeName:on_context_menu( point, nodeName ) )
        
        propertyFrame = QTWidgets.basicFrame()
        propertyFrame.setMinimumHeight( 80 )
        propertyFrame.setMaximumHeight( 80 )
        
        propertyStack = QtGui.QVBoxLayout()
        
        # Add string edit property
        propertyRow = QtGui.QHBoxLayout()
        propertyPlug = NodeUtility.getPlug( inNodeName, 'controlName' )
        propertyValue = NodeUtility.getPlugValue( propertyPlug )
        self.textBox = QtGui.QLineEdit()
        self.textBox.setAlignment( QtCore.Qt.AlignLeft )
        self.textBox.setMinimumHeight( 20 )
        if propertyValue:
            self.textBox.setText( propertyValue )
        
        textBoxLabel = QtGui.QLabel()
        textBoxLabel.setText( 'Control Name' )
        textBoxLabel.setAlignment( QtCore.Qt.AlignCenter )
        textBoxLabel.setMinimumHeight( 12 )
        
        propertyRow.addWidget( self.textBox )
        propertyRow.addWidget( textBoxLabel )
        
        # Edit buttons.
        self.editBtn = QtGui.QPushButton()
        self.editBtn.setText( 'Edit Control' )
        self.editBtn.clicked.connect( self.editControl )
        
        self.saveBtn = QtGui.QPushButton()
        self.saveBtn.setText( 'Save Control' )
        self.editBtn.clicked.connect( self.saveControl )
        '''
        self.editButton = QtGui.QToolButton()
        #editButton.setAutoRaise( True )
        self.editButton.setCheckable( True )
        self.editButton.setText( 'Edit Control' )
        self.editButton.toggled.connect( lambda:self.saveProperties() )
        '''
        
        propertyStack.addLayout( propertyRow )
        #propertyStack.addWidget( self.editButton )
        propertyStack.addWidget( self.editBtn )
        propertyStack.addWidget( self.saveBtn )
        propertyFrame.setLayout( propertyStack )
        
        # Add everything to the vertical layout.
        verticalLayout.addWidget( self.componentLabel )
        verticalLayout.addWidget( propertyFrame )
        
        # Connections
        #textBox = propertyFrame.findChild( QtGui.QLineEdit )
        self.textBox.editingFinished.connect( lambda inPlugName='controlName', inQTType='QLineEdit', inPlugValue=self.textBox, inNodeName=inNodeName
                                         :self.setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        return mainWidget
    
    def editControl( self ):
        print self.parent().ACTIVE_CONTROL_EDITS
        
        '''
        if self.textBox.text():
            curveType = CurveControlComponent( self.componentLabel.text() ).curveType
            node = self.createCurveControl( self.textBox.text(), curveType )
            self.CONTROL = OpenMaya.MDagPath.getAPathTo( node ).fullPathName()

            # Set the control to the bit's transform
            parentNode = CurveControlComponent( self.componentLabel.text() ).parentNode[0]
            TransformUtility.matchObjectTransforms( parentNode, self.CONTROL )
            
            # Get the saved properties and apply them to the curve.
        else:
            raise ValueError( '{0} does not have a Control Name set.'.format( self.CONTROL ) )
        '''
        
    def saveControl( self ):
        if self.CONTROL is not None:
            # Read the control properties and save them to the component node.
        
            # Delete the control
            cmds.delete( self.CONTROL )
            self.CONTROL = None
    
    def saveProperties( self ):
        if self.editButton.isChecked():
            # Create the curve control
            if self.textBox.text():
                curveType = CurveControlComponent( self.componentLabel.text() ).curveType
                node = self.createCurveControl( self.textBox.text(), curveType )
                self.CONTROL = OpenMaya.MDagPath.getAPathTo( node ).fullPathName()

                # Set the control to the bit's transform
                parentNode = CurveControlComponent( self.componentLabel.text() ).parentNode[0]
                TransformUtility.matchObjectTransforms( parentNode, self.CONTROL )
                
                # Get the saved properties and apply them to the curve.
                
            else:
                raise ValueError( '{0} does not have a Control Name set.'.format( self.CONTROL ) )
        else:
            if self.CONTROL is not None:
                # Read the control properties and save them to the component node.
            
                # Delete the control
                cmds.delete( self.CONTROL )
                self.CONTROL = None