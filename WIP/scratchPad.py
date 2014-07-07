import os
import math
import sys
import types
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import marigold.utility.NodeUtility as NodeUtility
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.XMLUtility as XMLUtility
import marigold.controllers.marigoldControls as marigoldControls
import marigold.skeleton.marigoldJoints as marigoldJoints
import marigold.meta.metaNode as metaNode
import marigold.utility.NurbsCurveUtility as NurbsCurveUtility
import marigold.components as Components
import marigold.utility.GeneralUtility as GeneralUtility


# @@@@@
'''
# making a matrix attr with cmd
cmds.addAttr( newObj, longName='testMatrix', dataType="matrix")
cmds.setAttr( '{0}.testMatrix'.format(newObj), (1,0,0,0,0,1,0,0,0,0,1,0,2,3,4,1), type='matrix' )
'''

'''
selList = cmds.ls( selection=True )
parent = selList[0]
print parent
children = cmds.listRelatives( parent, type='transform', allDescendents=True )
pShape = cmds.listRelatives( parent, type='shape', allDescendents=False )
print children
print pShape

shapes = cmds.listRelatives( pShape[0], type='shape', allDescendents=True )
print shapes
'''

'''
displayRGBColor -c userDefined1 0.904 0.889783 0.2712;
displayRGBColor -c userDefined2 0.607843 0.229029 0.182353;
displayRGBColor -c userDefined3 0.4095 0.63 0.189;
displayRGBColor -c userDefined4 0.189 0.63 0.3654;
displayRGBColor -c userDefined5 0.189 0.63 0.63;
displayRGBColor -c userDefined6 0.189 0.4051 0.63;
displayRGBColor -c userDefined7 0.43596 0.189 0.63;
displayRGBColor -c userDefined8 0.63 0.189 0.41391;
'''

        

def addMatrixAttr( targetObj, attrName ):
    mObj = NodeUtility.getDependNode( targetObj )
    dgModifier = OpenMaya.MDGModifier()

    mAttr = OpenMaya.MFnMatrixAttribute()
    controlMatrix = mAttr.create( attrName, attrName, OpenMaya.MFnMatrixAttribute.kDouble )
    dgModifier.addAttribute( mObj, controlMatrix )
    dgModifier.doIt()
        

#========================
import maya.OpenMayaUI as omui
from PySide import QtCore
from PySide import QtGui
from shiboken import wrapInstance
import maya.cmds as cmds
import marigold.ui.qtui_resources

def maya_main_window():
    '''
    Return the Maya main window as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtGui.QWidget )


class MainWindow( QtGui.QDialog ):
    def __init__( self, parent=maya_main_window() ):
        super( MainWindow, self ).__init__( parent )
        
        self.winName = 'My Main Window'        
        self.create()
        
    def create( self ):
        # Check to see if this UI is already open. If it is then delete it before
        # creating it anew.
        if cmds.window( self.winName, exists=True ):
            cmds.deleteUI( self.winName )

        layout = QtGui.QVBoxLayout()
        testWidget = MainWidget()
        layout.addWidget( testWidget )
        self.setLayout( layout )
        
        
class MainWidget( QtGui.QWidget ):
    def __init__( self, parent=None ):
        super( MainWidget, self ).__init__( parent )
        
        self.pen = QtGui.QPen( QtCore.Qt.SolidLine )
        self.pen.setColor( QtCore.Qt.red )
        self.pen.setWidth( 2 )
        
        self.brush = QtGui.QBrush( QtGui.QColor( 30,56,209,100 ) )
        
        self.pixmap = QtGui.QPixmap( ':/riggingUI/icons/bg_test.png' )
        self.pixmapItem = QtGui.QGraphicsPixmapItem( self.pixmap )
        #self.pixmapItem = MyPixmapItem( self.pixmap )
        
        self.scene = QtGui.QGraphicsScene()
        self.scene.addItem( self.pixmapItem )
        
        # Polygon draw
        polyOffset = [200, 200]
        polyPoints = [[0,0],[0,100],[100,100],[100,0]]
        polyShape = QtGui.QPolygonF()
        for i in polyPoints:
            polyShape.append( QtCore.QPointF( i[0]+polyOffset[0], i[1]+polyOffset[1] ) )
        polyItem = MyPolygonItem( polyShape )
        self.scene.addItem( polyItem )
        
        self.view = QtGui.QGraphicsView( self.scene )
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget( self.view )
        self.setLayout( layout )
        
        
class MyPixmapItem( QtGui.QGraphicsPixmapItem ):
    def __init__( self, pixmap=None ):
        super( MyPixmapItem, self ).__init__( pixmap )
        
        self.setAcceptHoverEvents( True )
        
    def hoverEnterEvent( self, event ):
        pass
        
    def hoverLeaveEvent( self, event ):
        pass
        
    def hoverMoveEvent( self, event ):
        pass
    

class MyPolygonItem( QtGui.QGraphicsPolygonItem ):
    def __init__( self, polygon=None ):
        super( MyPolygonItem, self ).__init__( polygon )
        
        self.polygon = polygon
        
        self.setAcceptHoverEvents( True )
        
        self.active = False
        
        # Hover pen and brush
        self.hoverPen = QtGui.QPen( QtCore.Qt.SolidLine )
        self.hoverPen.setColor( QtCore.Qt.black )
        self.hoverPen.setWidth( 2 )
        self.hoverBrush = QtGui.QBrush( QtGui.QColor( 30,156,209,100 ) )
        
        # Leave pen and brush. Also the default colors.
        self.leavePen = QtGui.QPen( QtCore.Qt.SolidLine )
        self.leavePen.setColor( QtCore.Qt.red )
        self.leavePen.setWidth( 2 )
        self.leaveBrush = QtGui.QBrush( QtGui.QColor( 30,56,209,100 ) )
        
        # Mouse press pen and brush.
        self.activePen = QtGui.QPen( QtCore.Qt.DotLine )
        self.activePen.setColor( QtCore.Qt.green )
        self.activePen.setWidth( 4 )
        self.activeBrush = QtGui.QBrush( QtGui.QColor( 130,56,209,100 ) )
        
        # Setup the default pen and brush
        self.setPen( self.leavePen )
        self.setBrush( self.leaveBrush )
        
    def hoverEnterEvent( self, event ):
        if self.active:
            self.setPen( self.pressPen )
            self.setBrush( self.activeBrush )
        else:
            self.setPen( self.hoverPen )
            self.setBrush( self.hoverBrush )
        
    def hoverLeaveEvent( self, event ):
        if self.active:
            self.setPen( self.pressPen )
            self.setBrush( self.activeBrush )
        else:
            self.setPen( self.leavePen )
            self.setBrush( self.leaveBrush )
        
    def hoverMoveEvent( self, event ):
        pass

    def mousePressEvent( self, event ):
        if not self.active:   
            self.setPen( self.activePen )
            self.setBrush( self.activeBrush )
            self.active = True
        else:
            self.setPen( self.hoverPen )
            self.setBrush( self.hoverBrush )
            self.active = False
'''
    RUN THE WINDOW
'''
testUI = MainWindow()
testUI.show()