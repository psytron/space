ray( wrapper ) 
import ray


ray.init( '0.0.0.0' )

PoolModel = ray.remote( PoolModel )
poolModel = PoolModel.options(name='modelactor').remote()  #, lifetime='detached'
poolModel.run.remote()

cs = [ Tokens, Pool ]

# process_objects 


def run( process_objects ):
    wrapped = [ ray.remote( c ) for c in process_objects ]
    procs = [ p.remote() for p in wrapped ]
    [ x.run.remote() for x in procs ]
