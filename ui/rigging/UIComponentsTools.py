'''
UI COMPONENTS TOOLS

Creates a QtGui.QWidget object containing all the UI and functionality for
creating/editing components.

By: Austin Baker
Date: 9/5/2013
'''
from PySide import QtCore
from PySide import QtGui

import maya.cmds as cmds

from marigold.ui import clearLayout
from marigold.ui import mayaToQtObject
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.components as Components

class UIComponentsTools( QtGui.QWidget ):
    SCRIPT_JOB_NUMBER = -1
    SELECTED_OBJECT_LONGNAME = None
        
    def __init__( self ):
        super( UIComponentsTools, self ).__init__()
        
        layout = QtGui.QVBoxLayout( self )

        # COMPONENTS MENU BAR
        menuFrame = QtGui.QFrame()
        menuFrame.setMinimumHeight( 20 )
        
        # Meta menu.
        moduleMeta = QtGui.QAction( '&Module Meta', self)
        moduleMeta.triggered.connect( lambda a='ModuleRootComponent':Components.addComponentToObject( a ) )
        characterMeta = QtGui.QAction( '&Character Meta', self)
        characterMeta.triggered.connect( lambda a='CharacterRootComponent':Components.addComponentToObject( a ) )
        
        # Joints menu
        basicJoint = QtGui.QAction( '&Basic Joint', self)
        #basic_joint.setShortcut('Ctrl+Q')
        #basic_joint.setStatusTip('Exit application')
        basicJoint.triggered.connect( lambda a='BasicJointComponent':Components.addComponentToObject( a ) )
        
        # Controls menu
        squareCurveControl = QtGui.QAction( '&Square', self)
        squareCurveControl.triggered.connect( lambda a='CurveControlComponent', b='square':Components.addComponentToObject( a, curveType=b ) )
        triangleCurveControl = QtGui.QAction( '&Triangle', self)
        triangleCurveControl.triggered.connect( lambda a='CurveControlComponent', b='triangle':Components.addComponentToObject( a, curveType=b ) )
        arrowCurveControl = QtGui.QAction( '&Arrow', self)
        arrowCurveControl.triggered.connect( lambda a='CurveControlComponent', b='arrow':Components.addComponentToObject( a, curveType=b ) )
        plusCurveControl = QtGui.QAction( '&Plus', self)
        plusCurveControl.triggered.connect( lambda a='CurveControlComponent', b='plus':Components.addComponentToObject( a, curveType=b ) )
        pyramidCurveControl = QtGui.QAction( '&Pyramid', self)
        pyramidCurveControl.triggered.connect( lambda a='CurveControlComponent', b='pyramid':Components.addComponentToObject( a, curveType=b ) )
        circleCurveControl = QtGui.QAction( '&Circle', self)
        circleCurveControl.triggered.connect( lambda a='CurveControlComponent', b='circle':Components.addComponentToObject( a, curveType=b ) )
        ringDirectionCurveControl = QtGui.QAction( '&Ring Direction', self)
        ringDirectionCurveControl.triggered.connect( lambda a='CurveControlComponent', b='ringDirection':Components.addComponentToObject( a, curveType=b ) )
        
        # Setup menus.
        componentsMenubar = QtGui.QMenuBar( menuFrame )
        
        metaMenu = componentsMenubar.addMenu( '&Meta' )
        metaMenu.addAction( moduleMeta )
        metaMenu.addAction( characterMeta )
        
        jointsMenu = componentsMenubar.addMenu( '&Joints' )
        jointsMenu.addAction( basicJoint )
        
        controlsMenu = componentsMenubar.addMenu( '&Controls' )
        controlsCurvesMenu = controlsMenu.addMenu( '&Curves' )
        controlsCurvesMenu.addAction( squareCurveControl )
        controlsCurvesMenu.addAction( triangleCurveControl )
        controlsCurvesMenu.addAction( arrowCurveControl )
        controlsCurvesMenu.addAction( plusCurveControl )
        controlsCurvesMenu.addAction( pyramidCurveControl )
        controlsCurvesMenu.addAction( circleCurveControl )
        controlsCurvesMenu.addAction( ringDirectionCurveControl )
        
        constraintsMenu = componentsMenubar.addMenu( '&Constraints' )
        
        deformersMenu = componentsMenubar.addMenu( '&Deformers' )
        

        # SELECTED HEADER
        self.selectedLockBtn = QTWidgets.imageTextButton( '', ':/riggingUI/icons/lock_off.png', [16,16] )
        self.selectedLockBtn.setMaximumWidth( 30 )
        self.selectedLockBtn.clicked.connect( self.lockSelection )
        self.selectedLockActive = False
        
        self.selectedLabel = QTWidgets.basicLabel( 'nothing selected', 'bold', 14, 'white', '2B2B30', inIndent=10 )
        self.selectedLabel.setMinimumHeight( 30 )
        self.selectedLabel.setAlignment( QtCore.Qt.AlignCenter )
        
        selectedGrid = QtGui.QGridLayout()
        selectedGrid.setContentsMargins( 0, 0, 0, 0 )
        selectedGrid.setHorizontalSpacing( 0 )
        selectedGrid.setColumnMinimumWidth( 0, 30 )
        selectedGrid.addWidget( self.selectedLockBtn, 0, 0 )
        selectedGrid.addWidget( self.selectedLabel, 0, 1 )
        
        # SELECTED COMPONENTS LIST/EDITOR        
        # Add the component specific GUI.
        self.componentsLayout = QtGui.QVBoxLayout()
        self.componentsLayout.setAlignment( QtCore.Qt.AlignTop )
        scrollArea = QTWidgets.scrollArea( self.componentsLayout )
        
        # Layout hookup
        layout.addWidget( menuFrame )
        layout.addLayout( selectedGrid )
        layout.addWidget( scrollArea )
        
        # In order to delete this scriptJob when this UI is destroyed we need to
        # parent the scriptJob to a Maya UI item. In this case I'm using a text object
        # with visibility turned off.
        scriptJobHolder = cmds.text( visible=False )
        self.SCRIPT_JOB_NUMBER = cmds.scriptJob( event=[ 'SelectionChanged', self.onSelectionChange ], protected=True, parent=scriptJobHolder )
        scriptJobHolderQT = mayaToQtObject( scriptJobHolder )
        layout.addWidget( scriptJobHolderQT )
        
    def lockSelection( self ):
        '''
        Locks the current object selection.
        This allows the user to select other things while keeping the component GUI locked
        on a particular object.
        '''
        if not self.selectedLockActive:
            self.selectedLockActive = True
            self.selectedLockBtn.setIcon( QtGui.QIcon( ':/riggingUI/icons/lock_on.png' ) )
        else:
            self.selectedLockActive = False
            self.selectedLockBtn.setIcon( QtGui.QIcon( ':/riggingUI/icons/lock_off.png' ) )
            self.onSelectionChange()
            
    def onSelectionChange( self ):
        '''
        Function called by the scripted event in componentsGUI().
        Updates the componentGUI whenever the user selects a different object.
        '''
        selList = cmds.ls( selection=1, long=True )
        if not self.selectedLockActive:
            clearLayout( self.componentsLayout )
            if len( selList ) == 1:
                shortName = selList[0].split( '|' )
                selName = shortName[ len(shortName)-1 ]
                self.selectedLabel.setText( selName )
                self.SELECTED_OBJECT_LONGNAME = selList[0]
                componentsClassList = Components.getComponents( self.SELECTED_OBJECT_LONGNAME )
                
                # Add the component node GUI widgets to the component section.
                if componentsClassList is not None:
                    for nodeName in componentsClassList:
                        component = componentsClassList[ nodeName ]
                        nodeName = nodeName
                        componentClass = Components.str_to_class( component )
                        componentGui = componentClass( component ).componentGui( nodeName, parent=self )
                        self.componentsLayout.addWidget( componentGui )
                        

            elif len( selList ) > 1:
                if not self.selectedLockActive:
                    self.SELECTED_OBJECT_LONGNAME = None
                    self.selectedLabel.setText( 'select only one module bit' )
            else:
                if not self.selectedLockActive:
                    self.SELECTED_OBJECT_LONGNAME = None
                    self.selectedLabel.setText( 'nothing selected' )
    