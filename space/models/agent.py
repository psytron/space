from py2neo import Node, Relationship
from bizutil.dbutil import driver
from bizutil.dbutil import graph

class Agent:

    id = ''
    user_id=''
    actor_id=''
    identifier = ''
    credentials=[]



    def __init__(self , *args , **kwargs ):
        self.logic=kwargs['logic']
        print( 'instantiating')
    def init(self):
        print( ' hydrate ')
        self.session = dbutil.get_session()


    def evaluate_and_act(self , df ):
        print('evaluate and act: ')
        self.logic.evaluate_and_act()



    @classmethod
    def find_or_create( self,   *args , **kwargs ):
        obj_in = args[0]
        with driver.session() as session:
            obj = Agent( *args , **kwargs )
            a_record = session.run("MERGE( a:Agent  {identifier:$identifier}  ) RETURN a ",
                                    identifier=obj_in['identifier'])
            obj.identifier = obj_in['identifier']
            obj.node = a_record
            return obj


    # SO MUCH SMALLER
    def merge_credentials(self , *args , **kwargs ):
        creds = args[0]
        for c in creds:
            a = graph.nodes.match("Agent", identifier=self.identifier ).first()
            b = Node( "Credential" , domain=c['domain'] , key=c['key'] )
            graph.create( b )
            a_has_b = Relationship(a, 'HAS', b)
            graph.create( a_has_b )
            print(' creating link ')


    # SO MUCH BIGGER
    def merge_credentials_bare(self , *args , **kwargs ):
        print( "incoming credentials for: ", self.identifier , ' whats the package: ', kwargs)
        creds = args[0]
        with driver.session() as session:
            for c in creds:
                qry = ''' MERGE( a:Agent {identifier:$identifier} ) -[ l:HAS ]-> 
                               ( c:Credential { domain:$domain , key:$key }) 
                          RETURN a '''
                a = session.run( qry  ,
                          identifier=self.identifier,
                          domain=c['domain'] ,
                          key=c['key'] )
                print(' should be creating credential: ' , c['domain'] , c['key'] )



    def parse_wallets(self , *args , **kwargs ):
        from py2neo.data import Node, Relationship
        wallets = kwargs['wallets']
        for w in wallets:
            print( w )
            # should create
            a = Node("Agent", name="Alice")
            b = Node("Wallet", name= w['word'])
            ab = Relationship(a, "OWNS", b)
            # >>> ab
        # a_record = session.run(" MATCH ( a:Agent { email:'self.email'} )-[ :OWNS ]->( b:Domain ) RETURN a,b")