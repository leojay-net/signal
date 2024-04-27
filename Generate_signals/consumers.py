import pandas as pd
import vectorbt as vbt
import pandas_ta as ta
import datetime
import time
import MetaTrader5 as mt5
#from mt5linux import MetaTrader5
import json
from channels.generic.websocket import WebsocketConsumer


class PremiumCheckConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()


    def disconnect(self, message):
        pass


    def receive(self):
        if not mt5.initialize():
            self.send(data=json.dumps({'message': f"initialize() failed, error code = {mt5.last_error()}"}))
            quit()


        symbol = "XAUUSD"

        while True:
            print("Getting data in progress...")
            # Get the latest data
            bars = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.set_index('time')
            current_price = df['close'].iloc[-1]

            # Calculate indicators
            print("Calculating indicators in progress...")
            ma14 = vbt.MA.run(df['close'], 14)
            ma50 = vbt.MA.run(df['close'], 50)
            ma365 = vbt.MA.run(df['close'], 365)
            rsi = vbt.RSI.run(df['close'], 14)
            
            # Check the conditions for the last bar
            print("Checking conditions in progress...\n")
            if (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40):
                self.send(data=json.dumps({'condition':'BUY',
                                'RSI':rsi.rsi.iloc[-1],
                                '14 SMA': ma14.ma.iloc[-1],
                                'Current Price': current_price
                                }))
                print("Buy condition met:")
                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (below 40)")
                print(f"14 SMA: {ma14.ma.iloc[-1]:.5f} (above 50 SMA and 50 SMA > 365 SMA)")
                print(f"Current price: {current_price:.5f}")
                print("-" * 30)
            
            elif (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 60):
                self.send(data=json.dumps({'condition':'SELL',
                                            'RSI':rsi.rsi.iloc[-1],
                                            '14 SMA': ma14.ma.iloc[-1],
                                            'Current Price': current_price
                                            }))
                print("Sell condition met:")
                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (above 60)")
                print(f"14 SMA: {ma14.ma.iloc[-1]:.5f} (below 50 SMA and 50 SMA < 365 SMA)")
                print(f"Current price: {current_price:.5f}")
                print("-" * 30)

            time.sleep(5)  # wait for 60 seconds




class FreeCheckConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()


    def disconnect(self, message):
        pass


    def receive(self, text_data):
        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()
        symbol = 'XAUUSD'  # or any other valid symbol
        symbol_info = mt5.symbol_info(symbol)

        while True:
            print("Getting data in progress...")
            # Get the latest data
            bars = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.set_index('time')

            # Calculate RSI
            rsi = vbt.RSI.run(df['close'], 14)
            
            # Check buy condition
            buy_condition = rsi.rsi > 78
            
            # Check sell condition
            sell_condition = rsi.rsi < 22

            
            if buy_condition.iloc[-1]:
                print("Buy condition met:")
                current_price = df['close'].iloc[-1]
                stop_loss = current_price - 1000 * symbol_info.point
                take_profit = current_price + 1500* symbol_info.point
                self.send(text_data=json.dumps({'condition':'BUY',
                                            'RSI':rsi.rsi.iloc[-1],
                                            'Current Price': current_price,
                                            'SL': stop_loss,
                                            'TP': take_profit
                                            }))
                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (above 78)")
                print(f"Current price: {current_price:.5f}")
                print(f"Stop loss: {stop_loss:.5f}")
                print(f"Take profit: {take_profit:.5f}")
                print("-" * 30)
            
            if sell_condition.iloc[-1]:
                print("Sell condition met:")
                current_price = df['close'].iloc[-1]
                stop_loss = current_price + 1500 * symbol_info.point
                take_profit = current_price - 1000* symbol_info.point
                self.send(data=json.dumps({'condition':'SELL',
                                            'RSI':rsi.rsi.iloc[-1],
                                            'Current Price': current_price,
                                            'SL': stop_loss,
                                            'TP': take_profit
                                            }))

                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (below 22)")
                print(f"Current price: {current_price:.5f}")
                print(f"Stop loss: {stop_loss:.5f}")
                print(f"Take profit: {take_profit:.5f}")
                print("-" * 30)

            time.sleep(60)  # wait for 60 seconds
