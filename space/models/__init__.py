from .chunk import Chunk
from .user import User
from .agent import Agent
from .vehicle import Vehicle
from .sample import Sample
from .aux import Domain, Registration


# DataModel
# Actor , User , Vehicle, Sample


# Actor -has->  Credentials
# Actor -has-> Credential  -has-> Domain
# Index{ type:'Asset' } -has{ :CONVERSION | :TRANSFER , ->

# Index { type:'AssetAggregate' , base:'btc' } -- has -> Vehicle
#