
match (x) return x



// DELETE

// Delete Everything
MATCH (n) DETACH DELETE n

// Delete with No Label
MATCH (n) where size(labels(n)) = 0 DETACH DELETE n

// Delete by Label x, which is missing properties y :


// Delete by ID
MATCH (n) where id(n) = xx DETACH DELETE n





MERGE (keanu:Person { name: 'Keanu Reeves' })
  ON CREATE SET keanu.created = timestamp()
RETURN keanu.name, keanu.created

# I've spent years using all kinds of databases, postgres, mySQL  Years with alone . CouchDB , MongoDB, Redis, MapReduce, Cassandra, on and on
# I keep loving NEO4J , Its such a beauty. It has changed the way I think about apps and my own mind.
# Its like an amorphous mesh , its such fun. And you can implement complex UNIX level granularity roles and permissions systems.
# The DB for my apps moving forward is NEO4J + Cassandra    NEO is the graph and Cass is the time series.

# Unique Keys
MATCH (a:Asset)
UNWIND keys(a) AS key
RETURN collect(distinct key)



MERGE (person:Person) ON MATCH SET person.found = TRUE RETURN person.name, person.found





// Uniqueness contraints
CREATE CONSTRAINT ON (r:Role)
ASSERT r.name IS UNIQUE

CREATE CONSTRAINT ON (u:User)
ASSERT u.email IS UNIQUE