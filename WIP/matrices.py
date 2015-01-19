import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

import marigold.utility.TransformUtility as TransformUtility

def printMatrix( matrix ):
    util = OpenMaya.MScriptUtil()
    row1 = [ util.getDoubleArrayItem( matrix[0], 0 ),
            util.getDoubleArrayItem( matrix[0], 1 ),
            util.getDoubleArrayItem( matrix[0], 2 ),
            util.getDoubleArrayItem( matrix[0], 3 ) ]
    row2 = [ util.getDoubleArrayItem( matrix[1], 0 ),
            util.getDoubleArrayItem( matrix[1], 1 ),
            util.getDoubleArrayItem( matrix[1], 2 ),
            util.getDoubleArrayItem( matrix[1], 3 ) ]
    row3 = [ util.getDoubleArrayItem( matrix[2], 0 ),
            util.getDoubleArrayItem( matrix[2], 1 ),
            util.getDoubleArrayItem( matrix[2], 2 ),
            util.getDoubleArrayItem( matrix[2], 3 ) ]
    row4 = [ util.getDoubleArrayItem( matrix[3], 0 ),
            util.getDoubleArrayItem( matrix[3], 1 ),
            util.getDoubleArrayItem( matrix[3], 2 ),
            util.getDoubleArrayItem( matrix[3], 3 ) ]
    
    print 'Row 1: {0}'.format( row1 )
    print 'Row 2: {0}'.format( row2 )
    print 'Row 3: {0}'.format( row3 )
    print 'Row 4: {0}'.format( row4 )


## setup double[4][4]
fileTran = [-10.330358779423445, 3.5726726411932432, 7.329368248748317]
fileRotMatrix = [0.9035851814735454, -0.41914955150032557, -0.08858596558426181, 0.0]
fileRotMatrix.extend([0.4263705359882413, 0.8999962921054725, 0.09063575584448433, 0.0])
fileRotMatrix.extend([0.04173710414631, -0.11966757151992792, 0.991936331860066, 0.0])
fileRotMatrix.extend([0.0, 0.0, 0.0, 1.0])

util = OpenMaya.MScriptUtil()

mat = TransformUtility.getMatrix( 'pSphere1', 'worldMatrix' )
rotMat = OpenMaya.MTransformationMatrix( mat ).asRotateMatrix()

## create a zero matrix
matrixZero = OpenMaya.MMatrix()

## set the zero matrix to the file values
rotMatT = OpenMaya.MTransformationMatrix( rotMat )
x = util.asDoublePtr()
y = util.asDoublePtr()
z = util.asDoublePtr()
w = util.asDoublePtr()
rotMatT.getRotationQuaternion(x,y,z,w)
print y
print util.getDouble(y)
quat = OpenMaya.MQuaternion(util.getDouble(x),
                            util.getDouble(y),
                            util.getDouble(z),
                            util.getDouble(w))
print quat
printMatrix( matrixZero )

blarg = OpenMaya.MTransformationMatrix( matrixZero )
blarg.setRotationQuaternion(quat.x,quat.y,quat.z,quat.w)#OpenMaya.MSpace().kTransform)
#OpenMaya.MTransformationMatrix().setRotationQuaternion(blarg,x,y,z,w,OpenMaya.MSpace.kWorld)