# Description

This project contains 3 services in seperate folders.
1. `binance_feed` : Parses live feeds of orderbook from binance and provide gRPC server for other services to fetch latest orderbook based on size as parameter. To update the token pair update _BINANCE_BTC_PAIR = "BTCBUSD"_  line in the _BinanceFeedService.py_ file.
1. `ftx_feed` : Parses live feeds of orderbook from ftx and provide gRPC server for other services to fetch latest orderbook based on size as parameter. To update the token pair update _FTX_BTC_PAIR = "BTC/USD"_  line in the _FTXFeedService.py_ file.
1. `btc_feed_aggregator` : Provides REST API for fetching latest aggregated order book & calculate the best buy/sell price based on current aggregated orderbook. APIs are implemented using Flask. This service communicates with above services through gRPC client.

`protobufs` folder contains _.proto_ files for the gRPC protocol buffer implementation.

# Usage

The services are bundled in a `docker-compose.yaml` so the whole environment can be brought up by following command:
```
docker-compose up
```
After all the images are built and up, you will see logs for a Flask server being up at on 5000 port 

Do any of the following set of requests to check the API response(you can use curl or browser for the same):

> http://localhost:5000/calculate?side=buy&size=10

> http://localhost:5000/calculate?side=sell&size=10

> http://localhost:5000/order_book?size=50

**Note:** If you face Internal server error immidiate after the server is up, just wait for few more seconds and try again. The binance service might take tens of seconds to warmup.

That's it!