# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: BinanceOrderBook.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16\x42inanceOrderBook.proto\x12\x0c\x62tcorderbook\"!\n\x10OrderBookRequest\x12\r\n\x05\x64\x65pth\x18\x01 \x01(\x05\"\xdf\x01\n\x11OrderBookResponse\x12\x37\n\x04\x62ids\x18\x01 \x03(\x0b\x32).btcorderbook.OrderBookResponse.BidsEntry\x12\x37\n\x04\x61sks\x18\x02 \x03(\x0b\x32).btcorderbook.OrderBookResponse.AsksEntry\x1a+\n\tBidsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a+\n\tAsksEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x32o\n\x13\x42TCOrderBookService\x12X\n\x13GetBTCFullOrderBook\x12\x1e.btcorderbook.OrderBookRequest\x1a\x1f.btcorderbook.OrderBookResponse\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'BinanceOrderBook_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ORDERBOOKRESPONSE_BIDSENTRY._options = None
  _ORDERBOOKRESPONSE_BIDSENTRY._serialized_options = b'8\001'
  _ORDERBOOKRESPONSE_ASKSENTRY._options = None
  _ORDERBOOKRESPONSE_ASKSENTRY._serialized_options = b'8\001'
  _ORDERBOOKREQUEST._serialized_start=40
  _ORDERBOOKREQUEST._serialized_end=73
  _ORDERBOOKRESPONSE._serialized_start=76
  _ORDERBOOKRESPONSE._serialized_end=299
  _ORDERBOOKRESPONSE_BIDSENTRY._serialized_start=211
  _ORDERBOOKRESPONSE_BIDSENTRY._serialized_end=254
  _ORDERBOOKRESPONSE_ASKSENTRY._serialized_start=256
  _ORDERBOOKRESPONSE_ASKSENTRY._serialized_end=299
  _BTCORDERBOOKSERVICE._serialized_start=301
  _BTCORDERBOOKSERVICE._serialized_end=412
# @@protoc_insertion_point(module_scope)
