from time import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import msgpack_lz4block
import msgpack
import lz4.block
import ssl
import certifi
import socket
import requests
import base64
import h2.connection
import h2.events
import struct
import os
from hashlib import md5
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms


class Model:
    def __init__(self):
        pass

    @staticmethod
    def readTo(data, sew=None):
        vals = sew

        def _get(_d):
            return _d[0], _d[1]

        def _read(_d, _s):
            _newdata = {}
            vals = _s
            if _d is None:
                return None
            if len(vals) == 1 and isinstance(vals[0], list):
                _v = vals[0]
                _newdata = []
                for d in _d:
                    d = _read(d, _v)
                    _newdata.append(d)
            else:
                index = 0
                for d in _d:
                    if index < len(vals):
                        if isinstance(vals[index], list):
                            _k, _v = _get(vals[index])
                            d = _read(d, _v)
                        else:
                            _k, _v = vals[index], None
                        _newdata[_k] = d
                    index += 1
            return _newdata

        if sew is not None and len(sew) > 0:
            newdata = _read(data, sew)
            return newdata
        return data


class ApiStatusError(Exception):
    def __init__(self, code):
        self.code = code

        super().__init__(f"ApiStatusCode: {self.code}")
