


import secrets
from bizutil import xweb
from bizutil import xmail, dbutil
from bizutil import dbutil
from py2neo import Node, Relationship
from datetime import datetime
from flask import session
from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, Relationship)

#from tradespace.models.aux import Domain


#import pyjwt
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
official_invites=[
    'rm.goldengate@gmail.com', # Roman
    'ssinghwb204@gmail.com',   # Sneha
    'xmusat@gmail.com',        # Alex
    'jonahcoyote@gmail.com',   # Jonah
    'biankasaetre@gmail.com',  # Bianka
    'jalbert.bgi@gmail.com',   # Jason
    'mmmdphd@gmail.com',       # Tata
    'greglewis111@gmail.com',  # Greg
    'joe_gough_22@gmail.com',  # Joe
    'steve',                   # Steve
    'james',                   # James
    'erika',                   # Erica
    'miccco@gmail.com',        # Mico
    'm2fxllc@gmail.com'        # Logger
]

# neomodel_install_labels app.py --db bolt://neo4j:ZONE_ONE_ZERO@localhost:7687


class User( StructuredNode ):
    uuid = UniqueIdProperty()
    email = StringProperty(unique_index=True)
    pw = StringProperty()
    depth = IntegerProperty(index=True, default=0)
    domains = Relationship('tradespace.models.aux.Domain','PERMITS')

    def logged_in(self , *args , **kwargs ):
        # check session # session.
        if( self.email and 'userinfo' in session  ):
            return True
        else:
            return False

    def invited_user(self , *args , **kwargs):
        return self.email in official_invites

    @classmethod
    def merge(  *args , **kwargs ):
        graph = dbutil.get_graph()
        user_instance = User( *args , **kwargs )
        tx = graph.begin()
        n = Node("User" , **kwargs )
        tx.merge(n, primary_label='User', primary_key='email' )
        tx.commit()
        user_instance.node = user_instance
        return user_instance



    def generate_registration( self, *args , **kwargs):
        from tradespace.models.aux import Registration
        token = secrets.token_urlsafe(16)
        r = Registration( uuid=        token,
                          ip=          xweb.get_ip(),
                          domain=      xweb.get_domain() ,
                          create_date= datetime.now() ).save()
        rel = r.user.connect( self )
        try:
            xmail.send(
                recipient=self.email ,
                subject=xweb.get_domain()+' Activation',
                message=xweb.get_protocol()+xweb.get_url()+'/activate/'+token )
        except Exception as e:
            self.log_event(tag='auth_error')


    def activate_registration(self , registration ):
        from tradespace.models.aux import Domain
        d = Domain.nodes.get( name=registration.domain )
        self.domains.connect( d )

    def permission_on_domain(self):
        cur_domain = xweb.get_domain()
        if len( list( self.domains.filter( name=cur_domain) ) )>0:
            return True
        else:
            return False

    def log_event(self , *args , **kwargs ):
        graph = dbutil.get_graph()
        tx = graph.begin()
        tag = kwargs['tag']
        u = graph.nodes.match("User", email=self.email )
        e = Node( "Event" , domain=domain , tag=tag )
        r = Relationship( u , "EMANATES" , e)
        tx.create(e)
        tx.create(r)
        tx.commit()

    def termify_domain(self , *args , **kwargs):
        domain = kwargs['domain']
        ip = kwargs['ip']
        graph = dbutil.get_graph()
        tx = graph.begin()
        u = graph.nodes.match("User", email=self.email )
        if( u.email in official_invites ):
            t = Node("Terms", domain=domain , ip=ip )
            tx.create( Relationship( u , "AGREES" , t ) )
            tx.commit()
            return True
        else:
            return False


    def activation_on_domain(self , *args , **kwargs ):
        graph = dbutil.get_graph()
        tx = graph.begin()
        u = graph.nodes.match("User", email=self.email ).first()
        a = graph.nodes.match("Activation" , domain=xweb.get_domain() ).first()
        if( u and a):
            rlt =Relationship(u,a)
            records = graph.run("MATCH ( u:User { email:$email} )-[r]-( a:Activation ) RETURN r" , email=self.email , domain = xweb.get_domain() )
            recs = records.data()
            recslen = len( recs )
            if( len( recs ) > 0 ):
                return True
            else:
                return False
        else:
            return False

    def terms_on_domain(self , *args , **kwargs ):
        graph = dbutil.get_graph()
        domain = args[0]
        graph = dbutil.get_graph()
        u = graph.nodes.match("User", email=self.email )
        t = graph.nodes.match("Terms", domain=domain )
        ut =  Relationship(u, "HAS", t)
        return graph.exists( ut )


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



    # JWT
    #This info is often referred to as JWT Claims.
    # We utilize the following “claims”:
    #exp: expiration date of the token
    #iat: the time the token is generated
    #sub: the subject of the token (the user whom it identifies)
    #The secret key must be random and only accessible server-side. Use the Python interpreter to generate a key:
    #  >>> import os
    #  >>>  os.urandom(24)
    #  b"\xf9'\xe4p(\xa9\x12\x1a!\x94\x8d\x1c\x99l\xc7\xb7e\xc7c\x86\x02MJ\
    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
