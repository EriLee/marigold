import sys
import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility

class createDeleteAttrUI():
    def __init__( self, winName='createDeleteAttrUI' ):
        self.winTitle = 'Delete Attribute'
        self.winName = winName
        
        self.selList = cmds.ls( selection=True )
        if len(self.selList) == 0:
            sys.stderr.write( 'An object isn\'t selected. Select one and try again.\n' )
            return
        if len(self.selList) > 1:
            sys.stderr.write( 'To many objects ({0}) selected. Select only one object and try again.\n'.format( len(selList) ) )
            return
        else:
            self.objName = NodeUtility.getDagPath( self.selList[0] ).fullPathName() 
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

        self.column = cmds.rowColumnLayout( numberOfRows=2, rowSpacing=[(1,0),(2,10)] )
        
        # ROW 1
        self.updateScrolllist()
        
        # ROW 2
        self.buttonRow = cmds.rowColumnLayout( numberOfColumns=2, columnSpacing=[(1,0),(2,10)], columnWidth=[(1,self.winWidth/2),(2,self.winWidth/2)] )
        cmds.button( label='Delete', command=lambda b: self.deleteAttributes() )
        cmds.button( label='Close', command=lambda b, a1=self.winName: cmds.deleteUI( a1 ) )
        cmds.setParent( '..' )#self.buttonRow
        
        cmds.setParent( '..' )#self.column
        
        # Show the window.
        cmds.showWindow( self.winName )
        
    def updateScrolllist( self ):
        # Build attr list.
        try:
            cmds.textScrollList( self.attrWin, edit=True, removeAll=True )
        except:
            pass
        
        self.attrList = cmds.listAttr( self.selList[0], userDefined=True )
        if self.attrList is not None:
            self.attrWin = cmds.textScrollList( parent=self.column, append=self.attrList, allowMultiSelection=True, width=self.winWidth )
        else:
            self.attrWin = cmds.textScrollList( parent=self.column, allowMultiSelection=True, width=self.winWidth )
        
    def deleteAttributes( self ):
        selAttrs = cmds.textScrollList( self.attrWin, query=True, selectItem=True )
        if len(selAttrs) > 0:
            for a in selAttrs:
                cmds.deleteAttr( '{0}.{1}'.format( self.objName, a ) )
                cmds.textScrollList( self.attrWin, edit=True, removeItem=a )