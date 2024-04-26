# API keys have been changed for demonstration
import config, requests, json # type: ignore
from datetime import datetime, timedelta # type: ignore
from alpaca.trading.client import TradingClient # type: ignore
from alpaca.trading.requests import MarketOrderRequest # type: ignore
from alpaca.trading.enums import OrderSide, TimeInForce # type: ignore
from alpaca.data.live import StockDataStream # type: ignore
from alpaca.data import StockHistoricalDataClient, StockTradesRequest
import btalib # type: ignore
import pandas as pd # type: ignore
import pytz         # type: ignore

# Set up pandas and trading client
pd.set_option('display.max_rows', None) 
pd.set_option('display.max_columns', None) 
pd.set_option('display.width', None)  
pd.set_option('display.max_colwidth', None)  
trading_client = TradingClient (config.API_KEY, config.SECRET_KEY)

def calc_NAS_stats():
    for stock in config.NAS_STOCKS:
        bars_url = "https://data.alpaca.markets/v2/stocks/bars?symbols=%s&timeframe=1Day&limit=500&start=%s" % (stock, (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'))
        response = requests.get(bars_url, headers=config.HEADERS)

        filename = 'data/ohlc/{}.txt'.format(stock)
        f = open(filename, 'w+')
        f.write('Date,Open,High,Low,Close,Volume,OpenInterest\n')
        for bar in response.json()['bars'][stock]:
            line = '{},{},{},{},{},{},{}\n'.format(bar['t'][0:10], bar['o'], bar['h'], bar['l'], bar['c'], bar['v'], 0.00)
            f.write(line)

def trade_NAS():
    calc_NAS_stats()
    for stock in config.NAS_STOCKS:
        df = pd.read_csv('data/ohlc/%s.txt' % stock, parse_dates=True, index_col='Date')
        sma = btalib.sma(df, period=200)
        rsi = btalib.rsi(df)
        df['sma'] = sma.df
        df['rsi'] = rsi.df
        oversold_days = df[df['rsi'] < 30]
        # print(oversold_days)
        overbought_days = df[df['rsi'] > 70]
        # print(overbought_days)

        macd = btalib.macd(df)
        df['macd'] = macd.df['macd']
        df['signal'] = macd.df['signal']
        df['histogram'] = macd.df[ 'histogram']
        last_row = df.tail(1)
        current_signal = last_row.iloc[0]['signal']
        current_macd = last_row.iloc[0]['macd']
        current_rsi = last_row.iloc[0]['rsi']

        if (((current_macd > current_signal and current_signal < 0) and df.tail(1).iloc[0]['sma'] / df.tail(51).iloc[0]['sma'] >= 1) or current_rsi > 80):
            print("%s: buy" % stock)
            market_order_data = MarketOrderRequest(
                symbol=stock,
                qty=1,
                side=OrderSide.BUY, 
                time_in_force=TimeInForce.DAY
            )
            trading_client.submit_order(market_order_data)
        else:
            if (current_rsi < 30):
                print("%s: sell" % stock)
            else:
                if (current_rsi > 60 or df.tail(1).iloc[0]['sma'] / df.tail(51).iloc[0]['sma'] >= 1):
                    print("%s: hold" % stock)
                else:
                    print("%s: sell" % stock)
                    positions = trading_client.get_all_positions()
                    position = next((p for p in positions if p.symbol == stock), None)
                    if position and float(position.qty) > 0:
                        sell_order = MarketOrderRequest(
                            symbol=stock,
                            qty=position.qty,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.DAY
                        )
                        trading_client.submit_order(sell_order)

trade_NAS()


# def get_last_market_open():
#     today = datetime.now()
#     if today.weekday() == 5:
#         last_open = today - timedelta(days=1)
#     elif today.weekday() == 6:
#         last_open = today - timedelta(days=2)
#     else:
#         last_open = today
    
#     return last_open.strftime('%Y-%m-%d')

# def live_stock_updates(stock):
#     stream = StockDataStream("PKKDOP37NUG6VDUEUAF2", "EMrBxVS2QcvqUJv6IxqJrNggKfIQnFRxim2HWxa9")
#     async def handle_trade(data):
#         print(data)

#     stream.subscribe_quotes(handle_trade, stock)
#     stream.run()



# def get_last_market_open_utc_time():
#     # Set the timezone to UTC
#     utc = pytz.timezone("UTC")
#     now = datetime.now(utc)
    

#     if now.weekday() < 5 and now.time() < datetime.strptime("21:00", "%H:%M").time():
       
#         last_open = now
#     else:
       
#         days_behind = (now.weekday() - 4) % 7
#         if days_behind == 0 and now.time() >= datetime.strptime("21:00", "%H:%M").time():

#             last_open = now.replace(hour=21, minute=0, second=0, microsecond=0)
#         else:

#             last_friday = now - timedelta(days=days_behind + 1)
#             last_open = last_friday.replace(hour=21, minute=0, second=0, microsecond=0)
    
#     return last_open

# def get_trades(stock, s=get_last_market_open_utc_time() - timedelta(hours=1), e=get_last_market_open_utc_time()):
#     last_market_open_utc = get_last_market_open_utc_time()

#     data_client = StockHistoricalDataClient("PKKDOP37NUG6VDUEUAF2", "EMrBxVS2QcvqUJv6IxqJrNggKfIQnFRxim2HWxa9")
#     request_params_now = StockTradesRequest(
#         symbol_or_symbols = stock,
#         start = s, #utc year, month, day, military time hour, minute
#         end = e
#     )

#     pnow = data_client.get_stock_trades(request_params_now).data[stock]

#     def get_buy_vs_sell(pnow):
#         for p in pnow:
#             r = json.dumps(p.json(), indent=4)


#     print(pnow)



# get_trades('AAPL')






































# from alpaca.trading.client import TradingClient         # type: ignore
# from alpaca.trading.requests import GetOrdersRequest  # type: ignore
# from alpaca.trading.enums import OrderSide, QueryOrderStatus # type: ignore

# trading_client = TradingClient("PKKDOP37NUG6VDUEUAF2", "EMrBxVS2QcvqUJv6IxqJrNggKfIQnFRxim2HWxa9")

# request_params = GetOrdersRequest(
#     status = QueryOrderStatus.OPEN
# )

# orders = trading_client.get_orders(request_params)

# positions = trading_client.get_all_positions()

# for position in positions:
#     print(position.symbol, position.current_price)

# for order in orders:
#     trading_client.cancel_order_by_id(order.id)



# from alpaca.trading.client import TradingClient         # type: ignore
# from alpaca.trading.requests import LimitOrderRequest  # type: ignore
# from alpaca.trading.enums import OrderSide, TimeInForce # type: ignore

# trading_client = TradingClient("PKKDOP37NUG6VDUEUAF2", "EMrBxVS2QcvqUJv6IxqJrNggKfIQnFRxim2HWxa9")

# limit_order_data = LimitOrderRequest(
#     symbol = "SPY",
#     qty = "1",
#     side = OrderSide.BUY,
#     time_in_force = TimeInForce.DAY,
#     limit_price = 500
# )

# limit_order = trading_client.submit_order(limit_order_data)
# print(limit_order)


# from alpaca.trading.client import TradingClient         # type: ignore
# from alpaca.trading.requests import MarketOrderRequest  # type: ignore
# from alpaca.trading.enums import OrderSide, TimeInForce # type: ignore

# trading_client = TradingClient("PKKDOP37NUG6VDUEUAF2", "EMrBxVS2QcvqUJv6IxqJrNggKfIQnFRxim2HWxa9")

# market_order_data = MarketOrderRequest(
#     symbol = "SPY",
#     qty = "1",
#     side = OrderSide.BUY,
#     time_in_force = TimeInForce.DAY
# )

# trading_client.submit_order(market_order_data)

# print(trading_client.get_account().account_number)
# print(trading_client.get_account().buying_power)
