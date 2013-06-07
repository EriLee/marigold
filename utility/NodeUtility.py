import types
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

def getDependNode( inObj ):
    '''
    @param inObj: String.
    @return MObject.
    '''
    selList = OpenMaya.MSelectionList()
    selList.add( inObj )
    mObj = OpenMaya.MObject()
    selList.getDependNode( 0, mObj )
    return mObj

def getDagPath( inObjName ):
    '''
    Takes an object name as a string and returns
    its dag path.
    '''
    # make an empty selection list
    selList = OpenMaya.MSelectionList()
    # add the object to the list
    selList.add( inObjName )
    # create an empty dagpath and fill it with the object's
    mDagPath = OpenMaya.MDagPath()
    selList.getDagPath( 0, mDagPath )
    return mDagPath

def getPlug( inObj, inPlugName ):
    '''
    @param inObj: String.
    @param inPlugName: String.
    @return MPlug.
    '''
    mObj = getDependNode( inObj )
    #print mObj.apiTypeStr()
    depFn = OpenMaya.MFnDependencyNode()
    depFn.setObject( mObj )
    plug = depFn.findPlug( inPlugName )
    return plug#.node()
    
def getPlugValue( inPlug ):
    '''
    @param inPlug: MPlug. The node plug.
    @return: The value of the passed in node plug.
    '''
    pAttribute = inPlug.attribute()
    apiType = pAttribute.apiType()
    
    # Float Groups - rotate, translate, scale
    if apiType in [ OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float ]:
        result = []
        if inPlug.isCompound():
            for c in xrange( inPlug.numChildren() ):
                #print inPlug.child( c ).attribute().apiTypeStr()
                result.append( getPlugValue( inPlug.child( c ) ) )
            return result
    
    # Distance
    elif apiType in [ OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute ]:
        return inPlug.asMDistance().asCentimeters()
    
    # Angle
    elif apiType in [ OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute ]:
        return inPlug.asMAngle().asDegrees()
    
    # Typed - matrix
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        pType = OpenMaya.MFnTypedAttribute( pAttribute ).attrType()
        #print pType
        if pType == OpenMaya.MFnData.kMatrix:
            return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
    
    # Numbers
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()
        #print pType
        if pType == OpenMaya.MFnNumericData.kBoolean:
            return inPlug.asBool()
        elif pType in [ OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong, OpenMaya.MFnNumericData.kByte ]:
            return inPlug.asInt()
        elif pType in [ OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr ]:
            return inPlug.asDouble()
        
    # Enum
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        return inPlug.asInt()
        
def setPlugValue( inPlug, inValue ):
    '''
    @param inPlug: MPlug. The node plug.
    '''
    pAttribute = inPlug.attribute()
    apiType = pAttribute.apiType()
    #print pAttribute.apiTypeStr()
    #print inPlug.info()
    # Float Groups - rotate, translate, scale
    if apiType in [ OpenMaya.MFn.kAttribute3Double, OpenMaya.MFn.kAttribute3Float ]:
        result = []
        if inPlug.isCompound():
            if isinstance( inValue, types.ListType ):
                for c in xrange( inPlug.numChildren() ):
                    result.append( setPlugValue( inPlug.child( c ), inValue[ c ] ) )
                return result
            elif type( inValue ) == OpenMaya.MEulerRotation:
                setPlugValue( inPlug.child( 0 ), inValue.x )
                setPlugValue( inPlug.child( 1 ), inValue.y )
                setPlugValue( inPlug.child( 2 ), inValue.z )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type list.'.format( inPlug.info(), inValue, type( inValue ) ) )
    
    # Distance
    elif apiType in [ OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute ]:
        if isinstance( inValue, types.FloatType ):
            value =  OpenMaya.MDistance( inValue, OpenMaya.MDistance.kCentimeters )
            inPlug.setMDistance( value )
        else:
            OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
    
    # Angle
    elif apiType in [ OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute ]:
        if isinstance( inValue, types.FloatType ):
            value = OpenMaya.MAngle( inValue, OpenMaya.MAngle.kDegrees )
            inPlug.setMAngle( value )
        else:
            OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
            
    # Typed - matrix WE DON'T HANDLE THIS CASE YET!!!!!!!!!
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        pType = OpenMaya.MFnTypedAttribute( pAttribute ).attrType()
        if pType == OpenMaya.MFnData.kMatrix:
            OpenMaya.MGlobal.displayError( 'Matrix setting hasn\'t been setup yet.' )
            return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
    
    # Numbers
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()
        if pType == OpenMaya.MFnNumericData.kBoolean:
            if isinstance( inValue, types.BoolType ):
                inPlug.setBool( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type bool.'.format( inPlug.info(), inValue, type( inValue ) ) )
        elif pType in [ OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong, OpenMaya.MFnNumericData.kByte ]:
            if isinstance( inValue, types.IntType ):
                inPlug.setInt( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type int.'.format( inPlug.info(), inValue, type( inValue ) ) )
        elif pType in [ OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr ]:
            if isinstance( inValue, types.FloatType ):
                inPlug.setDouble( inValue )
            else:
                OpenMaya.MGlobal.displayError( '{0} :: Passed in value ( {1} ) is {2}. Needs to be type float.'.format( inPlug.info(), inValue, type( inValue ) ) )
                
    # Enums
    elif apiType == OpenMaya.MFn.kEnumAttribute:
        inPlug.setInt( inValue )