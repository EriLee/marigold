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
selList = cmds.ls( selection=True, long=True )
depFn = OpenMaya.MFnDependencyNode()

if len(selList) == 2:
    # First object is target.
    targetShape = cmds.listRelatives( selList[0], shapes=True, fullPath=True )[0]
    targetShapeMObj = NodeUtility.getDependNode( targetShape )
    depFn.setObject( targetShapeMObj )
    targetShapeType = depFn.typeName()
    
    # Second object is source.
    sourceShape = cmds.listRelatives( selList[1], shapes=True, fullPath=True )[0]
    sourceShapeMObj = NodeUtility.getDependNode( sourceShape )
    depFn.setObject( sourceShapeMObj )
    sourceShapeType = depFn.typeName()
    
    if targetShapeType == sourceShapeType:        
        # The types match. Do the copy of attribute settings.
        for attr in cmds.listAttr( sourceShape, multi=True, keyable=True ):
            # Get the plugs.
            sourcePlug = NodeUtility.getPlug( sourceShape, attr )
            targetPlug = NodeUtility.getPlug( targetShape, attr )
            
            # Get the source plug value.
            sourcePlugValue = NodeUtility.getPlugValue( sourcePlug )
            
            # Set the target's plug value.
            NodeUtility.setPlugValue( targetPlug, sourcePlugValue )
    else:
        raise ValueError( '{0} and {1} do not match.'.format( selList[0], selList[1] ) )
                