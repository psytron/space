


from neomodel import (config, StructuredNode, StringProperty, IntegerProperty,
                      UniqueIdProperty, RelationshipTo, RelationshipFrom , Relationship )
from tradespace.models import User


#class Country(StructuredNode):
#    code = StringProperty(unique_index=True, required=True)
#    # traverse incoming IS_FROM relation, inflate to Person objects
#    inhabitant = RelationshipFrom('Person', 'IS_FROM')

class Domain(StructuredNode):
    uuid = UniqueIdProperty()
    name = StringProperty()
    user = Relationship('tradespace.models.User','PERMITS')

class Registration(StructuredNode):
    uuid = UniqueIdProperty()
    user = Relationship( 'tradespace.models.User' , 'BINDS')
    domain = StringProperty()
    ip = StringProperty()
