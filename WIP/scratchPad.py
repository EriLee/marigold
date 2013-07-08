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

'''
- MAKE UI FOR CREATING META NODES
    - BOTTOM HALF OF UI FOR FILLING IN NODE ATTRIBUTES
    - SELECT THE NODE AND HIT REFRESH BUTTON
X- MAKE FRAME MODULE META NODE
    X- MAKE FKIKARM NODE
    - HOOK UP NODE
X- CREATE RIG
    X- READ FRAME MODULE META NODE
    X- CALL THE CORRECT MODULE SCRIPT
        - BUILD
            -SKELETON
                -CONSTRAIN SKELETON TO SHADOW
            X-SHADOW
            X- FK RIG
            X- IK RIG
            - FKIK NODE
- FKIK NODE
- SPACE SWITCH NODE
X- SAVE FRAME MODULE XML
X- LOAD FRAME MODULE XML
'''
# @@@@@
#FrameUtility.createFrameModuleXML()
def buildFrameModule( inDir=None, inXMLFile=False ):
    debug = False
    
    # Imports
    import marigold.frames.bits.bits as Bits
    
    # Get the XML settings for the frame module.
    dirPath = XMLUtility.getPresetPath( XMLUtility.FRAME_PRESETS_PATH+inDir )
    fullPath = dirPath+'/'+inXMLFile+'.xml'
    xmlDict = FrameUtility.readFrameModuleXML( fullPath )
    
    # Get the metanode.
    metanodeData = xmlDict['metanode']
    meta = metanodeData['name']
    metaPlugs = metanodeData['plugs']
    
    # Build the node.
    buildModule = importModule( 'marigold.frames.modules.'+inDir+'.'+inXMLFile )
    metanode = buildModule.MetaFrameFKIKArm()
    # Need the node created, which points to the custom class.
    # Till I figure a way to get the name through the API I'm going to use
    # the fact that the node is selected after creation.
    metanode = cmds.ls( selection=True )[0]  
    
    if not debug:
        # Get the bits.
        bits = xmlDict['bits']
        
        # Make a group for the module.
        for bit in bits:
            if bit['name'] == 'frame_root':
                for plug in bit['plugs']: 
                    if plug['name'] == 'prefix':
                        modulePrefix = plug['value']
        moduleGroup = '|'+cmds.group( em=True, name=modulePrefix+'_fkikArm' )
    
        # Make each bit.
        tick = 0
        while tick < len(bits):
            bitName = bits[0]['name']
            bitParent = moduleGroup+bits[0]['parent']
            bitPlugs = bits[0]['plugs']
            for plug in bitPlugs:
                if plug['name'] == 'bitType':
                    bitType = plug['value']
            
            # Make the bit.
            if bitParent == 'None' or cmds.objExists( bitParent ):
                newBit = Bits.frameBits( bitType, bitName )
                cmds.parent( newBit, bitParent )
                
                # From this point we use the long name for the bit. This avoids any
                # name clashes.
                fullBitName = bitParent+'|'+bitName 
                
                # Setup plugs.
                for plug in bitPlugs:
                    print plug
                    if not NodeUtility.attributeCheck( fullBitName, plug['name'] ):
                        FrameUtility.addPlug( fullBitName, plug['name'], plug['attrType'], plug['attrDataType'] )
                        if plug['value'] is not None:
                            FrameUtility.setPlug( fullBitName, plug['name'], plug['value'], inAttrDataType=plug['attrDataType'] )
                    else:          
                        # Setup position and rotation.
                        FrameUtility.setPlug( fullBitName, plug['name'], plug['value'] )
                        
                    # Connect plug to meta node.
                    for mplug in metaPlugs: 
                        if bitName+'.'+plug['name'] == mplug['value']:
                            inSourcePlug = fullBitName+'.'+plug['name']
                            inDestinationPlug = metanode+'.'+mplug['name']
                            NodeUtility.connectPlugs( inSourcePlug, inDestinationPlug )
                
                bits.remove( bits[0] )
            else:
                tick = tick+1
                pass
        
buildFrameModule( inDir='arms', inXMLFile='fkikArm' )
# Create meta frame node.

# Hook up plugs on the node.


    