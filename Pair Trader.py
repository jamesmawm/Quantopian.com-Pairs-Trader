stdevType1 = ta.STDDEV(timeperiod=10,nbdev=1)
stdevType2 = ta.STDDEV(timeperiod=30,nbdev=1)
stdevType3 = ta.STDDEV(timeperiod=100,nbdev=1)

BET_SIZE_1 = 100

def initialize(context):   
    context.citi = sid(1335)
    context.ms = sid(17080)
    set_benchmark(sid(8554))
    
    context.max_notional = 10000.1
    context.min_notional = -10000.0
    context.buy_signals = 0
    context.sell_signals = 0
    context.high_pnl = 0

def handle_data(context, data):
    sid1 = context.citi
    sid2 = context.ms
    
    sid1data = data[sid1]
    sid2data = data[sid2]
    
    mavg1 = sid1data.mavg(30)
    mavg2 = sid2data.mavg(30)
    beta = mavg1 / mavg2
            
    price1 = sid1data.price
    price2 = sid2data.price    
    fairPriceOf1 = beta * price2  
    diff1 = price1 - fairPriceOf1
    diff1Percent = (diff1) / price1 * 100
    
    stddev1 = sid1data.stddev(30)
    stddev2 = sid2data.stddev(30)  
    vwap1 = sid1data.vwap(30)   
    
    m = "price1:{price1} diff1Percent:{diff1} stddev1:{stddev1} "
    m = m.format(price1=price1, diff1=diff1Percent, stddev1=stddev1);
    log.info(m)     
    log.info(vwap1)     

    # Portfolio positions
    sid1_pos = context.portfolio.positions[sid1].amount
    is_neutral = (sid1_pos==0)
    is_long = (sid1_pos > 0)
    is_short = (sid1_pos < 0)
    market_value = sid1_pos * price1
    pnl = context.portfolio.pnl
    high_pnl = context.high_pnl
    
    if pnl > high_pnl:
        high_pnl = pnl
        context.high_pnl = high_pnl
    
    trade_size = BET_SIZE_1
    trade_price = trade_size * price1             
        
    datetime = get_datetime()
    
    # Conditions
    is_sell_by_diff = diff1Percent > 0.20
    is_buy_by_diff = diff1Percent < 0.20
    
    is_stdev_trade = stddev1 > 1.0
    
    is_buy_by_vwap = price1 < vwap1
    is_sell_by_vwap = price1 > vwap1
    
    is_close_by_stdev = stddev1 < 0.05 and stddev2 < 0.05
    is_close_by_loss = context.portfolio.pnl > 100
    is_close_by_pnl = (pnl - high_pnl) < 10     
          
    # Place orders
    if is_neutral:            
        # open position
        if is_stdev_trade and is_sell_by_diff and is_sell_by_vwap:
            # Go short
            order(sid1, -trade_size)
            order(sid2, trade_size)
            context.high_pnl = 0
        elif is_stdev_trade and is_buy_by_diff and is_buy_by_vwap:
            # # Go long
            order(sid1, trade_size)
            order(sid2, -trade_size)
            context.high_pnl = 0
            
    elif is_long:       
        
        if is_close_by_stdev and (is_close_by_pnl or is_close_by_loss):
            # Close position
            order(sid1, -trade_size)
            order(sid2, trade_size)
            
        elif is_stdev_trade and is_sell_by_diff and is_sell_by_vwap:
            # Take profit by closing long
            order(sid1, -trade_size)
            order(sid2, trade_size)
            
    elif is_short:
        
        if is_close_by_stdev and (is_close_by_pnl or is_close_by_loss):
            # Take profit by closing short.
            order(sid1, trade_size)
            order(sid2, -trade_size)
            
        elif is_stdev_trade and is_buy_by_diff and is_buy_by_vwap:
            # Take profit by closing short.
            order(sid1, trade_size)
            order(sid2, -trade_size)
   
               
    # Up to 5
    # record(diff1 = diff1)
    record(price1 = price1)
    record(fairPriceOf1 = fairPriceOf1)
        
        
        
        