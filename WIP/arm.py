'''
1. create joint positioners
2. aim constraint in chain build order
    a. setup up vector controls for switching axis of joint positioner
'''
import maya.cmds as cmds

class GameThing(object):
    def __init__(self, node):
        self.node = node
 
    #controllers
    @property
    def controllers(self):
        return cmds.listConnections(self.node + ".controllers")
 
    @controllers.setter
    def controllers(self, cons):
        #disconnect existing controller connections
        for con in cmds.listConnections(self.node + '.controllers'):
            cmds.disconnectAttr(self.node + '.controllers', con + '.rigging')
 
        for con in cons:
            if cmds.objExists(con):
                if not cmds.attributeQuery('rigging', n=con, ex=1):
                    cmds.addAttr(con, longName='rigging', attributeType='message', s=1)
                cmds.connectAttr((self.node + '.controllers'), (con + '.rigging'), f=1)
            else:
                cmds.error(con + ' does not exist!')


class frameRootBit( object ):
    def __init__( self, node ):
        self.node = node       
        
    @property
    def test( self ):
        print 'self.node: {0}'.format( self.node )
        
    @test.setter
    def test( self, inThing ):
        print 'test.setter'
        print inThing
        
sphere = cmds.sphere( radius=10 )
obj = frameRootBit( sphere )
obj.test
obj.test = 'thing'