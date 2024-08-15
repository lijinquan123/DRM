# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/11/23 12:25
# @Version     : Python 3.12.2


class DRMKeysException(Exception):
    """获取DRM秘钥异常"""

    def __init__(self, reason: str = None):
        self.message = type(self).__name__
        self.reason = reason
        super().__init__(self.__dict__)


class DeviceError(DRMKeysException):
    """设备错误"""


class UnsupportedDeviceError(DeviceError):
    """不被支持的设备错误"""


class LicenseError(DRMKeysException):
    """许可证错误"""


class LicenseSignatureUnmatchedError(LicenseError):
    """许可证摘要不匹配错误"""


class PSSHParseError(DRMKeysException):
    """PSSH解析错误"""


class InitDataParseError(PSSHParseError):
    """解析初始数据错误"""
