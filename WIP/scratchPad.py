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
import marigold.utility.FrameUtility as FrameUtility
import marigold.controllers.marigoldControls as marigoldControls
import marigold.skeleton.marigoldJoints as marigoldJoints
import marigold.meta.metaNode as metaNode
# @@@@@
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
class createModuleUI():
    JOINT_SUB_MENUS = { 'BasicJoint':'jointComponentNode' } 
    CONTROLS_SUB_MENUS = { 'BasicJoint':'jointComponentNode' } 
    DEFORMERS_SUB_MENUS = { 'BasicJoint':'jointComponentNode' } 
    CONTRAINTS_SUB_MENUS = { 'BasicJoint':'jointComponentNode' }
    MODULE_SUB_MENUS = { 'BuildComponent':'jointComponentNode' } 
    CHARACTER_SUB_MENUS = { 'BasicJoint':'jointComponentNode' }
    
    SUB_MENUS = { 'Joints':JOINT_SUB_MENUS,
                 'Controls':CONTROLS_SUB_MENUS,
                 'Deformers':DEFORMERS_SUB_MENUS,
                 'Constraints':CONTRAINTS_SUB_MENUS,
                 'Module Item':MODULE_SUB_MENUS,
                 'Character Item':CHARACTER_SUB_MENUS }
    
    def __init__( self, winName='createModuleUI' ):
        self.winTitle = 'Module UI'
        self.winName = winName 
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 400
        self.winHeight = 600
        self.iconWidth = 32
        self.iconHeight = 32
        
        # Window colors
        self.rowColors = [[0.4,0.4,0.4],[0.5,0.5,0.5]]
         
        # Clean up old uis before opening a new one.
        try:
            cmds.deleteUI( self.winName )
        except:
            pass

        # Setup the form layout.
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=True, resizeToFitChildren=True )
        
        # MENU
        self.menuBar = cmds.menuBarLayout()
        self.updateTopMenu( 'Component' )
        cmds.setParent( '..' )#self.menuBar
        
        # MAIN BODY
        self.mainColumn = cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 5) )
        
        # OPTION MENU
        cmds.columnLayout( width=200 )
        self.modeSelect = cmds.optionMenu( width=100, changeCommand=lambda b:self.updateTopMenu(b) )
        cmds.menuItem( label='Component' )
        cmds.menuItem( label='Module' )
        cmds.menuItem( label='Character' )
        cmds.setParent( '..' )
        
        # HIGHLIGHTED
        cmds.separator( style='none', height=4, width=413 )
        self.selName = cmds.text( label=str.upper( 'nothing selected' ), height=20, font='boldLabelFont', backgroundColor=[0.2,0.2,0.2] )
        cmds.separator( style='none', height=10 )
        
        # COMPONENT AREA
        #self.compArea = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.columnLayout( adjustableColumn=True, columnAttach=('both', 0) )
        self.compArea = cmds.frameLayout( labelVisible=False, borderStyle='in' )
        cmds.setParent( '..' )#self.compArea
        cmds.setParent( '..' )
        
        cmds.setParent( '..' )#self.mainColumn
        
        # Selection script job
        self.selJob = cmds.scriptJob( event=[ 'SelectionChanged', self.onSelectionChange ],
                                      parent=self.winName, protected=True )
        
        # Show the window.
        #cmds.showWindow( self.winName )
        allowedAreas = ['right', 'left']
        cmds.dockControl( label=self.winTitle, area='right', floating=True, content=self.mainWindow, allowedArea=allowedAreas )
        
    def buildMenuItems( self, inMenu ):
        menuName = cmds.menu( inMenu, query=True, label=True )
        subMenus = self.SUB_MENUS[ menuName ]
        for subMenu in subMenus:
            className = subMenus[ subMenu ]
            cmds.menuItem( parent=inMenu, label=subMenu, annotation='Creates a {0}'.format( className ),
                           command=lambda b, a1=className:self.addComponentToObject(a1) )
    
    def updateTopMenu( self, inMode ):
        # Delete the existing menu bar's content.
        barChildren = cmds.menuBarLayout( self.menuBar, query=True, menuArray=True )
        if barChildren is not None:
            for child in barChildren:
                cmds.deleteUI( child )
        
        # Now fill the menu layout with the active set.
        if inMode == 'Component':
            self.menuJoints = cmds.menu( parent=self.menuBar, label='Joints' )
            self.buildMenuItems( self.menuJoints )
            
            self.menuControls = cmds.menu( parent=self.menuBar, label='Controls' )
            self.buildMenuItems( self.menuControls )
            
            self.menuDeformers = cmds.menu( parent=self.menuBar, label='Deformers' )
            self.buildMenuItems( self.menuDeformers )
            
            self.menuConstraints = cmds.menu( parent=self.menuBar, label='Constraints' )
            self.buildMenuItems( self.menuConstraints )
        elif inMode == 'Module':
            self.menuTemp = cmds.menu( parent=self.menuBar, label='Module Item' )
            self.buildMenuItems( self.menuTemp )
        elif inMode == 'Character':
            self.menuTemp = cmds.menu( parent=self.menuBar, label='Character Item' )
            self.buildMenuItems( self.menuTemp )
        
    def selectComponentMetaNode( self ):
        # Selects the component meta node.
        pass
    
    def setComponentProperty( self ):
        # Connects this property to the selected object.
        # What is the UI for connecting two properties?
        pass
    
    def deleteComponent( self, inBit, inCompName, inCompNode ):        
        cmds.deleteAttr( '{0}.{1}'.format( inBit, inCompName ) )
        cmds.delete( inCompNode )
        cmds.select( inBit )
        # DISABLED FOR NOW. FOR SOME REASON THIS CRASHES MAYA. SEEMS LIKE IT MIGHT
        # BE A QT ERROR.
        #self.onSelectionChange()
    
    def buildComponent( self, inCompNode ):
        c = str_to_class( inCompNode )
        node = c( inCompNode )
        node.buildNode(node.name())
                
    def testCommand( self, *args ):
        for arg in args:
            print arg
            
    def addComponentToObject( self, inNode ):
        '''
        '''
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) is 1:
            jointComponentNode().createCompNode( inNode )
            # Add the component attribute to the object.
            FrameUtility.addPlug( selList[0], 'jointComponent', 'attributeType', 'message' )
            #cmds.addAttr( inObject, longName='jointComponent', attributeType='message', storable=False )
            nodePlug = '{0}.parentName'.format( inNode )
            objectPlug = '{0}.jointComponent'.format( selList[0] )
            NodeUtility.connectPlugs( objectPlug, nodePlug )
    
    def metaNodeCheck( self, inObj, inComponents ):
        for comName in inComponents:
            metaNode = NodeUtility.getNodeAttrDestination( inObj, comName )
            if metaNode:
                return True
        return False
    
    def updateComponentParameter( self, inCompNode, inPropName, newValue ):
        # Update the parameter.
        node = baseComponentNode( node=inCompNode )
        node.setAttribute( inPropName, newValue, inNodeName=inCompNode )
        
    def updateComponentArea( self, inBit ):
        if inBit is None:
            components = None
        else:
            # Get the components of the selected bit.
            components = FrameUtility.getFrameBitSettings( inBit )
        
        # Clean up the compArea layout prior to adding new children by
        # removing the previously selected bit's information from the UI.
        mainChildren = cmds.frameLayout( self.compArea, query=True, childArray=True )
        
        if mainChildren is not None:
            for child in mainChildren:
                cmds.deleteUI( child )
                    
        # If the newly selected bit has components then update the UI to show them.
        # Check to see if any of the components are connected to a meta node.
        # We do this check so that we don't create a bunch of UI elements
        # unnecessarily.
        if components is not None and self.metaNodeCheck( inBit, components ):
            # Create the scroll layout.
            self.mainScroll = cmds.scrollLayout( parent=self.compArea )
            
            # Loop through each component on the bit.
            for comName in components:
                # Check to see if the component is connected to a meta node.
                metaNode = NodeUtility.getNodeAttrDestination( inBit, comName )
                if metaNode:
                    # It has a meta node.
                    # Get the meta node parameters.                
                    metaParameters = FrameUtility.getFrameBitSettings( metaNode[0] )
                    
                    # Make the component UI elements.
                    self.frameOne = cmds.frameLayout( parent=self.mainScroll, borderStyle='out', label=comName, collapsable=True, width=self.winWidth-10 )
                    
                    cmds.popupMenu()
                    #bit name, component name, meta node name
                    cmds.menuItem( label='Delete Component', command=lambda b, a1=inBit, a2=comName, a3=metaNode[0]:self.deleteComponent(a1, a2, a3) )
                    cmds.menuItem( label='Build Component', command=lambda b, a1=metaNode[0]:self.buildComponent(a1) )
                    
                    self.compColumn = cmds.rowColumnLayout( numberOfColumns=1 )
                    
                    # Loop through the parameters and add them to the component UI.
                    for param in metaParameters:
                        #print isinstance(param, unicode)
                        if not( param == u'parentName' or param == u'classType' ):
                            self.propRow = cmds.rowColumnLayout( numberOfColumns=4, columnWidth=[(1,100),(2,100),(3,40),(4,40)],
                                              columnSpacing=[(1,10),(2,10),(3,10),(4,2)] )
                            cmds.text( label=param, align='left' )
                            cmds.textField( text=metaParameters[param], enterCommand=lambda b, a1=metaNode[0], a2=param:self.updateComponentParameter(a1, a2, b) )
                            cmds.setParent( '..' )#self.propRow
                            
                    cmds.setParent( '..' )#self.compColumn
                    cmds.setParent( '..' )#self.frameOne
                
            cmds.setParent( '..' )#self.mainScroll

    # ==
    # ScriptJob Function.
    # ==
    def onSelectionChange( self ):
        selList = cmds.ls( selection=True, long=True )
        if len( selList ) == 1:
            shortName = selList[0].split( '|' )
            cmds.text( self.selName, edit=True, label=shortName[ len(shortName)-1 ] )
            self.updateComponentArea( selList[0] )
        elif len( selList ) > 1:
            cmds.text( self.selName, edit=True, label=str.upper( 'select only one module bit' ) )
            self.updateComponentArea( None )
        else:
            cmds.text( self.selName, edit=True, label=str.upper( 'nothing selected' ) )
            self.updateComponentArea( None )
            
            
# ==
# UTILITY
# ==
class baseComponentNode( object ):
    '''
    Base class for all meta nodes.
    '''
    nodeType = 'baseComponent'
    
    def __init__( self, node=None ):
        self.node = node
        
    @classmethod
    def createCompNode( cls, inNodeName ):
        '''
        Creates a meta node and adds the required attributes.
        
        @return: The newly created meta node.
        '''
        # Create the node.
        cls.newNode = cmds.createNode( 'network', name=inNodeName )
        #cmds.addAttr( newNode, hidden=False, dataType="string", shortName='classType' )
        #cls.setAttribute( cls(), 'classType', cls.nodeType, inNodeName=newNode )
        
        # Add the required attributes.
        cls.requiredAttributes( cls() )
         
        return cls( cls.newNode )
    
    def name( self ):
        return self.node
        
    @property
    def classType( self ):
        '''
        @return: String. Class type of the meta node.
        '''
        if cmds.attributeQuery( 'classType', node=self.node, exists=True ):
            return cmds.getAttr( '{0}.classType'.format( self.node ) )
        
    @classType.setter
    def classType( self, cons ):
        '''
        Sets the class type of a meta node.
        
        @param cons: List. List of each variable needed to set the attribute.
            cons[0]: String. Name of the component node.
            cons[1]: String. Name of the class type.
            cons[2]: Bool. Lock setting.
        '''
        print len( cons )
        cmds.setAttr( '{0}.classType'.format( cons[0] ), cons[1], type='string', lock=cons[2] )
    
    def requiredAttributes( self ):
        FrameUtility.addPlug( self.newNode, 'parentName', 'attributeType', 'message' )
        #cmds.addAttr( newNode, longName='parentName', attributeType='message', storable=True )
        #self.setAttribute( cls(), 'parentName', self.newNode, inNodeName=self.newNode )
        self.setAttribute( 'parentName', self.newNode, inNodeName=self.newNode )
        
        FrameUtility.addPlug( self.newNode, 'classType', 'dataType', 'string' )
        #cls( self.newNode ).classType = [ self.newNode, self.nodeType, True ]
        self.classType = [ self.newNode, self.nodeType, True ]
        
    def setAttribute( self, inPlugName, inPlugValue, inNodeName=None, inLock=False ):
        print inNodeName, inPlugName
        plug = NodeUtility.getPlug( inNodeName, inPlugName )
        NodeUtility.setPlugValue( plug, inPlugValue )
        cmds.setAttr( '{0}.{1}'.format( inNodeName, inPlugName ), lock=inLock )
        
    @classmethod
    def addComponentToObject( cls, inObjectName ):
        '''
        Add the component to the object and link their plugs.
        '''
        print 'addCompToObj: {0}'.format( inObjectName )
        #print 'addCompToObj: {0}'.format( cls.node )
        
    @classmethod
    def buildNode( cls ):
        '''
        Override this classmethod if a component must build assets.
        '''
        print 'building node stuff!'

class jointComponentNode( baseComponentNode ):
    nodeType = 'jointComponent'
    def __init__( self, node=None, *args, **kwargs ):
        self.node = node
        super( jointComponentNode, self ).__init__( node=self.node )
        
    @classmethod
    def buildNode( cls, nodeName ):
        '''
        Builds a joint.
        
        @param nodeName: String. Name of the node.
        '''
        jointName = cmds.getAttr( '{0}.jointName'.format( nodeName ) )
        transReference = NodeUtility.getNodeAttrSource( nodeName, 'parentName' )
        marigoldJoints.createJoint( jointName, transReference[0], inPrefix='j' )
    
    def requiredAttributes( self ):
        super( jointComponentNode, self ).requiredAttributes()
        FrameUtility.addPlug( self.newNode, 'jointName', 'dataType', 'string' )
    

def str_to_class(field):
    try:
        identifier = getattr(sys.modules[__name__], field)
    except AttributeError:
        raise NameError("%s doesn't exist." % field)
    if isinstance(identifier, (types.ClassType, types.TypeType)):
        return identifier
    raise TypeError("%s is not a class." % field)

#test = jointComponentNode().createCompNode('test')
#selList = cmds.ls( selection=True, long=True )
#selObject = selList[0]
#addComponentToObject( selObject, 'test' )    
    

#print test
#print test.name()
     
#sel = cmds.ls( selection=True )
#node = jointComponentNode( node=sel[0] )
#print node.name()
#node.setAttribute( 'classType', 'bob', inNodeName=node.name() )
#print 'node.classType: {0}'.format( node.classType )
#node.classType = [ node.name(), 'smith' ]


#node.addComponentToObject( 'pCube1' )
#node.setAttribute( 'classType', 'test' )





createModuleUI()




