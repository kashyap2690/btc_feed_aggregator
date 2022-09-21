from itertools import islice
import grpc
import BinanceOrderBook_pb2_grpc as pb2_grpc
import BinanceOrderBook_pb2 as pb2
from flask import Flask, request, Response
from flask_restx import Api, Resource
import os

# parameterized gRPC client that can be used to communicate with both the services. binance & ftx
class OrderBookClient(object):
    """
    Client for gRPC functionality
    """

    def __init__(self, host, port):
        print(host)
        self.host = host
        self.server_port = port

        # instantiate a channel
        self.channel = grpc.insecure_channel(
            '{}:{}'.format(self.host, self.server_port))

        # bind the client and the server
        self.stub = pb2_grpc.BTCOrderBookServiceStub(self.channel)

    def get_orderbook(self, depth):
        """
        Client function to call the rpc for GetBTCFullOrderBook
        """
        req = pb2.OrderBookRequest(depth=depth)
        print(f'{req}')
        return self.stub.GetBTCFullOrderBook(req)

app = Flask(__name__)
api = Api(app)

binanceOrderBookClient = OrderBookClient(os.getenv("BINANCE_FEED_HOST", "localhost"), 50051)
ftxOrderBookClient = OrderBookClient(os.getenv("FTX_FEED_HOST", "localhost"), 50052)

def sortFloat(price):
    return float(price)

# REST API for calculate buy and sell price of provided qty on aggregated orderbook
@api.route("/calculate", methods=['GET'])
class Calculate(Resource):

    def get(self):
        print("Request Arrived.")
        args = request.args
        side = args.get("side", default="", type=str)
        size = args.get("size", default=10, type=int)

        if side != "buy" and side != "sell":
            return {
                "error": "Invalid side provided, pass 'buy' or 'sell' as side.."
            }
        binanceOrderBook = binanceOrderBookClient.get_orderbook(depth=100)
        ftxOrderBook = ftxOrderBookClient.get_orderbook(depth=100)
        binanceQty = 0
        ftxQty = 0
        executionPrice = 0
        idxBinance = 0
        idxFtx = 0
        if side == "buy":
            binanceAskPrices = list(islice(sorted(binanceOrderBook.asks.keys(), key=sortFloat), 100))
            ftxAskPrices = list(islice(sorted(ftxOrderBook.asks.keys(), key=sortFloat), 100))
            lenBinance = len(binanceAskPrices)
            lenFtx = len(ftxAskPrices)
            # Check both orderbook asks for finding best qtys
            while idxBinance < lenBinance or idxFtx < lenFtx:
                if idxBinance < lenBinance and (idxFtx == lenFtx or float(binanceAskPrices[idxBinance]) < float(ftxAskPrices[idxFtx])):
                    qty = min(float(binanceOrderBook.asks[binanceAskPrices[idxBinance]]), size)
                    binanceQty = binanceQty + qty
                    executionPrice = executionPrice + qty * float(binanceAskPrices[idxBinance])
                    size = size - qty
                    idxBinance = idxBinance+1
                elif idxFtx < lenFtx:
                    qty = min( float(ftxOrderBook.asks[ftxAskPrices[idxFtx]]), size)
                    ftxQty = ftxQty + qty
                    size = size - qty
                    executionPrice = executionPrice + qty * float(ftxAskPrices[idxFtx])
                    idxFtx = idxFtx+1
                if size == 0:
                    break
            return {
                "executionPrice" : executionPrice / (ftxQty + binanceQty),
                "sizeBinance": binanceQty,
                "sizeFtx": ftxQty
            }
        elif side == "sell":
            binanceBidPrices = list(islice(sorted(binanceOrderBook.bids.keys(), reverse=True, key=sortFloat), 100))
            ftxBidPrices = list(islice(sorted(ftxOrderBook.bids.keys(), reverse=True, key=sortFloat), 100))
            lenBinance = len(binanceBidPrices)
            lenFtx = len(ftxBidPrices)
            # Check both orderbook bids for finding best qtys
            while idxBinance < lenBinance or idxFtx < lenFtx:
                if idxBinance < lenBinance and (idxFtx == lenFtx or float(binanceBidPrices[idxBinance]) > float(ftxBidPrices[idxFtx])):
                    qty = min(float(binanceOrderBook.bids[binanceBidPrices[idxBinance]]), size)
                    binanceQty = binanceQty + qty
                    executionPrice = executionPrice + qty * float(binanceBidPrices[idxBinance])
                    size = size - qty
                    idxBinance = idxBinance+1
                elif idxFtx < lenFtx:
                    qty = min(float(ftxOrderBook.bids[ftxBidPrices[idxFtx]]), size)
                    ftxQty = ftxQty + qty
                    executionPrice = executionPrice + qty * float(ftxBidPrices[idxFtx])
                    size = size - qty
                    idxFtx = idxFtx+1
                if size == 0:
                    break
            return {
                "executionPrice" : executionPrice / (ftxQty + binanceQty),
                "sizeBinance": binanceQty,
                "sizeFtx": ftxQty
            }
       
# HTML formating for the aggregated orderbook
def generateHtml(bids, asks):
    strHTML = "<table>"
    strHTML += "<tr><td>|---------Exchange--------|</td><td>|---------Bid Price---------|</td><td>|---------Qty---------|</td></tr>"
    for b in bids:
        strHTML += "<tr> <td>"+b[0]+"</td><td>" + b[1] + "</td><td>" + b[2] + "</td></tr>"
    strHTML += "</table></br></br>"
    strHTML += "<table>"
    strHTML += "<tr><td>|---------Exchange--------|</td><td>|---------Ask Price---------|</td><td>|---------Qty---------|</td></tr>"
    for b in asks:
        strHTML += "<tr> <td>"+b[0]+"</td><td>" + b[1] + "</td><td>" + b[2] + "</td></tr>"
    strHTML += "</table>"
    return strHTML

# REST API for orderbook which takes size as optional
@api.route("/order_book", methods=['GET'])
class OrderBook(Resource):
    def get(self):
        binanceOrderBook = binanceOrderBookClient.get_orderbook(depth=100)
        ftxOrderBook = ftxOrderBookClient.get_orderbook(depth=100)
        args = request.args
        size = args.get("size", default=10, type=int)
        bestBids = []
        bestAsks = []

        # aggregate bids
        binanceBidPrices = list(islice(sorted(binanceOrderBook.bids.keys(), reverse=True, key=sortFloat), 100))
        ftxBidPrices = list(islice(sorted(ftxOrderBook.bids.keys(), reverse=True, key=sortFloat), 100))
        lenBinance = len(binanceBidPrices)
        lenFtx = len(ftxBidPrices)
        idxBinance = 0
        idxFtx = 0
        # Check both orderbook bids for finding best bids
        while len(bestBids) < size and (idxBinance < lenBinance or idxFtx < lenFtx):
            if idxBinance < lenBinance and (idxFtx == lenFtx or float(binanceBidPrices[idxBinance]) > float(ftxBidPrices[idxFtx])):
                bestBids.append(['binance', binanceBidPrices[idxBinance], binanceOrderBook.bids[binanceBidPrices[idxBinance]]])
                idxBinance = idxBinance+1
            elif idxFtx < lenFtx:
                bestBids.append(['ftx', ftxBidPrices[idxFtx], ftxOrderBook.bids[ftxBidPrices[idxFtx]]])
                idxFtx = idxFtx+1
        
        # aggregate asks
        binanceAskPrices = list(islice(sorted(binanceOrderBook.asks.keys(), key=sortFloat), 100))
        ftxAsksPrices = list(islice(sorted(ftxOrderBook.asks.keys(), key=sortFloat), 100))
        lenBinance = len(binanceAskPrices)
        lenFtx = len(ftxAsksPrices)
        idxBinance = 0
        idxFtx = 0
        # Check both orderbook bids for finding best bids
        while len(bestAsks) < size and (idxBinance < lenBinance or idxFtx < lenFtx):
            if idxBinance < lenBinance and (idxFtx == lenFtx or float(binanceAskPrices[idxBinance]) < float(ftxAsksPrices[idxFtx])):
                bestAsks.append(['binance', binanceAskPrices[idxBinance], binanceOrderBook.asks[binanceAskPrices[idxBinance]]])
                idxBinance = idxBinance+1
            elif idxFtx < lenFtx:
                bestAsks.append(['ftx', ftxAsksPrices[idxFtx], ftxOrderBook.asks[ftxAsksPrices[idxFtx]]])
                idxFtx = idxFtx+1
        return Response(generateHtml(bestBids, bestAsks), mimetype='text/html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")