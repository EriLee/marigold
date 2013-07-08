'''
Placeholder for bits functions.

This file contains functions used to create the basic bits required to make a 
frame module.

TODO:
    Convert these bits into opengl objects.
    Store their shape attributes in the frame module xml.
'''
import maya.cmds as cmds
import marigold.utility.NodeUtility as NodeUtility

def frameBits( inSubType=None, inBitName=None ):
    buildFunctions = { 'rootX' : rootX,
                      'rootY' : rootY,
                      'rootZ' : rootZ,
                      'ballX' : ballX,
                      'ballY' : ballY,
                      'ballZ' : ballZ,
                      'hingeX' : hingeX,
                      'hingeY' : hingeY,
                      'hingeZ' : hingeZ,
                      'triangleZ' : triangleZ }
    f = buildFunctions[ inSubType ]
    return f( inBitName )
    
def rootX( inBitName ):
    # Bit is a list. [name, meshType]
    bit = cmds.polyTorus( axis=[1,0,0],
                            radius=6,
                            sectionRadius=0.2,
                            twist=0,
                            subdivisionsX=8,
                            subdivisionsY=3,
                            name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]

def rootY( inBitName ):
    bit = cmds.polyTorus( axis=[0,1,0],
                            radius=6,
                            sectionRadius=0.2,
                            twist=0,
                            subdivisionsX=8,
                            subdivisionsY=3,
                            name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]

def rootZ( inBitName ):
    bit = cmds.polyTorus( axis=[0,0,1],
                            radius=6,
                            sectionRadius=0.2,
                            twist=0,
                            subdivisionsX=8,
                            subdivisionsY=3,
                            name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]
    
def ballX( inBitName ):
    bit = cmds.polySphere( axis=[1,0,0],
                             radius=4,
                             subdivisionsX=8,
                             subdivisionsY=4,
                             name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]
    
def ballY( inBitName ):
    bit = cmds.polySphere( axis=[0,1,0],
                             radius=4,
                             subdivisionsX=8,
                             subdivisionsY=4,
                             name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]
    
def ballZ( inBitName ):
    bit = cmds.polySphere( axis=[0,0,1],
                             radius=4,
                             subdivisionsX=8,
                             subdivisionsY=4,
                             name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]

def hingeX( inBitName ):
    bit = cmds.polyCylinder( axis=[1,0,0],
                               radius=1,
                               height=10,
                               subdivisionsX=6,
                               subdivisionsY=1,
                               subdivisionsZ=1,
                               name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]
    
def hingeY( inBitName ):
    bit = cmds.polyCylinder( axis=[0,1,0],
                               radius=1,
                               height=10,
                               subdivisionsX=6,
                               subdivisionsY=1,
                               subdivisionsZ=1,
                               name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]
    
def hingeZ( inBitName ):
    bit = cmds.polyCylinder( axis=[0,0,1],
                               radius=1,
                               height=10,
                               subdivisionsX=6,
                               subdivisionsY=1,
                               subdivisionsZ=1,
                               name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]

def triangleZ( inBitName ):
    bit = cmds.polyCylinder( axis=[0,0,1],
                               radius=1,
                               height=10,
                               subdivisionsX=6,
                               subdivisionsY=1,
                               subdivisionsZ=1,
                               name=inBitName )
    # Return the name of the newly created bit.
    return bit[0]