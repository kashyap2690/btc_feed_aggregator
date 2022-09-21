import asyncio
import websockets
import json
from itertools import islice
import threading
import grpc
import BinanceOrderBook_pb2_grpc as pb2_grpc
import BinanceOrderBook_pb2 as pb2
from concurrent import futures
from datetime import datetime, timedelta

DEBUG=False
FTX_BTC_PAIR = "BTC/USD"
FTX_BTCUSD_SOCKET_URL = "wss://ftx.com/ws/" 

ftx_orderbook = {"bids":{}, "asks":{}}
orderbook_lock = threading.Lock()

ping = {'op': 'ping'}
subscription_req = {'op': 'subscribe', 'channel': 'orderbook', 'market': FTX_BTC_PAIR}
last_ping_time = datetime.now()

# connection to FTX websockets for live orderfeed
async def connectToFtxWebSocket(uri):
    global last_ping_time
    async for websocket in websockets.connect(uri):
        try:
            #  Send subscription event for BTC-USDT
            await websocket.send(json.dumps(subscription_req))
            async for message in websocket:
                await processFtxMessage(message)
                if datetime.now() >= last_ping_time + timedelta(seconds = 15):
                    await websocket.send(json.dumps(ping))
                    last_ping_time = datetime.now()
        except websockets.ConnectionClosed:
            continue

# ws message processing for full orderbook and update in orderbook.
async def processFtxMessage(message):
    if DEBUG:
        print(message)
    global bids_sorted
    global asks_sorted

    msg = json.loads(message)
    if msg.get("type") != None and (msg["type"] == "partial" or msg["type"] == "update" ):
        orderbook_lock.acquire()
        if msg["type"] == "partial":
            ftx_orderbook["bids"] = {}
            ftx_orderbook["asks"] = {}
        for row in msg["data"]["bids"]:
            if float(row[1]) == 0 and ftx_orderbook["bids"].get(row[0]) != None:
                del ftx_orderbook["bids"][row[0]]
            elif float(row[1]) != 0:
                ftx_orderbook["bids"][row[0]] = row[1]
            else:
                if DEBUG:
                    print(row)
        for row in msg["data"]["asks"]:
            if float(row[1]) == 0 and ftx_orderbook["asks"].get(row[0]) != None:
                del ftx_orderbook["asks"][row[0]]
            elif float(row[1]) != 0:
                ftx_orderbook["asks"][row[0]] = row[1]
            else:
                if DEBUG:
                    print(row)
        if DEBUG:
            print("--------------------------------")
        iterator = islice(sorted(ftx_orderbook["bids"].keys(), reverse=True), 10)
        if DEBUG:
            for key in iterator:
                print('{0} {1}'.format(key, ftx_orderbook["bids"][key]))
            print("\n")
        
        iterator = islice(sorted(ftx_orderbook["asks"].keys()), 10)
        if DEBUG:
            for key in iterator:
                print('{0} {1}'.format(key, ftx_orderbook["asks"][key]))
            print("--------------------------------")
        orderbook_lock.release()

def FTXWsThread():
    asyncio.run(connectToFtxWebSocket(FTX_BTCUSD_SOCKET_URL))

# Service class for gRPC service request handling
class BinanceOrderBookService(pb2_grpc.BTCOrderBookService):
    def __init__(self, *args, **kwargs):
        pass

    def GetBTCFullOrderBook(self, request, context):

        # get the depth from the incoming request
        depth = request.depth
        orderbook_lock.acquire()
        
        bidsRes = {}
        asksRes = {}
        iterator = islice(sorted(ftx_orderbook["bids"].keys(), reverse=True), depth)
        for bid in iterator:
            bidsRes[str(bid)] = str(ftx_orderbook["bids"][bid])
        iterator = islice(sorted(ftx_orderbook["asks"].keys()), depth)
        for ask in iterator:
            asksRes[str(ask)] = str(ftx_orderbook["asks"][ask])

        orderbook_lock.release()
        return pb2.OrderBookResponse(bids=bidsRes, asks=asksRes)
        
# gRPC server 
def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  pb2_grpc.add_BTCOrderBookServiceServicer_to_server(
      BinanceOrderBookService(), server)
  server.add_insecure_port('[::]:50052')
  server.start()
  server.wait_for_termination()

async def main():
    thread1 = threading.Thread(target = FTXWsThread, args=())
    thread1.start()

    thread2 = threading.Thread(target = serve, args=())
    thread2.start()
   
    thread1.join()
    thread2.join()

if __name__ == '__main__':
    
    asyncio.run(main()) # creats an envent loop