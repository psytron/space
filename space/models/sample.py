#from app import db

from bizutil import xtime, cass, dbutil

insert = cass.insert_entry

class Sample():
    id          = ''
    domain      = ''
    symbol      = ''
    typeclass   = ''
    series = ''
    #  SAMPLE BASE SEGS
    close       = ''
    bid         = ''
    ask         = ''
    high        = ''
    low         = ''
    vol         = ''
    vals = ''

    def __init__(self , *args , **kwargs ):

        self.domain = kwargs['domain']
        self.symbol = kwargs['symbol']
        self.vals = kwargs

    @classmethod
    def syncdb( self,   *args , **kwargs ):
        session = dbutil.get_cluster()
        session.execute("CREATE KEYSPACE IF NOT EXISTS gspace WITH REPLICATION = { 'class':'NetworkTopologyStrategy', 'datacenter1':1 }; ")
        session.execute(""" CREATE TABLE IF NOT EXISTS xsample (
                carrier text,
                symbol text,
                xclass text,
                series timestamp,
                xval decimal,
                PRIMARY KEY ( (carrier,symbol,xclass),series) );
        """)

        #    series        |  carrier  |     native   |    xclass   |   xval
        # (S1)  01:01:00   |  NASDAQ   |    GBP/USD   |    close    |      1.10
        # (S1)  01:01:00   |  NYSE     |    EUR/USD   |    close    |      2.11
        # (S1)  01:01:00   |  BITTREX  |    EUR/USD   |    close    |      2.11
        # (S1)  01:01:00   |  APDEX    |    EUR/USD   |    close    |     11.11
        # (S1)  01:01:00   |  GDAX     |    BTC/USD   |    close    |   1000.00

        # (S2)  01:02:00   |  NASDAQ   |    GBP/USD   |    close    |      1.20
        # (S2)  01:02:00   |  NYSE     |    EUR/USD   |    close    |      2.11
        # (S2)  01:02:00   |  BITTREX  |    EUR/USD   |    close    |      2.11
        # (S2)  01:02:00   |  APDEX    |    EUR/USD   |    close    |     22.22
        # (S2)  01:02:00   |  GDAX     |    BTC/USD   |    close    |   2000.00

        # (S3)  01:03:00   |  NASDAQ   |    GBP/USD   |    close    |      1.30
        # (S3)  01:03:00   |  NYSE     |    EUR/USD   |    close    |      3.33
        # (S3)  01:03:00   |  BITTREX  |    EUR/USD   |    close    |      3.33
        # (S3)  01:03:00   |  APDEX    |    EUR/USD   |    close    |     33.33
        # (S3)  01:03:00   |  GDAX     |    BTC/USD   |    close    |   3000.00

        # (S4)  01:04:00   |  NASDAQ   |    GBP/USD   | close_proj  |     1.40


        # I've watched tons of video tutorials about struturing schema for timeseries data
        # Curious if you could advise if this makes sense.

        # High order objective in this example is to pass some search tokens to an "economy" object
        # the economy object represents an RDD which has historical time series data for all stocks
        # example method call:
        #   economy.getDataFrame( ["NASDAQ","close"] , ["S&P500","close"], ["TEXAS OIL","open","close","volume"] )
        # The above example would dynamically infer that the user wishes to retreive 5 recorded signal streams
        # returned in the form of a matrix ( data frame ) example from above values:

        # S1 [  01:01:00  , 0.11 , 14.50 , 1242.43 , 11.11 ,  1000.00  ]
        # S2 [  01:02:00  , 0.14 , 15.51 , 1266.53 , 22.22 ,  2000.00  ]
        # S3 [  01:03:00  , 0.19 , 16.53 , 1298.83 , 33.33 ,  3000.00  ]

        # <--- each row is single slice of time, with all values as requested
    def save(self):
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'close', series, self.vals['close'])

    def sync(self):
        series = xtime.series_now()
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'close', series, self.vals['close'])
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'high', series, self.vals['high'])
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'low', series, self.vals['low'])
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'bid', series, self.vals['bid'])
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'ask', series, self.vals['ask'])
        cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'vol', series, self.vals['baseVolume'])
        if( self.vals['open'] != None ):
            cass.insert_entry(self.vals['domain'], self.vals['symbol'], 'open', series, self.vals['open'])
        #if self.vals['vwap']== None:
        #    x=1
        #cass.insert_entry( self.vals['domain'] , self.vals['symbol'] , 'vwap',  series , self.vals['vwap'] )
        #for v in self.vals: # this was meant to iterate available fields and convert to rows, but was actually
        # doubling and trippling the below inserts:
        # insert( self.vals['domain'] , self.vals['symbol'] , 'high' ,  series , self.vals['high'] )




    #def get_or_create( *args , **kwargs ):
    #    from models.dbutil import get_one_or_create
    #    return get_one_or_create( db.session , Sample, **kwargs )#
#
#    def save(self):
#        db.session.add( self )
#        db.session.commit()


