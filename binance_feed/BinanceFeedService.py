import asyncio
import websockets
from urllib.request import urlopen
import json
from itertools import islice
import threading
import grpc
import BinanceOrderBook_pb2_grpc as pb2_grpc
import BinanceOrderBook_pb2 as pb2
from concurrent import futures

DEBUG=False
BINANCE_BTC_PAIR = "BTCBUSD"
BINANCE_BTCUSD_SOCKET_URL = "wss://stream.binance.com:9443/ws/{}@depth@100ms".format(BINANCE_BTC_PAIR.lower()) # Diff events in Orderbook Depth
BINANCE_DEPTH_SNAPSHOT = "https://api.binance.com/api/v3/depth?symbol={}&limit=1000".format(BINANCE_BTC_PAIR)

binance_orderbook = {"bids":{}, "asks":{}}
orderbook_lock = threading.Lock()

# subscribe to binance ws for continous diff events in orderbook
async def connectToBinanceDiffEvents(uri):
    print("Subscribe to websocket.")
    async for websocket in websockets.connect(uri):
        try:
            async for message in websocket:
                await processBinanceMessage(message)
        except websockets.ConnectionClosed:
            continue

def sortFloat(price):
    return float(price)

msgs = []
bids_sorted = []
asks_sprted = []

# process diff messages of the binance ws
async def processBinanceMessage(message):
    global bids_sorted
    global asks_sorted

    curmsg = json.loads(message)
    # enqueue the messages till we have snapshot ready for further processing.
    # This also triggers downloading for snapshot.
    msgs.append(curmsg)
    if binance_orderbook.get("lastUpdateId") != None and binance_orderbook["lastUpdateId"] > 0 :
        if DEBUG:
            print(len(msgs))
        # Lock just to make sure underprocess orderbook is never shared with gRPC clients.
        orderbook_lock.acquire()
        for msg in msgs:
            msgs.remove(msg)
            if msg["e"] == "depthUpdate" and msg["u"] >= binance_orderbook["lastUpdateId"]:
                for row in msg["b"]:
                    if float(row[1]) == 0 and binance_orderbook["bids"].get(row[0]) != None:
                        del binance_orderbook["bids"][row[0]]
                    elif float(row[1]) != 0:
                        binance_orderbook["bids"][row[0]] = row[1]
                    else:
                        if DEBUG:
                            print(row)
                for row in msg["a"]:
                    if float(row[1]) == 0 and binance_orderbook["asks"].get(row[0]) != None:
                        del binance_orderbook["asks"][row[0]]
                    elif float(row[1]) != 0:
                        binance_orderbook["asks"][row[0]] = row[1]
                    else:
                        if DEBUG:
                            print(row)
            if DEBUG:
                print("--------------------------------")
            bids_sorted = islice(sorted(binance_orderbook["bids"].keys(), reverse=True, key=sortFloat), 10)
            if DEBUG:
                for key in bids_sorted:
                    print('{0} {1}'.format(key, binance_orderbook["bids"][key]))
                print("\n")
            
            asks_sorted = islice(sorted(binance_orderbook["asks"].keys(), key=sortFloat), 10)
            if DEBUG:
                for key in asks_sorted:
                    print('{0} {1}'.format(key, binance_orderbook["asks"][key]))
                print("--------------------------------")
        orderbook_lock.release()

# Fetch the binance full orderbook
async def fetchBinanceLatestDepthSnapshot(url):
    print("\n\n\n Fetching Snapshot")
    response = urlopen(url)
    bo = json.loads(response.read())
    for row in bo["bids"]:
        binance_orderbook["bids"][row[0]] = row[1]
    for row in bo["asks"]:
        binance_orderbook["asks"][row[0]] = row[1]
    binance_orderbook["lastUpdateId"] = bo["lastUpdateId"]
    if DEBUG:
        print(binance_orderbook)
        

def binanceWsThread():
    binance_diff = asyncio.run(connectToBinanceDiffEvents(BINANCE_BTCUSD_SOCKET_URL))

def binanceSnapshotAPIThread():
    binance_snapshot = asyncio.run(fetchBinanceLatestDepthSnapshot(BINANCE_DEPTH_SNAPSHOT))
    serve()

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
        iterator = islice(sorted(binance_orderbook["bids"].keys(), reverse=True, key=sortFloat), depth)
        for bid in iterator:
            bidsRes[bid] = binance_orderbook["bids"][bid]
        iterator = islice(sorted(binance_orderbook["asks"].keys(), key=sortFloat), depth)
        for ask in iterator:
            asksRes[ask] = binance_orderbook["asks"][ask]
        orderbook_lock.release()
        return pb2.OrderBookResponse(bids=bidsRes, asks=asksRes)
        
# gRPC server 
def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  pb2_grpc.add_BTCOrderBookServiceServicer_to_server(
      BinanceOrderBookService(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()

async def main():
    thread1 = threading.Thread(target = binanceWsThread, args=())
    thread1.start()

    # Wait for the binance ws feed to be started, it first needs to be started before we fetch a snapshot.
    # to makesure we don't miss any diff events of orderbook
    while True:
        if len(msgs):
            thread2 = threading.Thread(target = binanceSnapshotAPIThread, args=())
            thread2.start()
            break

    thread1.join()
    thread2.join()

if __name__ == '__main__':
    asyncio.run(main()) # creats an envent loop