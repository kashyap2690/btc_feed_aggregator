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
COPY binance_feed service/binance_feed
WORKDIR service/binance_feed
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt
RUN python -m grpc_tools.protoc -I ../protobufs --python_out=. --grpc_python_out=. ../protobufs/BinanceOrderBook.proto

EXPOSE 50051
ENTRYPOINT [ "python", "BinanceFeedService.py" ]
