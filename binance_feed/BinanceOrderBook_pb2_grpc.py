# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import BinanceOrderBook_pb2 as BinanceOrderBook__pb2


class BTCOrderBookServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetBTCFullOrderBook = channel.unary_unary(
                '/btcorderbook.BTCOrderBookService/GetBTCFullOrderBook',
                request_serializer=BinanceOrderBook__pb2.OrderBookRequest.SerializeToString,
                response_deserializer=BinanceOrderBook__pb2.OrderBookResponse.FromString,
                )


class BTCOrderBookServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetBTCFullOrderBook(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BTCOrderBookServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetBTCFullOrderBook': grpc.unary_unary_rpc_method_handler(
                    servicer.GetBTCFullOrderBook,
                    request_deserializer=BinanceOrderBook__pb2.OrderBookRequest.FromString,
                    response_serializer=BinanceOrderBook__pb2.OrderBookResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'btcorderbook.BTCOrderBookService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BTCOrderBookService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetBTCFullOrderBook(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/btcorderbook.BTCOrderBookService/GetBTCFullOrderBook',
            BinanceOrderBook__pb2.OrderBookRequest.SerializeToString,
            BinanceOrderBook__pb2.OrderBookResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
