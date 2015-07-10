## createCurve ##

Creates a nurbs curve.

> @param **inName**: _String_. Name of the curve to be created.

> @param **inPoints**: _List of lists_. Points of the control vertices of the curve.

> @param **inDegree**: _Int_. Degree of the curve. 1, 2, 3, 5, 7

> @param **inForm**: _Int_. Open or closed curve. 1 for closed, 2 for open.

> @param **inOffset**: _List_. Offset for each axis of the curve.

> @return: _MObject_. Nurbs curve.

## createCurveCircle ##

Creates a closed nurbs curve circle.

> @param **inName**: _String_. Name of curve circle.

> @param **inNormal**: _List_. Direction the curve faces.

> @param **inRadius**: _Int_. Radius of the circle.

> @return. _MObject_. Curve circle.

## createCompoundCurve ##

Merges all the controls into one transform node.

> @param **inCurves**: _List of Strings_. Names of curves to combine under one transform node. The first curve in the list is considered the parent of all the others.

> @return: _MObject_. Compound curve transform node.

## getCurveCvs ##

Retrieves the positions for all CVs on the curve.

> @param **inCurve**: _String_. Name of the curve from which to retrieve CV positions.

> @return: _List of Dicts_. Each dict holds the information for one nurbs curve. since there could be multiple curves for one object we build a list of each curve.

## buildCVPointArray ##

Builds a MPointArray from the passed in CV value list.

> @param **inCVList**: _List of Dicts_. Each dict holds the information for one nurbs curve. since there could be multiple curves for one object we build a list of each curve.

> @return: _List of MPointArrays_.

## setCurveCvs ##

Sets a curves CVs to the values from inCVArray.

> @param **inCurve**: _String_. Name of curve to update.

> @param **inCVArray**: _List of MPointArrays_.

## addCurveValues ##

Add curve CV attributes to an object.

> @param **inObj**: _String_. Name of object to add curve cv values too.

> @param **inPoints**: _List_. Curves and their cv points.

## writeCurveValues ##

Write curve CV values to an object. Object must already have curve CV attributes. If it does not then add them with addCurveValues()

> @param **inObj**: _String_. Name of object to add curve cv values too.

> @param **inPoints**: _List_. Curves and their cv points.

## readCurveValues ##

Read stored curve CV values on an object. Object must have curve CV attributes created with addCurveValues().

@param **inObj**: _String_. Name of object to add curve cv values too.
@return: _List_. List of dicts.