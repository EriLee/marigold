'''
Plug-in: Multi-Point Blend Node
Author: Austin Baker
Date Started: June 2013

*ABOUT*
Creates a multi-point blend node. This node takes an XY input in the ranges of -1 ~ +1.
Each row can have 1~N number of blend points, and there can be 1~N number of rows.

*DEPENDENCY*
Marigold.utility.NodeUtility

*SAMPLE USAGE*
import maya.cmds as cmds
cmds.createNode( 'multiAxisBlend' )
    
*TODO*
    Add individual blend point influence scale.
'''
import sys, math
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import marigold.utility.NodeUtility as NodeUtility

class MultiAxisBlendNode( OpenMayaMPx.MPxNode ):
    
    nodeName = 'multiAxisBlend'
    nodeID = OpenMaya.MTypeId( 0x1234B )
    
    inputX = OpenMaya.MObject()
    inputY = OpenMaya.MObject()
    radiusScale = OpenMaya.MObject()
    outBlendWeight = OpenMaya.MObject()
    outRow = OpenMaya.MObject()
    
    @classmethod
    def nodeCreator( cls ):
        return OpenMayaMPx.asMPxPtr( MultiAxisBlendNode() )
    
    @classmethod
    def nodeInitializer( cls ):
        # Declare MFNs
        nAttr = OpenMaya.MFnNumericAttribute()
        cAttr = OpenMaya.MFnCompoundAttribute()
        
        # INPUT.
        MultiAxisBlendNode.inputX = nAttr.create( 'inputX', 'inputX', OpenMaya.MFnNumericData.kFloat )
        nAttr.setMax( 1.0 )
        nAttr.setMin( -1.0 )
        nAttr.setStorable( True )
        nAttr.setWritable( True )
        nAttr.setChannelBox( False )
        MultiAxisBlendNode.addAttribute( MultiAxisBlendNode.inputX )
        
        MultiAxisBlendNode.inputY = nAttr.create( 'inputY', 'inputY', OpenMaya.MFnNumericData.kFloat )
        nAttr.setMax( 1.0 )
        nAttr.setMin( -1.0 )
        nAttr.setStorable( True )
        nAttr.setWritable( True )
        nAttr.setChannelBox( False )
        MultiAxisBlendNode.addAttribute( MultiAxisBlendNode.inputY )
        
        MultiAxisBlendNode.radiusScale = nAttr.create( 'radiusScale', 'radiusScale', OpenMaya.MFnNumericData.kFloat )
        nAttr.setStorable( True )
        nAttr.setWritable( True )
        nAttr.setChannelBox( False )
        MultiAxisBlendNode.addAttribute( MultiAxisBlendNode.radiusScale )
        
        # OUTPUT.
        MultiAxisBlendNode.outBlendWeight = nAttr.create( 'outBlendWeight', 'obw', OpenMaya.MFnNumericData.kFloat, 0.0 )
        nAttr.setMax( 1.0 )
        nAttr.setMin( 0.0 )
        nAttr.setReadable( True )
        nAttr.setArray( True )
        nAttr.setUsesArrayDataBuilder( True )
        MultiAxisBlendNode.addAttribute( MultiAxisBlendNode.outBlendWeight )
        
        MultiAxisBlendNode.outRow = cAttr.create( 'outRow', 'or' )
        cAttr.setArray( True )
        cAttr.setReadable( True )
        cAttr.addChild( MultiAxisBlendNode.outBlendWeight )
        cAttr.setUsesArrayDataBuilder( True )
        MultiAxisBlendNode.addAttribute( MultiAxisBlendNode.outRow )
        
        # AFFECTS.
        MultiAxisBlendNode.attributeAffects( MultiAxisBlendNode.inputX, MultiAxisBlendNode.outRow )
        MultiAxisBlendNode.attributeAffects( MultiAxisBlendNode.inputY, MultiAxisBlendNode.outRow )
        MultiAxisBlendNode.attributeAffects( MultiAxisBlendNode.radiusScale, MultiAxisBlendNode.outRow )
    
    def compute( self, plug, dataBlock ):
        thisNode = self.thisMObject()
        socketNode = OpenMaya.MFnDependencyNode( thisNode )        
        
        xValue = OpenMaya.MPlug( thisNode, socketNode.attribute( 'inputX' ) ).asFloat()
        yValue = OpenMaya.MPlug( thisNode, socketNode.attribute( 'inputY' ) ).asFloat()
        rScaleValue = OpenMaya.MPlug( thisNode, socketNode.attribute( 'radiusScale' ) ).asFloat()
        outRowPlug = OpenMaya.MPlug( thisNode, socketNode.attribute( 'outRow' ) )
        outWeightPlug = OpenMaya.MPlug( thisNode, socketNode.attribute( 'outBlendWeight' ) )
        
        # Out blends.
        outRowAttr = outRowPlug.attribute()
        
        # For each row get the number of blend points.
        numRows = outRowPlug.numElements()
        gridLength = 2.0 # Both inputs range from -1 to 1. To make things easier we map this to 0.0 to 2.0
        rowPoints = []
        
        # Subtract 1 since Maya automatically adds an empty element at the end of the compound plug.
        for row in range( numRows ):
            rowPoints.append( [] )
            outWeightPlug.selectAncestorLogicalIndex( row, outRowAttr )
            
            # Get the radius for all points in the row.
            numPoints = outWeightPlug.numElements()
            if numPoints > 1:
                tempXLoc = 0.0
                
                # The first plug will be at zero X.
                radius = ( gridLength / numPoints ) + rScaleValue
                xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
                yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
                inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
                if inputDistance <= radius:
                    perc = ( inputDistance / radius ) * 100
                    rowPoints[row].append( ( 100 - perc ) / 100 )
                else:
                    rowPoints[row].append( 0.0 )
                
                # Loop to get the remaining plug X locations.
                for point in xrange( numPoints - 1 ):
                    xLoc = gridLength / ( numPoints - 1 )
                    tempXLoc = tempXLoc + xLoc
                    xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
                    yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
                    inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
                    if inputDistance <= radius:
                        perc = ( inputDistance / radius ) * 100
                        rowPoints[row].append( ( 100 - perc ) / 100 )
                    else:
                        rowPoints[row].append( 0.0 )
            else:
                # Handle single point rows.
                radius = 1.0 + rScaleValue # Maximum for a single point in a row.
                tempXLoc = 1.0
                xLoc = scaleRange( tempXLoc, [0.0, 2.0], [-1.0, +1.0] )
                yLoc = scaleRange( row, [ 0.0, 2.0 ], [ +1.0, -1.0 ] )
                inputDistance = math.sqrt( ( xLoc - xValue )**2 + ( yLoc - yValue )**2 )
                if inputDistance <= radius:
                    perc = ( inputDistance / radius ) * 100
                    rowPoints[row].append( ( 100 - perc ) / 100 )
                else:
                    rowPoints[row].append( 0.0 )
        
            for a in range( outWeightPlug.numElements() ):
                outWeightPlug[a].setFloat( rowPoints[row][a] )
        '''
        for r in range( outRowPlug.numElements() - 1 ):
            outWeightPlug.selectAncestorLogicalIndex( r, outRowAttr )
            outHandle = outWeightPlug.constructHandle( dataBlock )
            arrayHandle = OpenMaya.MArrayDataHandle( outHandle )
            arrayBuilder = arrayHandle.builder()
            for a in range( outWeightPlug.numElements() ):
                handle = arrayBuilder.addElement( a )
                handle.setFloat( rowPoints[r][a] )
            arrayHandle.set( arrayBuilder )
            outWeightPlug.setMDataHandle( outHandle )
            outWeightPlug.destructHandle( outHandle )
        '''

def scaleRange( inValue, inOrigRange, inNewRange ):
    return ( ( inValue - inOrigRange[0] ) / ( inOrigRange[1] - inOrigRange[0] ) ) * ( inNewRange[1] - inNewRange[0] ) + inNewRange[0]

  
def initializePlugin( obj ):
    ''' Initialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj, 'Austin Baker', '1.0', 'Any' )
    # Aim constraint node.
    try:
        plugin.registerNode( MultiAxisBlendNode.nodeName, MultiAxisBlendNode.nodeID, MultiAxisBlendNode.nodeCreator, MultiAxisBlendNode.nodeInitializer  )
    except:
        sys.stderr.write( 'Failed to register node: {0}'.format( MultiAxisBlendNode.nodeName ) )
        raise

def uninitializePlugin( obj ):
    ''' Uninitialize the plug-in. '''
    plugin = OpenMayaMPx.MFnPlugin( obj )
    # Aim constraint node.
    try:
        plugin.deregisterNode( MultiAxisBlendNode.nodeID )
    except:
        sys.stderr.write( 'Failed to deregister node: {0}'.format( MultiAxisBlendNode.nodeName ) )
        raise