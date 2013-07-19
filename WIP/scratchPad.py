# BUILD ARM FROM SKELETON
import os
import math
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

'''
- CREATE RIG
    - CREATE BASIC ROOT
    - CONNECT MODULES TO ROOT
    - BUILD
        -SKELETON
            -CONSTRAIN SKELETON TO SHADOW
        - FKIK NODE
- FKIK NODE
- SPACE SWITCH NODE
- CLEAN UP LIBRARY. OPTIMISE IMPORTS
'''
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