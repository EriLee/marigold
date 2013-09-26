import traceback
import sys
import os
import types

from PySide import QtCore
from PySide import QtGui
import marigold.ui.widgets.QTWidgets as QTWidgets
import marigold.ui.qtui_resources

from shiboken import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import marigold.utility.TransformUtility as TransformUtility
import marigold.utility.FrameUtility as FrameUtility
import marigold.utility.NodeUtility as NodeUtility

import marigold.components as Components

import marigold.ui.test_widget as test_widget



'''
C:\Python27\Lib\site-packages\PySide\pyside-rcc.exe -py2 E:\maya\scripts\marigold\ui\qtui.qrc > E:\maya\scripts\marigold\ui\qtui_resources.py
pyside-rcc.exe E:\maya\scripts\marigold\ui\qtui.qrc -o E:\maya\scripts\marigold\ui\qtui_resources.py
'''

def maya_main_window():
    '''
    Return the Maya main window widget as a Python object
    '''
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance( long( main_window_ptr ), QtGui.QWidget )

class ExtendedQLabel(QtGui.QLabel):  
    '''
    Usage:
        self.test_btn = ExtendedQLabel( self )
        self.test_btn.setPixmap( QtGui.QPixmap( "E:\maya\scripts\marigold\ui\icons\icon_foot.png" ) )
    '''
  
    def __init(self, parent):  
        QtGui.QLabel.__init__(self, parent)  
  
    def mouseReleaseEvent(self, ev):  
        self.emit(QtCore.SIGNAL('clicked()')) 
        
class RigBuilderUI( QtGui.QDialog ):
    '''
    Builds the UI for the rig building tools.
    '''
    SCRIPT_JOB_NUMBER = -1
    SELECTED_OBJECT_LONGNAME = None
    
    def __init__( self, parent=maya_main_window() ):
        super( RigBuilderUI, self ).__init__( parent )
        
    def create( self ):
        self.setWindowTitle( 'Rig Builder' )
        self.setWindowFlags( QtCore.Qt.Tool )
        
        self.create_actions()
        self.create_main_menu()
        self.create_main_layout()
        self.update_gui()
        #self.create_controls()
        #self.create_layout()
        #self.create_connections()
    
    def closeEvent( self, event ):
        # Clean up the script job stuff prior to closing the dialog.
        if self.SCRIPT_JOB_NUMBER is not -1:
            cmds.scriptJob( kill=self.SCRIPT_JOB_NUMBER, force=True )
        super( RigBuilderUI, self ).closeEvent( event )            
            
    def create_actions( self ):
        self.exit = QtGui.QAction( '&Exit', self, triggered=self.close() )
        
    def create_main_menu( self ):        
        # Mode combo box.
        self.combo_menu = QtGui.QComboBox()
        self.combo_items = [ 'Bits', 'Components', 'Modules', 'Characters' ]
        self.combo_menu.insertItems( 0, self.combo_items )
        self.combo_menu.setFixedWidth( 100 )
        self.combo_menu.activated.connect( self.update_gui )
        
    def create_main_layout( self ):
        # Combo box layout
        combo_layout = QtGui.QHBoxLayout()
        combo_layout.setContentsMargins( 2, 2, 2, 2 )
        combo_layout.setAlignment( QtCore.Qt.AlignLeft )
        combo_layout.addWidget( self.combo_menu )
        #self.combo_spacer = QtGui.QSpacerItem( 100, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding )
        #combo_layout.addItem( self.combo_spacer )
        
        # Dynamic layout.
        self.sub_layout = QtGui.QVBoxLayout()
        self.sub_layout.setAlignment( QtCore.Qt.AlignTop )
        #self.sub_layout.SetMinimumSize( 20, 300 )
        
        
        # Main vertical layout. This is the parent of everything in the GUI.
        self.main_column = QtGui.QVBoxLayout()
        self.main_column.addLayout( combo_layout )
        #self.main_column.setMenuBar( self.menu_bar )
        self.main_column.addLayout( self.sub_layout )
        self.setLayout( self.main_column )
        
    def update_gui( self ):
        '''
        Updates the gui based on the combo box selection.
        '''
        current_combo_index = self.combo_menu.currentIndex()
        current_combo_text = self.combo_menu.currentText()
        
        if self.sub_layout.count() is not 0: self.clear_layout( self.sub_layout )
        
        build_functions = { 0:self.build_bits_gui,
                           1:self.build_components_gui,
                           2:self.build_module_gui,
                           3:self.build_character_gui }
        f = build_functions[ current_combo_index ]
        f()
        
        # Clean up the script job stuff
        if self.SCRIPT_JOB_NUMBER is not -1 and current_combo_index is not 1:
            # Kill the job if we aren't in the component section of the GUI.
            cmds.scriptJob( kill=self.SCRIPT_JOB_NUMBER, force=True )
            self.SCRIPT_JOB_NUMBER = -1
        elif self.SCRIPT_JOB_NUMBER is -1 and current_combo_index == 1:
            # Create the job if we are in the component section and the job doesn't already exist.
            self.SCRIPT_JOB_NUMBER = cmds.scriptJob( event=[ 'SelectionChanged', self.onSelectionChange ], protected=True )
            
    def onSelectionChange( self ):
        '''
        Function called by the scripted event in componentsGUI().
        Updates the componentGUI whenever the user selects a different object.
        '''
        TEST = False
        selList = cmds.ls( selection=1, long=True )
        if not self.selected_lock_active:
            self.clear_layout( self.components_layout )
            if len( selList ) == 1:
                shortName = selList[0].split( '|' )
                selName = shortName[ len(shortName)-1 ]
                self.selected_label.setText( selName )
                self.SELECTED_OBJECT_LONGNAME = selList[0]
                components_class_list = getComponents( self.SELECTED_OBJECT_LONGNAME )
                
                # Add the component node GUI widgets to the component section.
                if components_class_list is not None:
                    for node_name in components_class_list:
                        component = components_class_list[ node_name ]
                        node_name = node_name
                        if TEST:
                            # TEST GUIs
                            self.components_layout.addWidget( componentGui( node_name ) )
                            print 'ADDING NODE GUI FOR: {0}'.format( node_name )
                            print 'comp: {0}'.format( component )
                        else:
                            component_class = Components.str_to_class( component )
                            component_gui = component_class( component ).componentGui( node_name )
                            self.components_layout.addWidget( component_gui )
                        

            elif len( selList ) > 1:
                if not self.selected_lock_active:
                    self.SELECTED_OBJECT_LONGNAME = None
                    self.selected_label.setText( 'select only one module bit' )
            else:
                if not self.selected_lock_active:
                    self.SELECTED_OBJECT_LONGNAME = None
                    self.selected_label.setText( 'nothing selected' )
    
    def lock_selection( self ):
        '''
        Locks the current object selection.
        This allows the user to select other things while keeping the component GUI locked
        on a particular object.
        '''
        if not self.selected_lock_active:
            self.selected_lock_active = True
            self.selected_lock_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/lock_on.png' ) )
        else:
            self.selected_lock_active = False
            self.selected_lock_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/lock_off.png' ) )
            self.onSelectionChange()
            
    def clear_layout( self, layout ):
        '''
        Clears all the sub-objects from the sub_layout.
        '''
        if layout is not None:
            while layout.count():
                item = layout.takeAt( 0 )
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout( item.layout() )
        
    def build_bits_gui( self ):
        '''
        Build the bits GUI sub-layout.
        '''
        # Build bits controls
        # Primitive buttons.        
        self.sphere_btn = QtGui.QToolButton( self )
        self.sphere_btn.setStyleSheet( 'border:0' )
        self.sphere_btn.setAutoRaise( True )
        self.sphere_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_sphere.png' ) )
        self.sphere_btn.setIconSize( QtCore.QSize(32,32) )
        self.sphere_btn.setText( 'Sphere' )
        self.sphere_btn.clicked.connect( self.primitive_buttons )
        
        self.box_btn = QtGui.QToolButton( self )
        self.box_btn.setStyleSheet( 'border:0' )
        self.box_btn.setAutoRaise( True )
        self.box_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_box.png' ) )
        self.box_btn.setIconSize( QtCore.QSize(32,32) )
        self.box_btn.setText( 'Box' )
        self.box_btn.clicked.connect( self.primitive_buttons )
        
        self.cylinder_btn = QtGui.QToolButton( self )
        self.cylinder_btn.setStyleSheet( 'border:0' )
        self.cylinder_btn.setAutoRaise( True )
        self.cylinder_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_cylinder.png' ) )
        self.cylinder_btn.setIconSize( QtCore.QSize(32,32) )
        self.cylinder_btn.setText( 'Cylinder' )
        self.cylinder_btn.clicked.connect( self.primitive_buttons )
        
        self.cone_btn = QtGui.QToolButton( self )
        self.cone_btn.setStyleSheet( 'border:0' )
        self.cone_btn.setAutoRaise( True )
        self.cone_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_cone.png' ) )
        self.cone_btn.setIconSize( QtCore.QSize(32,32) )
        self.cone_btn.setText( 'Cone' )
        self.cone_btn.clicked.connect( self.primitive_buttons )
        
        self.torus_btn = QtGui.QToolButton( self )
        self.torus_btn.setStyleSheet( 'border:0' )
        self.torus_btn.setAutoRaise( True )
        self.torus_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_torus.png' ) )
        self.torus_btn.setIconSize( QtCore.QSize(32,32) )
        self.torus_btn.setText( 'Torus' )
        self.torus_btn.clicked.connect( self.primitive_buttons )
        
        # Bit tools.
        self.match_translation_btn = QtGui.QPushButton( 'Match Translation' )
        self.match_translation_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/icon_match_translation.png' ) )
        self.match_translation_btn.setIconSize( QtCore.QSize(16,16) )
        self.match_translation_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.match_translation_btn.clicked.connect( lambda a='tran':TransformUtility.matchTransforms( a ) )
        
        self.match_rotation_btn = QtGui.QPushButton( 'Match Rotation' )
        self.match_rotation_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/icon_match_rotation.png' ) )
        self.match_rotation_btn.setIconSize( QtCore.QSize(16,16) )
        self.match_rotation_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.match_rotation_btn.clicked.connect( lambda a='rot':TransformUtility.matchTransforms( a ) )
        
        self.match_all_btn = QtGui.QPushButton( 'Match All' )
        self.match_all_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/icon_match_all.png' ) )
        self.match_all_btn.setIconSize( QtCore.QSize(16,16) )
        self.match_all_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.match_all_btn.clicked.connect( lambda a='all':TransformUtility.matchTransforms( a ) )
        
        self.copy_bit_settings_btn = QtGui.QPushButton( 'Copy Bit Settings' )
        self.copy_bit_settings_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_copy_settings.png' ) )
        self.copy_bit_settings_btn.setIconSize( QtCore.QSize(16,16) )
        self.copy_bit_settings_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.copy_bit_settings_btn.clicked.connect( lambda:FrameUtility.copyBitSettings() )
        
        self.add_child_btn = QtGui.QPushButton( 'Add Child' )
        self.add_child_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_add_child.png' ) )
        self.add_child_btn.setIconSize( QtCore.QSize(16,16) )
        self.add_child_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.add_child_btn.clicked.connect( lambda:FrameUtility.setBitChild() )
        
        self.delete_child_btn = QtGui.QPushButton( 'Delete Child' )
        self.delete_child_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_delete_child.png' ) )
        self.delete_child_btn.setIconSize( QtCore.QSize(16,16) )
        self.delete_child_btn.setStyleSheet( 'text-align: left; padding: 4px' )
        self.delete_child_btn.clicked.connect( lambda:FrameUtility.deleteBitChild() )
        
        # Build bits layout.
        # Primitive buttons
        bit_primitives_header = QtGui.QLabel()
        bit_primitives_header.setText( 'Bit Primitives' )
        bit_primitives_header.setAlignment( QtCore.Qt.AlignCenter )
        bit_primitives_header.setStyleSheet( 'font:bold; font-size:14px; background-color:#2B2B30' )
        
        primitive_frame = QtGui.QFrame()
        primitive_frame.setFrameShadow( QtGui.QFrame.Sunken )
        primitive_frame.setFrameShape( QtGui.QFrame.Box )
        primitive_frame.setLineWidth( 1 )
        
        #self.primitive_groupbox.setStyleSheet( 'border:4px; border-style:outset' )
        primitive_layout = QtGui.QHBoxLayout()
        primitive_layout.addWidget( self.sphere_btn )
        primitive_layout.addWidget( self.box_btn )
        primitive_layout.addWidget( self.cylinder_btn )
        primitive_layout.addWidget( self.cone_btn )
        primitive_layout.addWidget( self.torus_btn )
        primitive_frame.setLayout( primitive_layout )
        
        # Bit tools.
        bit_tools_header = QtGui.QLabel()
        bit_tools_header.setText( 'Bit Tools' )
        bit_tools_header.setAlignment( QtCore.Qt.AlignCenter )
        bit_tools_header.setStyleSheet( 'font:bold; font-size:14px; background-color:#2B2B30' )
        
        bit_tools_grid = QtGui.QGridLayout()
        bit_tools_grid.setColumnMinimumWidth( 0, 100 )
        bit_tools_grid.setColumnMinimumWidth( 1, 100 )
        bit_tools_grid.setColumnMinimumWidth( 2, 100 )
        bit_tools_grid.setSpacing( 2 )
        bit_tools_grid.setContentsMargins( 0,0,0,0 )
        # widget, row, col
        bit_tools_grid.addWidget( self.match_translation_btn, 0, 0 )
        bit_tools_grid.addWidget( self.match_rotation_btn, 0, 1 )
        bit_tools_grid.addWidget( self.match_all_btn, 0, 2 )
        bit_tools_grid.addWidget( self.copy_bit_settings_btn, 1, 0 )
        bit_tools_grid.addWidget( self.add_child_btn, 1, 1 )
        bit_tools_grid.addWidget( self.delete_child_btn, 1, 2 )
        
        # Added the bits widgets to the sub-layout of the main window.
        self.sub_layout.addWidget( bit_primitives_header )
        self.sub_layout.addWidget( primitive_frame )
        self.sub_layout.addWidget( bit_tools_header )
        self.sub_layout.addLayout( bit_tools_grid )
    
    def build_components_gui( self ):
        # COMPONENTS MENU BAR
        menu_frame = QtGui.QFrame()
        menu_frame.setMinimumHeight( 20 )
        
        #HACK!!!!!!!!!!!
        basic_joint = QtGui.QAction( '&Basic Joint', self)
        #basic_joint.setShortcut('Ctrl+Q')
        #basic_joint.setStatusTip('Exit application')
        basic_joint.triggered.connect( lambda a='BasicJointComponent':self.addComponentToObject( a ) )
        
        components_menubar = QtGui.QMenuBar( menu_frame )
        joints_menu = components_menubar.addMenu( '&Joints' )
        controls_menu = components_menubar.addMenu( '&Controls' )
        constraints_menu = components_menubar.addMenu( '&Constraints' )
        deformers_menu = components_menubar.addMenu( '&Deformers' )
        joints_menu.addAction( basic_joint )

        # SELECTED HEADER
        self.selected_lock_btn = QtGui.QPushButton()
        self.selected_lock_btn.setIcon( QtGui.QIcon( ':/riggingUI/icons/lock_off.png' ) )
        self.selected_lock_btn.setIconSize( QtCore.QSize(16,16) )
        self.selected_lock_btn.setMaximumWidth( 22 )
        self.selected_lock_btn.setStyleSheet( 'padding: 4px' )
        self.selected_lock_btn.clicked.connect( self.lock_selection )
        self.selected_lock_active = False
        
        self.selected_label = QtGui.QLabel()
        self.selected_label.setText( 'nothing selected' )
        self.selected_label.setAlignment( QtCore.Qt.AlignCenter )
        self.selected_label.setStyleSheet( 'font:bold; font-size:14px; background-color:#2B2B30' )
        
        selected_grid = QtGui.QGridLayout()
        selected_grid.setContentsMargins( 0, 0, 0, 0 )
        selected_grid.setHorizontalSpacing( 0 )
        selected_grid.setColumnMinimumWidth( 0, 22 )
        selected_grid.addWidget( self.selected_lock_btn, 0, 0 )
        selected_grid.addWidget( self.selected_label, 0, 1 )
        
        # SELECTED COMPONENTS LIST/EDITOR        
        # Add the component specific GUI.
        self.components_layout = QtGui.QVBoxLayout()
        self.components_layout.setAlignment( QtCore.Qt.AlignTop )
        scroll_area = QTWidgets.scrollArea( self.components_layout )
        
        # SUB_LAYOUT HOOKUP
        self.sub_layout.addWidget( menu_frame )
        self.sub_layout.addLayout( selected_grid )
        self.sub_layout.addWidget( scroll_area )
        
    def toggle_button_color( self ):
        sender = self.sender()
        if sender.isChecked():
            #sender.setFlat( True )
            #sender.setStyleSheet( 'border:1,background-color:#5e5e5e;')
            sender.setStyleSheet( 'border:1' )
            # Fill area with buttons.
        else:
            #sender.setFlat( False )
            sender.setStyleSheet( 'border:3' )
            #sender.setStyleSheet( 'background-color:#616161' )
        
    def build_module_gui( self ):
        print 'BUILDING MODULE GUI'
        comp_btns_grid = QtGui.QGridLayout()
        
        comp_joints_tog = QtGui.QToolButton()
        comp_joints_tog.setAutoRaise( True )
        comp_joints_tog.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_sphere.png' ) )
        comp_joints_tog.setIconSize( QtCore.QSize(32,32) )
        comp_joints_tog.setText( 'Sphere' )
        comp_joints_tog.setCheckable( True )
        
        comp_controls_tog = QtGui.QToolButton()
        comp_controls_tog.setAutoRaise( True )
        comp_controls_tog.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_sphere.png' ) )
        comp_controls_tog.setIconSize( QtCore.QSize(32,32) )
        comp_controls_tog.setText( 'Sphere' )
        comp_controls_tog.setCheckable( True )
        
        comp_deformers_tog = QtGui.QToolButton()
        comp_deformers_tog.setAutoRaise( True )
        comp_deformers_tog.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_sphere.png' ) )
        comp_deformers_tog.setIconSize( QtCore.QSize(32,32) )
        comp_deformers_tog.setText( 'Sphere' )
        comp_deformers_tog.setCheckable( True )
        
        comp_constraints_tog = QtGui.QToolButton()
        comp_constraints_tog.setAutoRaise( True )
        comp_constraints_tog.setIcon( QtGui.QIcon( ':/riggingUI/icons/bit_sphere.png' ) )
        comp_constraints_tog.setIconSize( QtCore.QSize(32,32) )
        comp_constraints_tog.setText( 'Sphere' )
        comp_constraints_tog.setCheckable( True )
        
        comp_btns_grid.addWidget( comp_joints_tog, 0, 0 )
        comp_btns_grid.addWidget( comp_controls_tog, 0, 1 )
        comp_btns_grid.addWidget( comp_deformers_tog, 0, 2 )
        comp_btns_grid.addWidget( comp_constraints_tog, 0, 3 )
    
    def build_character_gui( self ):
        print 'BUILD CHARACTER GUI'           
            
    def primitive_buttons( self ):
        sender = self.sender()
        bit_name = 'gl{0}'.format( sender.text() )
        cmds.makeGLBit( objecttype=bit_name )

    def addComponentToObject( self, inClassType ):
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) is 1:
            prevSel = selList[0]
            component_class = Components.str_to_class( inClassType )
            newNode = component_class.createCompNode( inClassType )
            
            # Add the component attribute to the object.
            FrameUtility.addPlug( selList[0], newNode.name(), 'attributeType', 'message' )
            nodePlug = '{0}.parentName'.format( newNode.name() )
            objectPlug = '{0}.{1}'.format( selList[0], newNode.name() )
            NodeUtility.connectPlugs( objectPlug, nodePlug )
            cmds.select( prevSel )

'''
THINGS TO MOVE
'''
def metaNodeCheck( inObj, inComponents ):
    '''
    Checks if the component plug of an object has a meta node connected.
    @param inObj: String. Name of the selected object.
    @param inComponents: List of connected components to the selected object.
    '''
    for comName in inComponents:
        metaNode = NodeUtility.getNodeAttrDestination( inObj, comName )
        if metaNode:
            return True
    return False

def getComponents( inObj ):
    '''
    Creates the components GUI.
    '''
    if inObj is not None:
        components_list = FrameUtility.getFrameBitSettings( inObj )
    else:
        components_list = None
    
    # If the newly selected bit has components then update the UI to show them.
    # Check to see if any of the components are connected to a meta node.
    # We do this check so that we don't create a bunch of UI elements
    # unnecessarily.
    if components_list is not None and metaNodeCheck( inObj, components_list ):            
        # Loop through each component on the bit.
        components_class_list = {}
        for node_name in components_list:
            # Check to see if the component is connected to a meta node.
            metaNode = NodeUtility.getNodeAttrDestination( inObj, node_name )
            if metaNode:
                # It has a meta node.
                # Get the meta node properties. This returns a dict.
                meta_properties = FrameUtility.getFrameBitSettings( metaNode[0] )
                component_class = meta_properties[ 'classType' ]
                # test hack!!!
                components_class_list[ node_name ] = component_class
        return components_class_list
    else:
        return None

def componentGui( inNodeName ):        
    def on_context_menu( point ):
        popMenu = QtGui.QMenu()
        popMenu.addAction( 'actionEdit' )
        popMenu.addAction( 'actionDelete' )
        popMenu.addSeparator()
        popMenu.addAction( 'actionAdd' )
        popMenu.exec_( componentLabel.mapToGlobal( point ) )
    
    mainWidget = QtGui.QWidget()
        
    verticalLayout = QtGui.QVBoxLayout( mainWidget )
    verticalLayout.setContentsMargins( 0,0,0,0 )
    verticalLayout.setSpacing( 0 )
    verticalLayout.setAlignment( QtCore.Qt.AlignTop )
    
    # Label for component
    componentLabel = QTWidgets.basicLabel( inNodeName, 'bold', 10, 'black', 448094 )    
    componentLabel.setContextMenuPolicy( QtCore.Qt.CustomContextMenu )
    componentLabel.customContextMenuRequested.connect( on_context_menu )
    
    propertyFrame = QTWidgets.basicFrame()
    propertyFrame.setMinimumHeight( 40 )
    propertyFrame.setMaximumHeight( 40 )
    
    # Add string edit property
    plug = NodeUtility.getPlug( inNodeName, 'jointName' )
    plugValue = NodeUtility.getPlugValue( plug )
    QTWidgets.stringProperty( propertyFrame, 'Joint Name', plugValue )
    
    # Add everything to the vertical layout.
    verticalLayout.addWidget( componentLabel )
    verticalLayout.addWidget( propertyFrame )
    
    #print 'test2: {0}'.format( prop.takeAt(0).widget() )
    #print propertyFrame.count()
    #print propertyFrame.findChild( QtGui.QLineEdit )
    #for item in xrange( propertyFrame.count() ):
    #    print propertyFrame.itemAt( item ).widget()
    
    return mainWidget
        
'''
    RUN THE WINDOW
'''
#THIS DOESN'T WORK THROUGH ECLIPSE. SO WE WORK AROUND IT WHEN SENDING TO MAYA
#FROM THE EDITOR.
#if __name__ == "__main__":
    
# Development workaround for PySide winEvent error (Maya 2014)
# Make sure the UI is deleted before recreating
try:
    test_ui.deleteLater()
except:
    pass

# Create minimal UI object
test_ui = RigBuilderUI()

# Delete the UI if errors occur to avoid causing winEvent
# and event errors (in Maya 2014)
try:
    test_ui.create()
    test_ui.show()
except:
    test_ui.deleteLater()
    traceback.print_exc()