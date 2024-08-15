# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/12/7 19:33
# @Version     : Python 3.12.2
import os
import random

from dataclasses import dataclass

from DRM.exceptions import *


@dataclass
class Device(object):
    name: str = 'widevine_default'
    type: str = 'android'
    # 许可证是否在设备离线状态下获取的
    is_offline: bool = False
    security_level: int = 3

    @property
    def request_id(self) -> bytes:
        """获取随机的会话ID"""
        if self.type == 'android':
            # format: 16 random hexdigits, 2 digit counter, 14 '0'
            rand_ascii = ''.join(random.sample("0123456789ABCDEF", 16)).encode('utf-8')
            counter = b'01'  # this resets regularly so its fine to use 01
            rest = b'00000000000000'
            request_id = rand_ascii + counter + rest
        elif self.type == 'chrome':
            request_id = os.urandom(16)
        else:
            raise UnsupportedDeviceError(self.type)
        return request_id


@dataclass
class LicenseRequest(object):
    raw: bytes
    msg: bytes


@dataclass
class Key(object):
    kid: str
    type: str
    key: str
    permissions: list = None


class Keys(list):
    def todict(self) -> dict:
        keys = {}
        for key in self:
            if key.type == 'CONTENT':
                keys[key.kid] = key.key
        return keys

    def tolist(self) -> list:
        keys = []
        for kid, key in self.todict().items():
            keys.append(f'{kid}:{key}')
        return keys
