'''
UI BITS TOOLS

Creates a QtGui.QWidget object containing all the UI and functionality for
creating bits.

By: Austin Baker
Date: 9/5/2013
'''
from PySide import QtCore
from PySide import QtGui

import maya.cmds as cmds

import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.ui.qtui_resources
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.FrameUtility as FrameUtility

class UIBitsTools( QtGui.QWidget ):
    def __init__( self ):
        super( UIBitsTools, self ).__init__()
        
        layout = QtGui.QVBoxLayout( self )

        # Build bits controls
        # Primitive buttons.        
        sphereBtn = QTWidgets.imageButton( 'Sphere', ':/riggingUI/icons/bit_sphere.png', [32,32] )
        sphereBtn.clicked.connect( self.primitive_buttons )
        
        boxBtn = QTWidgets.imageButton( 'Box', ':/riggingUI/icons/bit_box.png', [32,32] )
        boxBtn.clicked.connect( self.primitive_buttons )
        
        cylinderBtn = QTWidgets.imageButton( 'Cylinder', ':/riggingUI/icons/bit_cylinder.png', [32,32] )
        cylinderBtn.clicked.connect( self.primitive_buttons )
        
        coneBtn = QTWidgets.imageButton( 'Cone', ':/riggingUI/icons/bit_cone.png', [32,32] )
        coneBtn.clicked.connect( self.primitive_buttons )
        
        torusBtn = QTWidgets.imageButton( 'Torus', ':/riggingUI/icons/bit_torus.png', [32,32] )
        torusBtn.clicked.connect( self.primitive_buttons )
        
        # Bit tools.
        matchTranslationBtn = QTWidgets.imageTextButton( 'Match Translation', ':/riggingUI/icons/icon_match_translation.png', [16,16] )
        matchTranslationBtn.clicked.connect( lambda a='tran':TransformUtility.matchTransforms( a ) )
        
        matchRotationBtn = QTWidgets.imageTextButton( 'Match Rotation', ':/riggingUI/icons/icon_match_rotation.png', [16,16] )
        matchRotationBtn.clicked.connect( lambda a='rot':TransformUtility.matchTransforms( a ) )
        
        matchAllBtn = QTWidgets.imageTextButton( 'Match All', ':/riggingUI/icons/icon_match_all.png', [16,16] )
        matchAllBtn.clicked.connect( lambda a='all':TransformUtility.matchTransforms( a ) )
        
        copyBitSettingsBtn = QTWidgets.imageTextButton( 'Copy Bit Settings', ':/riggingUI/icons/bit_copy_settings.png', [16,16] )
        copyBitSettingsBtn.clicked.connect( lambda:FrameUtility.copyBitSettings() )
        
        addChildBtn = QTWidgets.imageTextButton( 'Add Child', ':/riggingUI/icons/bit_add_child.png', [16,16] ) 
        addChildBtn.clicked.connect( lambda:FrameUtility.setBitChild() )
        
        deleteChildBtn = QTWidgets.imageTextButton( 'Delete Child', ':/riggingUI/icons/bit_delete_child.png', [16,16] )
        deleteChildBtn.clicked.connect( lambda:FrameUtility.deleteBitChild() )
        
        # Build bits layout.
        # Primitive buttons
        bitPrimitivesHeader = QTWidgets.basicLabel( 'Bit Primitives', 'bold', 14, 'white', '2B2B30' )
        bitPrimitivesHeader.setMinimumHeight( 30 )
        bitPrimitivesHeader.setAlignment( QtCore.Qt.AlignCenter )
        
        primitiveFrame = QTWidgets.basicFrame()
        
        primitiveLayout = QtGui.QHBoxLayout()
        primitiveLayout.addWidget( sphereBtn )
        primitiveLayout.addWidget( boxBtn )
        primitiveLayout.addWidget( cylinderBtn )
        primitiveLayout.addWidget( coneBtn )
        primitiveLayout.addWidget( torusBtn )
        primitiveFrame.setLayout( primitiveLayout )
        
        # Bit tools.
        bitToolsHeader = QTWidgets.basicLabel( 'Bit Tools', 'bold', 14, 'white', '2B2B30' )
        bitToolsHeader.setMinimumHeight( 30 )
        bitToolsHeader.setAlignment( QtCore.Qt.AlignCenter )
        
        bitToolsGrid = QtGui.QGridLayout()
        bitToolsGrid.setColumnMinimumWidth( 0, 100 )
        bitToolsGrid.setColumnMinimumWidth( 1, 100 )
        bitToolsGrid.setColumnMinimumWidth( 2, 100 )
        bitToolsGrid.setSpacing( 2 )
        bitToolsGrid.setContentsMargins( 0,0,0,0 )
        # widget, row, col
        bitToolsGrid.addWidget( matchTranslationBtn, 0, 0 )
        bitToolsGrid.addWidget( matchRotationBtn, 0, 1 )
        bitToolsGrid.addWidget( matchAllBtn, 0, 2 )
        bitToolsGrid.addWidget( copyBitSettingsBtn, 1, 0 )
        bitToolsGrid.addWidget( addChildBtn, 1, 1 )
        bitToolsGrid.addWidget( deleteChildBtn, 1, 2 )
        
        # Added the bits widgets to the sub-layout of the main window.
        layout.addWidget( bitPrimitivesHeader )
        layout.addWidget( primitiveFrame )
        layout.addWidget( bitToolsHeader )
        layout.addLayout( bitToolsGrid )
        
    def primitive_buttons( self ):
        sender = self.sender()
        bit_name = 'gl{0}'.format( sender.text() )
        cmds.makeGLBit( objecttype=bit_name )