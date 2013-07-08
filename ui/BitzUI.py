import sys
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import marigold.utility.TransformUtility as TransformUtility

class createBitzUI():
    def __init__( self, winName='createBitzUI' ):
        self.winTitle = 'Bit Editing Tools'
        self.winName = winName
        self.doIt()

    def doIt( self, *args ):
        # Window settings.
        self.winWidth = 60
        self.winHeight = 400
        self.iconWidth = 32
        self.iconHeight = 32
        
        # Clean up old uis before opening a new one.
        try:
            cmds.deleteUI( self.winName )
        except:
            pass
        
        # Setup the form layout.
        self.mainWindow = cmds.window( self.winName, title=self.winTitle, sizeable=False, resizeToFitChildren=False )
        self.form = cmds.formLayout()
                
        self.column = cmds.rowColumnLayout( numberOfColumns=1 )
        cmds.text( label='Bitz Tools', width=self.winWidth, wordWrap=True, align='center', font='boldLabelFont', backgroundColor=(0.15,0.15,0.15) )
        cmds.separator( style='none', height=4 )
        cmds.button( label='match translation', command=lambda v, a1='tran': TransformUtility.matchTransforms(a1) )
        cmds.button( label='match rotation', command=lambda v, a1='rot': TransformUtility.matchTransforms(a1) )
        cmds.button( label='match all', command=lambda v, a1='all': TransformUtility.matchTransforms(a1) )
        cmds.setParent( '..' )#tabFrame

        # Show the window.
        cmds.showWindow( self.winName )    

createBitzUI()