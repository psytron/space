
from py2neo import Node

#pip install neo4j-driver
#from neo4j.v1 import GraphDatabase
#GraphDatabase.driver(uri, auth=(user, password)

from bizutil import dbutil


class Chunk:
    def __init__(self, x):
        self.identifier = x
        self._driver = dbutil.get_session()
        self.session = dbutil.get_session()
    #def __init__(self, uri, user, password):
    #    self._driver = GraphDatabase.driver(uri, auth=(user, password))


    def find_or_create( self , *args , **kwargs ):
        chunk = self.session.run(" MATCH ( x :Chunk ) RETURN x ")[0]
        if chunk:
            return chunk, False
        else:
            chunk = Node("Chunk", **kwargs )
            graph.create( chunk )
            return chunk, True

    def find_or_create_OG( *args , **kwargs ):
        chunk = graph.nodes.match("Chunk" , **kwargs ).first()
        if chunk:
            return chunk, False
        else:
            chunk = Node("Chunk", **kwargs )
            graph.create( chunk )
            return chunk, True


    def find_all( *args , **kwargs ):
        chunks = graph.nodes.match("Chunk" , **kwargs )
        return chunks



    def close(self):
        query = '''
         USING PERIODIC COMMIT 1000
         LOAD CSV FROM {file} AS col
         CREATE (pd:Provider {npi: col[0], entityType: col[1], address: col[20]+col[21], city: col[22], state: col[23], zip: col[24], country: col[25]})
         FOREACH (row in CASE WHEN col[1]='1' THEN [1] else [] END | SET pd.firstName=col[6], pd.lastName = col[5], pd.credential= col[10], pd.gender = col[41])
         FOREACH (row in CASE WHEN col[1]='2' THEN [1] else [] END | SET pd.orgName=col[4])
        '''
        self._driver.close()

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]










#chunk = graph.find_one("Chunk", property_key="identifier", property_value="viglar")
#chunk = graph.data("MATCH (a:Person) RETURN a.identifier LIMIT 4")
#print( matcher.match("Person", name="Keanu Reeves").first() )
# PRINTS ALL KEANUS
# [ (a["identifier"]) for a in graph.nodes.match("Chunk" , identifier="Keanu Reeves") ]
# chunk = matcher.match("Chunk", identitifer=strizzle ).first()
# chunk = graph.run("MATCH (a:Chunk) RETURN a.identifier LIMIT 1")