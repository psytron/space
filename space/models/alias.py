

############################################
#  import pandas as pd
from os import path
import yaml, time, datetime
#from py2neo import Node
from datetime import datetime
from collections import defaultdict
from bizutil import format, cass, dbutil
from bizutil import parallelizer
from bizutil import neo
from bizutil import xtime
from tradespace.models import User
from tradespace.models import Sample
from tradespace.models.vehicle import Vehicle
from tradespace.models.xobject import Xobject
from tradespace import symbols, megablobstore
from tradespace import drivers








class Alias:

    def __init__(self , *args , **kwargs ):
        print(' new Alias ')
        print(' incoming should be LIST of Credentials? ')




    def sync_orderbooks():

        ovs = orderbook_vehicles() # orderbook_vehicles_by_whitelist in config ?
        for veh in ovs:
            vals = veh.getOrderbookStats()
            for s in vals:
                cass.insert_entry( veh.domain, veh.symbol, s, xtime.series_now(), vals[s] )


    def sync( *args , **kwargs ):
        subset = parallelizer.select_segment( vehicles() )
        parallelizer.runxl( subset , 'sync' )
        ##for sx in subset:
        ##    sx.sync()

    def synco( *args , **kwargs ):
        subset = parallelizer.select_segment( vehicles() )
        parallelizer.runxl( subset , 'synco' )
        #for sx in subset:
        #    sx.synco()
