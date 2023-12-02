import msgpack
import requests
import lz4.block
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from ctypes import c_longlong as ll
from ctypes import c_ulonglong as ull
import subprocess
import os


class Object:
    def __init__(self):
        pass

    def DecodeEncData(self, data, raw=False):
        KEY = b""  # HEX e4ca7bf2...dc9891 to bytes.
        if KEY == b"":
            raise NotImplementedError
        cipher = AES.new(KEY, AES.MODE_CBC, data[:16])
        d = cipher.decrypt(data[16:])
        d = unpad(d, 16)
        if raw:
            return d
        _unpack = msgpack.unpackb(d, strict_map_key=False, use_list=False, timestamp=1)
        if isinstance(_unpack, msgpack.ExtType):
            if _unpack.code == 99:
                data = _unpack.data
                msgpack_code = data[0]
                size = int.from_bytes(data[1:5], byteorder="big", signed=True)
                data = data[5:]
                data = lz4.block.decompress(data, size)
                _unpack = msgpack.unpackb(
                    data, strict_map_key=False, use_list=False, timestamp=1
                )
            else:
                raise ValueError("cant decode")
        return _unpack

    def GetRealAssetData(self, name, file_ext=".msgpack", isPlain=False):
        hash = self.getCacheServerRevisionHash(self.region)
        if self.ResourceBaseUrl is None or len(self.ResourceBaseUrl) == 0:
            raise NotImplementedError()
        url = f"{self.ResourceBaseUrl}/{hash}/{name}{file_ext}.enc"
        if isPlain:
            url = url[:-4]
        res = requests.get(url)
        if res.status_code != 200:
            raise EOFError(f"resp not 200")
        return res.content

    @staticmethod
    def MusicEncryptLogic__GetRound(y):
        return (y & 0xF) + ((y >> 15) & 0xF) + 15

    @staticmethod
    def MusicEncryptLogic__Xorshift(x, round):
        result = ull(x).value
        if round >= 1:
            v2 = round + 1
            while v2 > 1:
                v2 -= 1
                v3 = result ^ (result << 16) ^ ((result ^ ull(result << 16).value) >> 5)
                result = ull(v3 ^ (v3 << 17)).value
        return str(hex(result))
