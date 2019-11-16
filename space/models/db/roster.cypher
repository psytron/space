create ( gr:Actor   { name:'Greg Lewis'} )
create ( ro:Actor   { name:'Roman Malecki' } )
create ( jo:Actor   { name:'Joe Gough' } )




# to delete node by native id:

MATCH (p:Person) where ID(p)=1
OPTIONAL MATCH (p)-[r]-() //drops p's relations
DELETE r,p
