from PySide import QtCore
from PySide import QtGui
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.NurbsCurveUtility as NurbsCurveUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.GeneralUtility as GeneralUtility
import marigold.ui.widgets.QTWidgets as QTWidgets
from marigold.components.BaseComponent import BaseComponent
from marigold.components.controls import storeControlTransforms
from marigold.components.controls import applyStoredTransforms

class CurveControlComponent( BaseComponent ):
    '''
    Nurbs curve control component. Extends BaseComponent class.
    '''
    nodeType = 'CurveControlComponent'
    
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( CurveControlComponent, self ).__init__( node=self.node )
        
    def requiredAttributes( self, *args, **kwargs ):
        '''
        kwargs
        curveType: Type of curve control to make. Square, triangle, arrow, plus, pyramid, circle, ringDirection.
        '''
        super( CurveControlComponent, self ).requiredAttributes()
        NodeUtility.addPlug( self.newNode, 'controlName', 'dataType', 'string' )
        NodeUtility.addPlug( self.newNode, 'curveType', 'dataType', 'string' )
        self.setAttribute( 'curveType', kwargs['curveType'], self.newNode )
        
        # Add attribute for control color.
        NodeUtility.addPlug( self.newNode, 'controlColor', 'attributeType', 'byte' )
        self.setAttribute( 'controlColor', 1, self.newNode )
        
        # Control transform relative to the parent.
        NodeUtility.addPlug( self.newNode, 'controlPosition', 'attributeType', 'float3' )
        NodeUtility.addPlug( self.newNode, 'controlRotation', 'attributeType', 'float3' )
        NodeUtility.addPlug( self.newNode, 'controlScale', 'attributeType', 'float3' )
        
        # Add attributes for the curve CVs.
        tempCurve = self.createCurveControl( '{0}TempCurve'.format( self.newNode ), kwargs['curveType'] )
        tempCurveName = OpenMaya.MDagPath.getAPathTo( tempCurve ).fullPathName()
        tempCurvePoints = NurbsCurveUtility.getCurveCvs( tempCurveName )
        NurbsCurveUtility.addCurveValues( self.newNode, tempCurvePoints )
        
        # Update curve transform values.
        storeControlTransforms( tempCurveName, self.newNode )
        
        # Clean up.
        cmds.delete( tempCurveName )
    
    @property
    def curveType( self ):
        '''
        Returns the type of curve control used by the component.
        
        @return: String. Curve type of the meta node.
        '''
        if cmds.attributeQuery( 'curveType', node=self.node, exists=True ):
            return cmds.getAttr( '{0}.curveType'.format( self.node ) )
        
    def createCurveControl( self, inName, inShape ):
        '''
        Creates a nurbs curve control.
        
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
    
    def componentGui( self, inNodeName, parent=None ):
        '''
        Creates the QT gui for this component.
        
        @return: QWidget.
        '''
        return componentWidget( inNodeName, parent=parent )
    
class componentWidget( QtGui.QWidget ):
    '''
    QT QWidget class for this component.
    
    Normally this would be a function in the component class itself, but for this component
    I needed to have access to the parent QT window (to toggle the lock selection on/off). So
    I moved the QT stuff into a stand alone class that takes a parent (the main QT window), which
    can then be used to get functions and variables from the main window.
    '''
    CONTROL = None
    COLOR = None
    
    def __init__( self, nodeName, parent=None ):
        super( componentWidget, self ).__init__( parent )
        self.parent = parent
         
        def on_context_menu( point, inNodeName ):
            popMenu = QtGui.QMenu()
            deleteAction = QtGui.QAction( 'Delete Component', popMenu, triggered=lambda a=inNodeName:self.deleteComponentFromObject( a ) )
            popMenu.addAction( deleteAction )
            
            popMenu.exec_( self.componentLabel.mapToGlobal( point ) )
        
        # Colors.
        userColors = GeneralUtility.getUserDefinedColors( inType=1 )
        self.colorList = []
        for color in userColors:
            self.colorList.append( GeneralUtility.convertRGB( color, inType=1 ) )
        
        # Setup layout.
        verticalLayout = QtGui.QVBoxLayout()
        verticalLayout.setContentsMargins( 0,0,0,0 )
        verticalLayout.setSpacing( 0 )
        verticalLayout.setAlignment( QtCore.Qt.AlignTop )
        
        # Label for component
        #self.componentLabel = QTWidgets.basicLabel( nodeName, 'bold', 10, 'black', '6E9094', inIndent=20 )
        self.componentLabel = QtGui.QLabel()
        self.componentLabel.setText( nodeName )
        self.componentLabel.setIndent( 20 )
        controlColorPlug = NodeUtility.getPlug( nodeName, 'controlColor' )
        self.COLOR = NodeUtility.getPlugValue( controlColorPlug )
        self.componentLabel.setStyleSheet( 'font:bold; font-size:10px; color:black; background-color:rgb({0},{1},{2})'.format(self.colorList[self.COLOR-1][0],
                                                                                                                              self.colorList[self.COLOR-1][1],
                                                                                                                              self.colorList[self.COLOR-1][2] ) )
        self.componentLabel.setMinimumHeight( 18 )
        self.componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
        self.componentLabel.customContextMenuRequested.connect( lambda point, nodeName=nodeName:on_context_menu( point, nodeName ) )
        
        propertyFrame = QTWidgets.basicFrame()
        propertyFrame.setMinimumHeight( 100 )
        propertyFrame.setMaximumHeight( 100 )
        
        propertyStack = QtGui.QVBoxLayout()
        
        # Add string edit property
        propertyRow = QtGui.QHBoxLayout()
        propertyPlug = NodeUtility.getPlug( nodeName, 'controlName' )
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
        
        # Colors.
        colorRow = QtGui.QHBoxLayout()
        
        color1Btn = QtGui.QPushButton()
        color1Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[0][0], self.colorList[0][1], self.colorList[0][2] ) )
        color1Btn.clicked.connect( lambda a=nodeName, b=1:self.colorChange( a, b ) )
        
        color2Btn = QtGui.QPushButton()
        color2Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[1][0], self.colorList[1][1], self.colorList[1][2] ) )
        color2Btn.clicked.connect( lambda a=nodeName, b=2:self.colorChange( a, b ) )
        
        color3Btn = QtGui.QPushButton()
        color3Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[2][0], self.colorList[2][1], self.colorList[2][2] ) )
        color3Btn.clicked.connect( lambda a=nodeName, b=3:self.colorChange( a, b ) )
        
        color4Btn = QtGui.QPushButton()
        color4Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[3][0], self.colorList[3][1], self.colorList[3][2] ) )
        color4Btn.clicked.connect( lambda a=nodeName, b=4:self.colorChange( a, b ) )
        
        color5Btn = QtGui.QPushButton()
        color5Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[4][0], self.colorList[4][1], self.colorList[4][2] ) )
        color5Btn.clicked.connect( lambda a=nodeName, b=5:self.colorChange( a, b ) )
        
        color6Btn = QtGui.QPushButton()
        color6Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[5][0], self.colorList[5][1], self.colorList[5][2] ) )
        color6Btn.clicked.connect( lambda a=nodeName, b=6:self.colorChange( a, b ) )
        
        color7Btn = QtGui.QPushButton()
        color7Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[6][0], self.colorList[6][1], self.colorList[6][2] ) )
        color7Btn.clicked.connect( lambda a=nodeName, b=7:self.colorChange( a, b ) )
        
        color8Btn = QtGui.QPushButton()
        color8Btn.setStyleSheet( 'background-color:rgb({0},{1},{2}); width:20'.format( self.colorList[7][0], self.colorList[7][1], self.colorList[7][2] ) )
        color8Btn.clicked.connect( lambda a=nodeName, b=8:self.colorChange( a, b ) )
        
        colorRow.addWidget( color1Btn )
        colorRow.addWidget( color2Btn )
        colorRow.addWidget( color3Btn )
        colorRow.addWidget( color4Btn )
        colorRow.addWidget( color5Btn )
        colorRow.addWidget( color6Btn )
        colorRow.addWidget( color7Btn )
        colorRow.addWidget( color8Btn )        
        
        # Edit buttons.
        self.editButton = QtGui.QToolButton()
        self.editButton.setCheckable( True )
        self.editButton.setText( 'Edit Control' )
        self.editButton.toggled.connect( lambda:self.editCurveProperties() )
        
        propertyStack.addLayout( propertyRow )
        propertyStack.addLayout( colorRow )
        propertyStack.addWidget( self.editButton )
        propertyFrame.setLayout( propertyStack )
        
        # Add everything to the vertical layout.
        verticalLayout.addWidget( self.componentLabel )
        verticalLayout.addWidget( propertyFrame )
        
        # Connections
        self.textBox.editingFinished.connect( lambda inPlugName='controlName', inQTType='QLineEdit', inPlugValue=self.textBox, inNodeName=nodeName
                                         :CurveControlComponent( inNodeName ).setComponentAttributeFromQT( inPlugName, inQTType, inPlugValue, inNodeName ) )
        #return mainWidget
        self.setLayout( verticalLayout )
    
    def colorChange( self, inNodeName, inPlugValue ):
        '''
        Sets the color of the control. Also changes the component label to the selected color.
        
        @param inNodeName: String. Name of the component node.
        @param inPlugValue: Int. 1-8. Which user defined color to use for the control.
        '''
        CurveControlComponent( inNodeName ).setComponentAttributeFromQT( 'controlColor', None, inPlugValue, inNodeName )
        self.componentLabel.setStyleSheet( 'background-color:rgb({0},{1},{2})'.format( self.colorList[inPlugValue-1][0], self.colorList[inPlugValue-1][1], self.colorList[inPlugValue-1][2] ) )
        self.COLOR = inPlugValue
        if self.editButton.isChecked():
            # Set the color of the control being edited.
            GeneralUtility.setUserColor( self.CONTROL, userColor=self.COLOR )
        
    def editCurveProperties( self ):
        '''
        Activates the control so the user can edit it's properties.
        '''
        if self.editButton.isChecked():
            if self.textBox.text():
                # Lock the components UI.
                if self.parent.selectedLockActive is False:
                    self.parent.lockSelection()
                
                # Create the curve.
                curveType = CurveControlComponent( self.componentLabel.text() ).curveType
                node = CurveControlComponent( self.componentLabel.text() ).createCurveControl( self.textBox.text(), curveType )
                controlName = OpenMaya.MDagPath.getAPathTo( node ).fullPathName()
                
                # Parent the control to the bit.
                parentNode = CurveControlComponent( self.componentLabel.text() ).parentNode[0]
                cmds.parent( controlName, parentNode )
                self.CONTROL = OpenMaya.MDagPath.getAPathTo( node ).fullPathName()
                
                # Set the control to the transform matrix.
                applyStoredTransforms( self.componentLabel.text(), self.CONTROL )
                
                # Get the saved properties and apply them to the curve.
                cvList = NurbsCurveUtility.readCurveValues( self.componentLabel.text() )
                cvPointArray = NurbsCurveUtility.buildCVPointArray( cvList )
                NurbsCurveUtility.setCurveCvs( self.CONTROL, cvPointArray )
                
                # Color.
                GeneralUtility.setUserColor( self.CONTROL, userColor=self.COLOR )
            else:
                raise ValueError( '{0} does not have a Control Name set.'.format( self.componentLabel.text() ) )
        else:
            if self.CONTROL is not None:
                # Read the control properties and save them to the component node.
                cvList = NurbsCurveUtility.getCurveCvs( self.CONTROL )
                NurbsCurveUtility.writeCurveValues( self.componentLabel.text(), cvList )
                
                # Update the transform matrix.
                storeControlTransforms( self.CONTROL, self.componentLabel.text() )

                # Delete the control
                cmds.delete( self.CONTROL )
                self.CONTROL = None
                
            # Unlock the UI.
            if self.parent.selectedLockActive:
                self.parent.lockSelection()