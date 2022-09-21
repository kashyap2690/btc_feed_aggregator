FROM python:3.8-alpine
RUN apk add --update --no-cache \
    gcc \
    linux-headers \
    make \
    musl-dev \
    g++ 
RUN python -m pip install --upgrade pip
RUN mkdir service
COPY protobufs service/protobufs
COPY btc_feed_aggregator service/btc_feed_aggregator
WORKDIR service/btc_feed_aggregator
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/BinanceOrderBook.proto

EXPOSE 5000
ENTRYPOINT [ "python", "BtcFeedAggregator.py" ]
