## getMatrix ##

Get an object's matrix.

> @param **inNode**: _String_. Name of object.

> @param **inMatrixType**: _String_. "matrix", "inverseMatrix", "worldMatrix", "worldInverseMatrix", "parentMatrix", "parentInverseMatrix", "xformMatrix"

> @return: _MMatrix_. Matrix in space requested.

## getMatrixTranslation ##

Get the position from the passed in object matrix.

> @param **inObjMatrix**: _MMatrix_.

> @return: World space translation from MMatrix.

## getMatrixRotation ##

Takes an object's matrix and a rotation type and return the rotation.

> @param **inObjMatrix**: _MMatrix_.

> @param **inType**: _String_. Type of rotation, 'euler' or 'quat'

> @return: Rotation from MMatrix in the desired format.

## getMatrixScale ##

Get the position from the passed in object matrix.

> @param **inObjMatrix**: _MMatrix_.

> @return: _MVector_. Scale from MMatrix.

## matchTransforms ##

Matches the transform of one object to another. Must be two objects selected.

> @param **inType**: _String_. Type of matching to perform. 'tran', 'rot', or 'all'

## matchObjectTransforms ##

Matches the child's translation and rotation to the source object.

> @param **src**: _String_. Name of the source transform object.

> @param **cld**: _String_. Name of the child object.

## mirrorObjectPrompt ##

UI prompt used to mirror an object.

## mirrorObject ##

Mirrors the selected object.

> @param **inSourceObj**: _String_. Name of the object to be mirrored.

> @param **inTargetObj**: _String_. Name of the object receive the mirroring.

> @param **inMirrorAxis**: _Int_. 0 is X, 1 = Y, and 2 = Z.

## mirrorModule ##

Mirrors the selected rigging module.