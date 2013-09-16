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
import marigold.utility.NurbsCurveUtility as NurbsCurveUtility


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
    
def getCurveCvs( inCurve ):
    '''
    Retrieves the positions for all CVs on the curve.
    
    @param inCurve: String. Name of the curve from which to retrieve CV positions.
    @return: List of Dicts. Each dict holds the information for one nurbs curve. since
                there could be multiple curves for one object we build a list of each curve.
    '''
    curDag = NodeUtility.getDagPath( inCurve )
    curFn = OpenMaya.MFnNurbsCurve()
    curCvs = OpenMaya.MPointArray()
    
    storedCvs = []
    childShapes = curDag.childCount()
    for child in xrange( childShapes ):
        childObj = curDag.child( child )
        #if childObj.apiType() == OpenMaya.MFn.kNurbsCurve:
        tempCvs = {}
        curFn.setObject( childObj )
        curFn.getCVs( curCvs )
        for cv in xrange( curCvs.length() ):
            tempCvs[cv] = [curCvs[cv].x, curCvs[cv].y, curCvs[cv].z]
        storedCvs.append( tempCvs )

    return storedCvs

def buildCVPointArray( inCVList ):
    '''
    Builds a MPointArray from the passed in CV value list.
    
    @param inCVList: List of Dicts. Each dict holds the information for one nurbs curve. since
                there could be multiple curves for one object we build a list of each curve.
    @return: List of MPointArrays.
    '''
    curList = []
    for cvDict in inCVList:
        curCvs = OpenMaya.MPointArray()
        for index in cvDict:
            curCvs.append( OpenMaya.MPoint( cvDict[index][0], cvDict[index][1], cvDict[index][2] ) )
        curList.append( curCvs )
    return curList

def setCurveCvs( inCurve, inCVArray ):
    '''
    Sets a curves CVs to the values from inCVArray.
    
    @param inCurve: String. Name of curve to update.
    @param inCVArray: List of MPointArrays.
    '''
    curDag = NodeUtility.getDagPath( inCurve )
    curFn = OpenMaya.MFnNurbsCurve()

    childShapes = curDag.childCount()
    for child in xrange( childShapes ):
        childObj = curDag.child( child )
        curFn.setObject( childObj )
        curFn.setCVs( inCVArray[child] )
        curFn.updateCurve()

def addCurveValues( inObj, inPoints ):
    '''
    Add curve CV attributes to an object.
    
    @param inObj: String. Name of object to add curve cv values too.
    @param inPoints: List of curves and their cv points. 
    '''
    print 'inObj: {0}'.format( inObj )
    print 'inPoints: {0}'.format( inPoints )
    # Naming convention: curve + curve# + CV + cv# + axis    
    for index in xrange( len(inPoints) ):
        # Create a compound attribute to hold the curves.
        curveName = 'curve{0}'.format( index )
        curDict = inPoints[index]
        numOfCvs = len( curDict )
        
        cmds.addAttr( inObj, longName=curveName, numberOfChildren=numOfCvs, attributeType='compound', category='nurbCurve' )
        
        for cv in curDict:
            cvPoint = curDict[cv]
            cvName = '{0}CV{1}'.format( curveName, cv )
            print 'cvPoint: {0}'.format( cvPoint )
            print 'cvName: {0}'.format( cvName )
            cmds.addAttr( inObj, longName=cvName, attributeType='float3', parent=curveName )
            cmds.addAttr( inObj, longName='{0}x'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[0] )
            cmds.addAttr( inObj, longName='{0}y'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[1] )
            cmds.addAttr( inObj, longName='{0}z'.format(cvName), attributeType='float', parent=cvName, defaultValue=cvPoint[2] )
            
def writeCurveValues( inObj, inPoints ):
    '''
    Write curve CV values to an object. Object must already have curve CV attributes.
    If it does not then add them with addCurveValues()
    
    @param inObj: String. Name of object to add curve cv values too.
    @param inPoints: List of curves and their cv points. 
    '''
    for index in xrange( len(inPoints) ):
        curveName = 'curve{0}'.format( index )
        curDict = inPoints[index]
        
        for cv in curDict:
            cvPoint = curDict[cv]
            cvName = '{0}CV{1}'.format( curveName, cv )
            attrX = '{0}x'.format(cvName)
            attrY = '{0}y'.format(cvName)
            attrZ = '{0}z'.format(cvName)
            
            cmds.setAttr( '{0}.{1}'.format( inObj, attrX ), cvPoint[0] )
            cmds.setAttr( '{0}.{1}'.format( inObj, attrY ), cvPoint[1] )
            cmds.setAttr( '{0}.{1}'.format( inObj, attrZ ), cvPoint[2] )

def readCurveValues( inObj ):
    '''
    Read stored curve CV values on an object. Object must have curve CV attributes
    created with addCurveValues().
    
    @param inObj: String. Name of object to add curve cv values too.
    '''
    curveAttrs = cmds.listAttr( inObj, string='curve*', category='nurbCurve' )
    
    # [cur, cur, ...]
    # cur[i] = { #:[x,y,z] }
    curList = []
    for attr in curveAttrs:
        plug = NodeUtility.getPlug( inObj, attr )
        plugValue = NodeUtility.getPlugValue( plug )
        
        cvDict = {}
        for index,point in enumerate( plugValue ):
            cvDict[index] = point
        curList.append( cvDict )

    curList
    return curList
                   
#curve = 'circle1'
#cvList = getCurveCvs( curve )
#cvArray = buildCVPointArray( cvList )
#curve2 = 'circle2'
#setCurveCvs( curve2, cvArray )

#curve = 'compound1'
#curve2 = 'CurveControlComponentTempCurve'

#points = getCurveCvs( curve2 )
#addCurveValues( 'CurveControlComponent', points )

#copyPoints = readCurveValues( curve2 )

#cvArray = buildCVPointArray( copyPoints )
#print cvArray
#setCurveCvs( 'compound2', cvArray )
#writeCurveValues( curve, points )

import marigold.components.controls.CurveControl as CurveControl
bob = 'CurveControlComponent1'
thing = CurveControl.CurveControlComponent( bob )
print thing.classType
print thing.curveType