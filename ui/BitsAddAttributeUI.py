import maya.cmds as cmds

class createAddAttrUI():
    def __init__( self, winName='createAddAttrUI' ):
        self.winTitle = 'Add Attribute'
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

        # Show the window.
        cmds.showWindow( self.winName )
        
createAddAttrUI()