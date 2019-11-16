from bizutil import dbutil
from bizutil import web
from bizutil import neo


#       ooooo
#      ooooooo
#      ooooooo
#      ooooooo
#       ooooo
#   oooooooooooo
#  oooooooooooooo
#  oooooooooooooo
#  oooooooooooooo
#
class Xobject:

    id = ''
    xclass = 'Base'
    node = False

    def __init__(self , *args , **kwargs ):
        self.xclass = kwargs['xclass']
        self.xid = kwargs['xid'] if 'xid' in kwargs else False
        self.domain = web.get_domain()
        self.blob = kwargs

    @classmethod
    def merge( self,   *args , **kwargs ):
        instance = Xobject( *args , **kwargs )

        xobj_obj = {}
        xobj_obj['title']=kwargs['address']
        xobj_obj['price']=kwargs['price'] if kwargs['price'] != None else 'CALL'
        xobj_obj['address']=kwargs['address']
        xobj_obj['city']=kwargs['city']
        xobj_obj['link']=kwargs['link']
        xobj_obj['xclass']=kwargs['xclass']
        xobj_obj['main_image']=kwargs['main_image']

        n = neo.power_merge( xobj_obj['xclass'].capitalize() , xobj_obj )
        instance.node = n
        return instance





    def apps_on_domain( self, *args , **kwargs):
        graph = dbutil.get_graph()
        apps=[]
        domain = args[0] if args[0] else self.domain
        if self.logged_in() and self.activation_on_domain( domain ):
            records = graph.run("MATCH ( a:App )--( d:Domain { url:$url} ) RETURN a" , email=self.email , url=domain )
            apps +=  [ dict( x['a'] ) for x in records.data() ]
        elif self.logged_in() and not self.activation_on_domain( domain ):
            records = graph.run("MATCH ( a:App ) WHERE a.identifier='logout' XOR a.type='contingency'  RETURN a" )
            apps +=  [ dict( x['a'] ) for x in records.data() ]
        else:
            records = graph.run("MATCH ( a:App { type:'auth'} ) RETURN a" , email=self.email )
            apps +=  [ dict( x['a'] ) for x in records.data() ]
        return apps