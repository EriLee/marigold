import marigold.utility.XMLUtility as XMLUtility

class glBoxControl():
    def __init__( self, inSubType=None, inControlName=None ):
        buildFunctions = { 'shoulder' : self.shoulder,
                          'elbow' : self.elbow,
                          'hand' : self.hand,
                          'upVec' : self.upVec }
        f = buildFunctions[ inSubType ]
        self.subType = inSubType
        f( inControlName )
        
    def shoulder( self, inControlName ):
        print 'BOX SHOULDER'
        XMLUtility.createControlFromXML( 'glBox', self.subType, inControlName )
        
    def elbow( self, inControlName ):
        print 'BOX ELBOW'
        XMLUtility.createControlFromXML( 'glBox', self.subType, inControlName )
        
    def hand( self, inControlName ):
        print 'BOX HAND'
        XMLUtility.createControlFromXML( 'glBox', self.subType, inControlName )
        
    def upVec( self, inControlName ):
        print 'UP VEC'
        XMLUtility.createControlFromXML( 'glBox', self.subType, inControlName )