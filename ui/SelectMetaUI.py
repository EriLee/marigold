import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.NodeUtility as NodeUtility

class selectMetaUI():
    def __init__( self, winName='selectMetaUI' ):
        self.winTitle = 'Select Meta Node'
        self.winName = winName
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 206
        self.winHeight = 400
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
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=False, resizeToFitChildren=False )
        self.form = cmds.formLayout()
        
        # Layout UI.
        self.column = cmds.rowColumnLayout( numberOfColumns=1, columnWidth=[(1,self.winWidth)] )
        self.fillList()
        cmds.setParent( '..' )#self.column

        # Show the window.
        cmds.showWindow( self.winName )
        
    def fillList( self ):
        metaNodes = NodeUtility.getMetaNodesInScene()
        try:
            cmds.textScrollList( self.scrollList, edit=True, removeAll=True )
        except:
            pass
        
        if metaNodes is not None:
            self.attrWin = cmds.textScrollList( parent=self.column, append=metaNodes,
                                                allowMultiSelection=False, width=self.winWidth,
                                                selectCommand=lambda: self.selectNode() )
        else:
            self.attrWin = cmds.textScrollList( parent=self.column, allowMultiSelection=True, width=self.winWidth )
            
    def selectNode( self ):
        selectedNode = cmds.textScrollList( self.attrWin, query=True, selectItem=True )
        cmds.select( selectedNode[0] )