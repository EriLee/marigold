'''
TODO:
1. Optimized ogl objects
2. Mapper UI
    a. main interface
        1. add module to joint - mapping
        2. sub-menu custom to module
            a. fill out required details for module
3. Mapped UI
    a. build rig
        1. store bind pose
    b. build module rigging
        1. must have rig in bind pose
    c. delete rigging
    d. delete module rigging
'''
def buildClavicle():
    '''
    create spacer for all controls
        match position to joint
        match rotation to joint
        set name
    create main clavicle control
        custom opengl control
            set name
            set attributes
                length is distance between clavicle joint and shoulder joint
                width and height are half of the length
        parent it to the spacer
        offset pivot based on left or right side
        position control
        set color
        clean up channel
            lock and remove translation, scale and visibility
        add animatable attributes to character set
        add visible controls to rig layer
        add non-visible/protected controls to don't touch group
            hide them
    if the clavicle's parent exists
        parent the entire clavicle rig into it's parent
    elif the character base exists
        parent the entire clavicle rig into the rig group
    '''
    pass


'''
prompt user selection
'''
import maya.cmds as cmds

def test( *args ):
    for i,n in enumerate( args ):
        print '{0}, {1}'.format( i, n )
        
def test2():
    ctx = cmds.scriptCtx( title='Select Something',
                            totalSelectionSets=1,
                            fcs="select -r $Selection1; python(\"test('\"+$Selection1[0]+\"','\"+$Selection1[1]+\"')\");",
                            cumulativeLists=False,
                            expandSelectionList=True,
                            setNoSelectionPrompt='Select Object',
                            setSelectionPrompt='Never used',
                            setDoneSelectionPrompt='Never used because setAutoComplete is set',
                            setAutoToggleSelection=True,
                            setSelectionCount=2,
                            setAutoComplete=True)
    
    cmds.setToolTo(ctx)
    
test2()

'''
get plug values
'''
def blah():
    print 'blah'
    
def asBool( inPlug ):
    return inPlug.asBool()

def asFloat( inPlug ):
    return inPlug.asFloat()
    
dataTypes = { 0 : blah, 1 : asBool, 13:asFloat, }

plug = getPlug( 'pCone1', 'matrix' )
if plug.isCompound():
    for i in xrange( plug.numChildren() ):
        pName = plug.child( i ).name()
        pAttribute = plug.child( i ).attribute()
        if pAttribute.hasFn( OpenMaya.MFn.kNumericAttribute ):
            print plug.child( i ).asFloat()
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()
        print pType
        print dataTypes[pType]( plug.child( i ) )
else:
    pAttribute = plug.attribute()
    print pAttribute
    print plug.asDouble()
    if pAttribute.hasFn( OpenMaya.MFn.kMatrixAttribute ):
        print 'matrix'
#======      

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

def getPlug( inObj, inPlugName ):
    '''
    @param inObj: Depend Node.
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
    print 'PLUG: {0}'.format( inPlug.name() )
    pAttribute = inPlug.attribute()
    print 'ATTR: {0}, {1}'.format( pAttribute.apiTypeStr(), pAttribute.apiType() )
    apiType = pAttribute.apiType()
    
    # Float Groups - rotate, translate, scale
    if apiType == OpenMaya.MFn.kAttribute3Double:
        print 'Float Group'
        result = []
        if plug.isCompound():
            print 'Compound!'
            for c in xrange( plug.numChildren() ):
                print plug.child( c ).attribute().apiTypeStr()
                result.append( getPlugValue( plug.child( c ) ) )
            return result
    
    # Distance
    elif apiType in [ OpenMaya.MFn.kDoubleLinearAttribute, OpenMaya.MFn.kFloatLinearAttribute ]:
        print 'Distance'
        return inPlug.asMDistance().asCentimeters()
    
    # Angle
    elif apiType in [ OpenMaya.MFn.kDoubleAngleAttribute, OpenMaya.MFn.kFloatAngleAttribute ]:
        print 'Angle'
        return inPlug.asMAngle().asDegrees()
    
    # Typed - matrix
    elif apiType == OpenMaya.MFn.kTypedAttribute:
        print 'Typed'
        pType = OpenMaya.MFnTypedAttribute( pAttribute ).attrType()
        print pType
        if pType == OpenMaya.MFnData.kMatrix:
            return OpenMaya.MFnMatrixData( inPlug.asMObject() ).matrix()
    
    # Numbers
    elif apiType == OpenMaya.MFn.kNumericAttribute:
        pType = OpenMaya.MFnNumericAttribute( pAttribute ).unitType()
        print pType
        if pType == OpenMaya.MFnNumericData.kBoolean:
            return inPlug.asBool()
        elif pType in [ OpenMaya.MFnNumericData.kShort, OpenMaya.MFnNumericData.kInt, OpenMaya.MFnNumericData.kLong, OpenMaya.MFnNumericData.kByte ]:
            return inPlug.asInt()
        elif pType in [ OpenMaya.MFnNumericData.kFloat, OpenMaya.MFnNumericData.kDouble, OpenMaya.MFnNumericData.kAddr ]:
            return inPlug.asDouble()
            
plug = getPlug( 'pCone1', 'matrix' )
print 'INFO: {0}'.format( plug.info() )
pValue = getPlugValue( plug )
print 'RESULT: {0}'.format( pValue )
print OpenMaya.MTransformationMatrix( pValue ).getTranslation( OpenMaya.MSpace.kWorld ).x
    
