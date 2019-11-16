from tradespace.models.sample import Sample
from bizutil import neo, dbutil
import pandas as pd
import time
#from tradespace import rdd
from tradespace.drivers import cache as drivercache
from bizutil import hashtricks as ht
from bizutil import xtime
from bizutil.format import block
from bizutil.format import block_right
from datetime import datetime
from bizutil import cass


class Vehicle:

    def __init__(self , *args , **kwargs ):
        self.domain = kwargs['domain']
        self.alias = kwargs.get('alias', 'default')
        self.carrier = kwargs['domain']
        self.symbol = kwargs['symbol']
        self.base = kwargs['base'] if 'base' in kwargs else kwargs['symbol'].split('/')[0]
        self.quote = kwargs['quote'] if 'quote' in kwargs else kwargs['symbol'].split('/')[1]
        self.deposit_info = None
        #self.logic = drivercache.instance( domain=kwargs['domain'] )
        self.logic = drivercache.get( alias=self.alias , domain=self.domain )
        self.prev_asks = False
        self.prev_bids = False
        #self.last_vol = { 'timestamp':datetime.utcnow() , 'val':0 }

    @classmethod
    def merge( self,   *args , **kwargs ):
        instance = Vehicle( *args , **kwargs )
        node_data = ht.erase_keys( kwargs , ['apiKey','key','secret','password','passphrase'] )
        n = neo.hash_merge( "Vehicle" , {'domain':kwargs['domain'] , 'symbol':kwargs['symbol'] } , node_data )
        instance.node = n
        return instance

    def dbref(self , *args , **kwargs):
        inst = neo.power_merge( "Vehicle" , {'domain':self.domain , 'base':self.base , 'quote':self.quote  } )
        return inst

    def base(self):
        return self.symbol.split('/')[0]

    def getSample( self , *args , **kwargs):
        symbol = kwargs['symbol']
        print( self.domain )

    def syncTrades(self):
        trds = self.logic.fetchTrades(self.symbol)
        l=3
        for tr in trds:
            print( trds )
        # are we iterating writes?
        # iterating non existing writes repeatedly?
        # its the same issue as with history

    def sync( self ,*args , **kwargs):
        try:
            vals = self.logic.fetchTicker( self.symbol )
            # vals['series']= kwargs.get('time_series', datetime.now().replace(second=0, microsecond=0) )
            # vals['series']= kwargs.get('time_series', datetime.now().replace(microsecond=0) )
            vals['series']= xtime.series_now()
            vals['domain']=self.domain
            match_obj={ 'symbol':self.symbol , 'domain':self.domain }
            #samp = Sample( **vals) #samp.sync()
            series = xtime.series_now()

            cass.insert_entry( vals['domain'], vals['symbol'], 'close', series, vals['close'])
            cass.insert_entry( vals['domain'], vals['symbol'], 'high', series, vals['high'])
            cass.insert_entry( vals['domain'], vals['symbol'], 'low', series, vals['low'])
            cass.insert_entry( vals['domain'], vals['symbol'], 'bid', series, vals['bid'])
            cass.insert_entry( vals['domain'], vals['symbol'], 'ask', series, vals['ask'])

            if vals.get('baseVolume') or False :
                cass.insert_entry( vals['domain'], vals['symbol'], 'bvol', series, vals['baseVolume'])

            if vals.get('quoteVolume') or False :
                cass.insert_entry( vals['domain'], vals['symbol'], 'qvol', series, vals['quoteVolume'])

            if vals.get('open') or False :
                cass.insert_entry( vals['domain'], vals['symbol'], 'open', series, vals['open'])
            #cval = cass.cval( self.domain , self.symbol , 'vol' , xtime.series_now_minus(1) )
            #cass.insert_entry( vals['domain'], vals['symbol'], 'vol', series, vals['baseVolume'])
            #cass.insert_entry( vals['domain'], vals['symbol'], 'xvol', series, vals['baseVolume'])
            ppp=4
        except Exception as e:
            print( "Vehicle Sync Exception: ",self.domain,' ',self.symbol,' \n', e )
            try:
                print(vals)
            except Exception as e2:
                print('Exception printing vals ',e2)


    def patch( self , *args ,**kwargs ):
        h_sym = self.symbol
        h_dom = self.domain
        cur_date = datetime.utcnow()
        cur_timestamp = datetime.utcnow().timestamp()
        cur_date_from_ts = datetime.fromtimestamp( cur_timestamp )
        df = rdd.segment( [self.domain],[self.symbol],['vol'],16480,16482)
        df = df.resample('1Min').last()
        df.index.rename('timecoord', inplace=True)

        resx  = self.logic.fetch_ohlcv(self.symbol, '1m')
        resx_by_time = { str( datetime.utcfromtimestamp(x[0]/1000)):x for x in resx }
        df_nans = df[df.isna().any(axis=1)]

        for index, row in df_nans.iterrows():
            if str( index ) in resx_by_time:
                x1obj = resx_by_time[ str(index) ]
                h_date = index.to_datetime64()
                cass.insert_entry( h_dom , h_sym , 'open' , h_date , x1obj[1]  )
                cass.insert_entry( h_dom , h_sym , 'high' , h_date , x1obj[2]  )
                cass.insert_entry( h_dom , h_sym , 'low' ,  h_date , x1obj[3]  )
                cass.insert_entry( h_dom , h_sym , 'close', h_date , x1obj[4]  )
                cass.insert_entry( h_dom , h_sym , 'vol' ,  h_date , x1obj[5]  )

    def synco( self , *args ,**kwargs ):
        h_sym = self.symbol
        h_dom = self.domain

        try:
            if( self.logic.has['fetchOHLCV'] ):
                resx  = self.logic.fetch_ohlcv(self.symbol, '1m')
        except Exception as e:
            return False

        insert_count=0
        for rec in reversed(resx):
            h_date=datetime.fromtimestamp( rec[0]/1000 )
            cass.insert_entry( h_dom , h_sym , 'open' , h_date , rec[1]  )
            cass.insert_entry( h_dom , h_sym , 'high' , h_date , rec[2]  )
            cass.insert_entry( h_dom , h_sym , 'low' ,  h_date , rec[3]  )
            cass.insert_entry( h_dom , h_sym , 'close', h_date , rec[4]  )
            cass.insert_entry( h_dom , h_sym , 'vol' ,  h_date , rec[5]  )
            insert_count+=1
            if insert_count > 3:
                break


    def patch_ORIGINAL_WORKING_WITHOUT_WRITING_FULL_VALS( self , *args ,**kwargs ):
        h_sym = self.symbol
        h_dom = self.domain
        cur_date = datetime.utcnow()
        cur_timestamp = datetime.utcnow().timestamp()
        cur_date_from_ts = datetime.fromtimestamp( cur_timestamp )
        df = rdd.segment( [self.domain],[self.symbol],['close'],16480,16482).resample('1Min').last()
        df.index.rename('timecoord', inplace=True)

        resx  = self.logic.fetch_ohlcv(self.symbol, '1m')
        resx_by_time = { str( datetime.utcfromtimestamp(x[0]/1000)):x for x in resx }
        df_nans = df[df.isna().any(axis=1)]

        for index, row in df_nans.iterrows():
            if str( index ) in resx_by_time:
                x1obj = resx_by_time[ str(index) ]
                h_date = index.to_datetime64()
                cass.insert_entry( h_dom , h_sym , 'open' , h_date , x1obj[1]  )
                cass.insert_entry( h_dom , h_sym , 'high' , h_date , x1obj[2]  )
                cass.insert_entry( h_dom , h_sym , 'low' ,  h_date , x1obj[3]  )
                cass.insert_entry( h_dom , h_sym , 'close', h_date , x1obj[4]  )
                cass.insert_entry( h_dom , h_sym , 'vol' ,  h_date , x1obj[5]  )

    #if 'since' in kwargs:
    #    #resx = self.logic.fetch_ohlcv(self.symbol, '1m' , since=kwargs['since'] , limit=1000 )
    #    resx = self.logic.fetch_ohlcv(self.symbol, '1m' , since=int(kwargs['since']*1000), limit=1000)
    #else:


    def impute_derivatives(self , *args, **kwargs ):
        if('close' in args[0] ):
            vals = args[0]
            neo.power_upsert('Vehicle', {'domain':self.domain,'symbol':self.symbol} , {'close':vals['close'] })

    def samples(self,*args, **kwargs):
        #from models import Sample
        # should now be CASS somethingf
        session = dbutil.get_store()
        rows = session.execute("""SELECT * FROM sample WHERE domain=%s AND symbol=%s""" , ( self.domain , self.symbol ) )
        return rows

    def ops(self):
        # CONVERSIONS
        # read fees if have private API
        if self.logic.has['privateAPI']:
            fees = self.logic.fees
            #print( fees )
        convertibles = [x['quote'] for x in self.logic.fetchMarkets() if x['base'] == 'LTC' ]
        return convertibles
        # TRANSFERS








    ##################### TRANSFER OPTIONS #######################
    ##############################################################
    def trades(self):
        trades_arr = self.logic.fetchMyTrades( self.symbol )
        for t in trades_arr:
            print( block(t['datetime'],19) ,block(t['symbol'],8), block(t['price'],14) ,  block_right(t['side'],4),block(t['amount'],9),block(t['cost'],9) )
        return trades_arr

    def orders(self):
        return self.logic.fetch_open_orders( self.symbol )

    def cancel_order(self , id_in ):
        res = self.logic.cancelOrder( id_in )
        print( res )
        return res

    def cancel_orders(self):
        # finds and cancels all on vehicle
        for o in self.orders():
            self.cancel_order( o['id'] )


    def concentrate(self):
        # This aggregates all balances from other coins onto this
        print('concentrate')

    def balances(self):
        all_balances = self.logic.fetchBalance()
        free = all_balances['free']
        for b in free:
            if free[b]>0:
                print( block( b ,4 ) , block( free[b] ,10 )  )
        f = { x:free[x] for x in free if free[x]>0 }
        return f
    def base_balance(self):
        all_balances = self.logic.fetchBalance()
        currency_obj = all_balances[ self.base ] if self.base in all_balances else {}
        balance = currency_obj['free'] if 'free' in currency_obj else 0.0
        return balance
    def quote_balance(self):
        all_balances = self.logic.fetchBalance()
        currency_obj = all_balances[ self.quote ] if self.quote in all_balances else {}
        balance = currency_obj['free'] if 'free' in currency_obj else 0.0
        return balance
    # aliases
    bal = base_balance
    bbal = base_balance
    qbal = quote_balance
    balance = base_balance

    def max_entry(self):
        fee_percent = self.market()['maker']
        avail_bal = self.qbal()
        price = self.fastBuyPricePerAvailQuote( avail_bal )
        target_amount_pre_fees = avail_bal / price # Calc avail purch power
        target_amount = target_amount_pre_fees - ( target_amount_pre_fees * fee_percent )
        obj={ 'amount':round(target_amount,8),
              'price':price}
        return obj
        #market_values = self.market()
        #prec_amount = market_values['precision']['amount']
        #prec_price = market_values['precision']['price']
        #min_trans = market_values['limits']['amount']['min']


    def fastBuyPricePerAvailQuote(self,bal_in):
        ob = self.orderbook()
        asks = ob['asks']
        q_avail=bal_in
        price=0
        for nx, a in asks.iterrows():
            ask_price=a[0]
            ask_avail=a[1]
            cost_to_fill_segment = ask_avail * ask_price
            q_avail -= cost_to_fill_segment
            if q_avail <= 0:
                price=ask_price
                break;
            else:
                continue
        return price











    def enter(self , amount_in=False ):
        if amount_in:
            target_amount= amount_in
            target_price = self.fastBuyPrice( target_amount )
        else:
            buy_obj = self.max_entry()
            target_price  = buy_obj['price']
            target_amount = buy_obj['amount']  # Fees included ( rounded )

        fee_percent = self.market()['maker']
        amount_cost = target_amount * target_price
        fee_cost = amount_cost * fee_percent
        expected_cost = amount_cost + fee_cost

        print('      Buy Order: ', self.symbol   ,'\n'
              '  Target Amount: ', target_amount ,'\n'
              '   Target Price: ', target_price  ,'\n'
              '          Fee %: ', fee_percent   ,'%\n'
              '       Fee Cost: ', fee_cost      ,'\n'
              '    Amount Cost: ', amount_cost   ,'\n'
              'Expected T Cost: ', expected_cost ,'\n')
        self.logic.verbose=True
        res = self.logic.create_order( self.symbol , 'limit' , 'buy' , target_amount , target_price , {'trading_agreement':'agree'} )
        self.logic.verbose=False
        return res











    def exit(self , amount_in=False ):
        base_bal=self.base_balance()
        if amount_in:
            target_amount = amount_in
        else:
            target_amount = base_bal

        if( target_amount == 0):
            raise Exception('Zero Ammount Cannot Load')

        price = self.fastSellPrice( base_bal )
        target_price = price

        fee = self.market()['maker']
        expected_fee = ( target_amount * fee )
        expected_p = ( target_amount * price )

        print('     Sell Order: ', self.symbol   ,'\n'
              '         Amount: ', target_amount ,'\n'
              '   Target Price: ', target_price  ,'\n'
              '            Fee: ', fee           ,'% \n'
              '   Expected_fee: ', expected_fee  ,'\n'
              ' Expect_proceed: ', expected_p    ,'\n'
              '       Base Bal: ', base_bal,'',self.quote )
        self.logic.verbose=True
        res = self.logic.create_order( self.symbol , 'limit' , 'sell' , target_amount , target_price , {'trading_agreement':'agree'} )
        self.logic.verbose=False
        return res



        # Gotta Save some record of the Transaction intent # Ideal=
        # t = Transaction( domain=self.domain , target_amount=target_amount , target_price=target_price )
        # REAL TRANSACTION:
        # res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        # def create_order(self, symbol, type, side, amount, price=None, params={}):
        # res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        # res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        # res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        # res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        # print( res )



    def unload(self, amount=False, vehicle=False ):
        if( not amount ):
            amount = self.balance()
            if( amount == 0):
                raise Exception('Zero Balance Cannot Unload')
        if( not vehicle ):
            vehicle = self
        vehicle.load( amount , self  )

    def load(self , amount=False , vehicle=False):
        if( not amount ):
            amount = self.balance()
            if( amount == 0):
                raise Exception('Zero Ammount Cannot Load')
        if( not vehicle ):
            vehicle = self
        x =' yes'




    def convert_maximum_to(self , target_base_in):
        # find_or_get_param_of_price
        amount = self.balance()
        if( amount == 0):
            return ' 0 balance cannot convert '
        price = self.getReasonablePrice()

        target_base_in

        target_amount = amount
        target_price = price

        self.logic.verbose=True
        print(' Sell Order in progress:: ', target_amount , target_price )
        res = self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        print( res )
        self.logic.verbose=False
        return res

        #self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )
        #return 'would convert: '+str(amount)+' at:'+str(price)+'  to: '+str(base_in)
        # find_amount_param_or_balance#print(' max up ',base_in )
    def increase_payload(self):
        self.create_order()
    def allocate(self, amount):
        print(' allocating means BUY from available ?')
        # a vehicle is only 1 pair , right?

    def retrieve_deposit_info(self):
        cluster = False
        attempts = 0
        while not cluster and attempts < 4:
            try:
                cluster = self.logic.fetchDepositAddress( self.base )
            except Exception as e1:
                try:
                    cluster = self.logic.createDepositAddress( self.base )
                except Exception as e2:
                    attempts= attempts +1
                    print( 'wow create failed too: ',self.domain, self.symbol,' : ',e2)
        return cluster
    def memo(self):
        out_memo=False
        if self.deposit_info == None:
            self.deposit_info = self.retrieve_deposit_info()
        if( 'tag' in self.deposit_info and self.deposit_info['tag'] != None ):
            out_memo = self.deposit_info['tag']
        else:
            if( 'destination_tag' in self.deposit_info['info'] ):
                out_memo = self.deposit_info['info']['destination_tag']
            else:
                out_memo = False
        return out_memo

    def address(self):
        if self.deposit_info == None:
            self.deposit_info = self.retrieve_deposit_info()
        return self.deposit_info['address']

    def transfer(self , target_amount , target_vehicle ):
        # prepare requirements:
        target_address = target_vehicle.address()
        target_memo = target_vehicle.memo()
        print(' Ok Flight check : ' , target_address , target_memo  )
        self.logic.verbose = True
        self.logic.withdraw( self.base , target_amount , target_address , tag=target_memo )
        self.logic.verbose = False 
        # Turn on Verbose for XFERS Cause yeah

    def withdraw(self , target_amount , target_address ):
        self.logic.withdraw( self.base , target_amount , target_address )
        #self.logic.withdraw(code, amount, address, tag=None, params={})
        #The code is the currency code (usually three or more uppercase letters, but can be different in some cases).
        #The withdraw method returns a dictionary containing the withdrawal id, which is usually the txid of the onchain transaction itself, or an internal withdrawal request id registered within the exchange. The returned value looks as follows:
        #{'id': '12345567890', // string withdrawal id, if any}

    def deposit_address(self):
        addy = False
        # a = self.logic.has['fetchDepositAddress']
        # b = self.logic.has['createDepositAddress']
        #self.logic.fetchDepositAddresses (codes = undefined, params = {})
        #self.logic.fetchDepositAddresses (codes = ['BTC','ETH'], params = {})
        attempts = 0
        while not addy and attempts < 4:
            try:
                cluster = self.logic.fetchDepositAddress( self.base )
                addy = cluster['address']
            except Exception as e1:
                try:
                    cluster = self.logic.createDepositAddress( self.base )
                    addy = cluster['address']
                    print( ' address not generated?: ', e1)
                    print(' tried create: ', addy )
                except Exception as e2:
                    attempts= attempts +1
                    print( 'wow create failed too: ',self.domain, self.symbol,' : ',e2)
        return addy
        # Some exchanges will also allow the user to create new addresses for deposits.
        # Some of exchanges require a new deposit address to be created for each new deposit.
        # The address for depositing can be either an already existing address that was created previously
        # or it can be created upon request. In order to see which of the two methods are supported,
        # check the exchange.has['fetchDepositAddress'] and exchange.has['createDepositAddress'] properties.
        # check SELF in DB For deposit address list
        # check exchange address balances if both don't exist issue new deposit address


    def create_order_examp(self):
        symbol = self.symbol
        side = 'sell' # 'buy'
        amount = 123.45  # your amount
        price = 54.321   # your price
        params = {
            'stopPrice': 123.45,
            'type': 'stopLimit' }
        order = self.logic.create_order( self.symbol, 'limit' , side, amount, price, params )

    def buyx( self  ):
        target_amount = 0.1
        target_price = 76.65
        #buy_vehicle=target_vehicle
        self.logic.create_limit_sell_order( self.symbol , target_amount , target_price , {'trading_agreement':'agree'} )

    def upfill(self):
        symbol = self.symbol
        type = 'limit'  # or 'market', other types aren't unified yet
        side = 'buy' # buy
        amount = 0.01  # your amount
        price = 54.321  # your price
        # overrides
        params = {
            'stopPrice': 123.45,  # your stop price
            'type': 'stopLimit',
        }
        order = self.logic.create_order( symbol, type, side, amount, price, params )







    ################################# INFORMATIONAL #####################################
    #####################################################################################
    def orderbook(self):
        ordr = self.logic.fetchOrderBook(self.symbol)
        books = { 'asks':pd.DataFrame(ordr['asks']) , 'bids':pd.DataFrame(ordr['bids']) }
        return books
    def getReasonablePrice(self):
        book = self.orderbook()
        lowest = book['bids'][0][0]
        highest = book['asks'][1][0]
        return lowest
    def fastPrice(self):
        book = self.orderbook()
        lowest = book['bids'][0][0]
        highest = book['asks'][0][2]
        return highest

    def fastSellPrice(self , quant):
        book = self.orderbook()
        bids = book['bids']
        bids['qsum']=bids[1].cumsum()
        price = bids[bids.qsum>=quant][0].iloc[0]
        return price

    def fastBuyPrice(self, quant):
        book = self.orderbook()
        asks = book['asks']
        asks['qsum']=asks[1].cumsum()
        # GET PRICE BY ROW WHERE QSUM > quant
        price = asks[asks.qsum>=quant][0].iloc[0]
        return price

    def getOrderbookStats(self):
        start_time = time.time()
        print(' in OrderBookStats  self.domain: ', self.domain )
        book = self.orderbook()
        df_bids = book['bids']
        df_asks = book['asks']
        top_bids=df_bids.head(15)
        top_asks=df_asks.head(15)

        out_obj = {}
        out_obj['ob_pingtime']=time.time()-start_time
        out_obj['ob_spread']= df_asks.iloc[0,0]-df_bids.iloc[0,0]

        out_obj['ob_bid_price_deviation']=df_bids.iloc[:,0].std()
        out_obj['ob_bid_quant_deviation']=df_bids.iloc[:,1].std()
        out_obj['ob_bid_vol']=df_bids.iloc[:,1].sum()
        out_obj['ob_ask_price_deviation']=df_asks.iloc[:,0].std()
        out_obj['ob_ask_quant_deviation']=df_asks.iloc[:,1].std()
        out_obj['ob_ask_vol']=df_asks.iloc[:,1].sum()

        out_obj['ob_t15_bid_vol']=top_bids[1].sum()
        out_obj['ob_t15_ask_vol']=top_asks[1].sum()
        out_obj['ob_t15_bid_range']=top_bids[0].max() - top_bids[0].min()
        out_obj['ob_t15_ask_range']=top_asks[0].max() - top_asks[0].min()

        # GET mid-point of spread
        # 'ob_new_ basically , graph if ob is leaning towards buyers or sellers market
        #'ob_topvol_fresh_bids'
        #'ob_topvol_fresh_asks'
        #'ob_big_vol_10_fresh_asks'
        # TO JSON IN  # doesn't work cause Cassandra type field
        #out_obj['ob_bids_json']=df_bids.to_json(orient='records')
        #out_obj['ob_asks_json']=df_asks.to_json(orient='records')

        if( self.prev_asks is not False ):
            set_diff_df = pd.concat([df_asks, self.prev_asks]).drop_duplicates(keep=False)
            out_obj['ob_fresh_asks']= set_diff_df.shape[0]
        else:
            out_obj['ob_fresh_asks']=0
        self.prev_asks = df_asks

        if( self.prev_bids is not False ):
            set_diff_df = pd.concat([df_bids, self.prev_bids]).drop_duplicates(keep=False)
            out_obj['ob_fresh_bids']= set_diff_df.shape[0]
        else:
            out_obj['ob_fresh_bids']=0
        self.prev_bids = df_bids

        return out_obj

    def fetchMarkets(self):
        self.logic.fetchMarkets()
        return self.logic.markets

    def market(self):
        try:
            return self.logic.market( self.symbol )
        except Exception as e:
            self.logic.load_markets()
            return self.logic.market( self.symbol )

    def caps(self , allowed_list ):
        allowed_markets = {e:False for e in allowed_list}
        all_markets = self.logic.loadMarkets()
        markets = self.logic.markets
        vehicles = rdd.vehicles()
        white_listed = {  x:markets.get(x) for x in allowed_markets if x in markets }
        #what_can_i_buy_with_this_base  = [ white_listed[x] for x in white_listed if white_listed[x]['quote']==self.base or white_listed[x]['base']==self.base ]
        where_can_i_move_this_base = [ x for x in vehicles if x.base==self.base and x.domain!=self.domain ]
        what_can_i_buy_with_this_base = [ x for x in vehicles if x.domain==self.domain and ( self.base == x.base or self.base == x.quote ) ]

        node_1 = self.dbref()
        outbound_conversions = []
        for b in what_can_i_buy_with_this_base :
            node_2 = b.dbref()
            if( node_1 != node_2):
                outbound_conversions.append( { 'type':'CONVERTS',  'source':node_1 , 'destination':node_2 ,'domain':self.domain , 'carrier':self.carrier })

        outbound_transfers = []
        for b in where_can_i_move_this_base :
            node_2 = b.dbref()
            outbound_transfers.append( { 'type':'TRANSFERS', 'source':node_1 , 'destination':node_2  , 'base':b.base })

        return {
            'transfers':outbound_transfers,
            'conversions':outbound_conversions  }


    def caps_ext(self , allowed_list ):
        all_markets = self.logic.loadMarkets()
        allowed_markets = {e:False for e in allowed_list}
        markets = self.logic.markets
        vehicles = rdd.vehicles()
        #white_listed = {  x:markets.get(x) for x in allowed_markets if x in markets }
        white_listed = all_markets
        #what_can_i_buy_with_this_base  = [ white_listed[x] for x in white_listed if white_listed[x]['quote']==self.base or white_listed[x]['base']==self.base ]
        where_can_i_move_this_base = [ x for x in vehicles if x.base==self.base and x.domain!=self.domain ]
        what_can_i_buy_with_this_base = [ x for x in vehicles if x.domain==self.domain and ( self.base == x.base or self.base == x.quote ) ]
        node_1 = self.dbref()
        outbound_conversions = []
        for b in what_can_i_buy_with_this_base :
            node_2 = b.dbref()
            if( node_1 != node_2):
                outbound_conversions.append( { 'type':'CONVERTS',  'source':node_1 , 'destination':node_2 ,'domain':self.domain , 'carrier':self.carrier })

        outbound_transfers = []
        for b in where_can_i_move_this_base :
            node_2 = b.dbref()
            outbound_transfers.append( { 'type':'TRANSFERS', 'source':node_1 , 'destination':node_2  , 'base':b.base })

        return {
            'transfers':outbound_transfers,
            'conversions':outbound_conversions  }








    def sync_orderbook(self):
        print(' sync order book ')
        # bids_df = pd.DataFrame( self.logic.fetchOrderBook('BTC/USDT')['asks'] ).max()
        # volume_loaded  = bids_df.sum()
        # Sample( domain, symbol, xclass ='TLVX' # total loaded volume
        # total_loaded_Offered_Units
        # total_ask_volume=22.0   asks.sum()
        # total_bid_volume=17.0  bids.sum()
        # spread =
        # low order =