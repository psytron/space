from bizutil import cass, dbutil

insert = cass.insert_entry
from datetime import datetime

class Transaction():

    def __init__(self , *args , **kwargs ):
        self.source = kwargs['source']
        self.destination = kwargs['destination']
        self.status = 'CREATED'
        self.type = kwargs['type']
        self.source_symbol = self.source.symbol
        self.source_carrier = self.source.carrier
        self.create_date = datetime.now()
        self.update_date = datetime.now()

    def send(self):
        if self.type == 'buy' or self.type == 'sell':
            self.source.buy()
        else:
            print('no other fucntion defined :')

    def save(self, *args, **kwargs):
        dbutil.get_graph()

    def search_event_number_until_non_exist(self):
        # THIS BAllS OUT METHOD SHOULD RETRIEVE ALL EVENT_NUMBER PROPERTIES FROM NODE PROPERTIES
        properties = { 'struct':'all-transaction-properties' , 'event0':'some_string' , 'event1':'some_string2' , 'event3':'some_string' }

        all_events = []
        for ndx,k in enumerate( properties ):
            event_key = 'event'+str(ndx)+''
            if event_key in properties:
                all_events.append( properties[event_key] )
        print( all_events )


