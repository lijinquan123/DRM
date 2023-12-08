# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/11/23 11:28
# @Version     : Python 3.6.4
"""内容解密模块(Content Decryption Modules)

通过设备数据构造请求数据,请求播放许可链接
"""
import os
import random
import time

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import pss
from Crypto.Util import Padding

from DRM.widevine.formats import wv_proto2_pb2
from DRM.widevine.structs import Device, LicenseRequest


class ContentDecryptionModules(object):
    """内容解密模块(Content Decryption Modules)"""
    WV_SYSTEM_ID = [237, 239, 139, 169, 121, 214, 74, 206, 163, 200, 39, 220, 213, 29, 33, 237]

    def __init__(self, pssh: bytes, certificate: bytes = b'', cenc_data: bytes = None):
        """
        内容解密模块
        :param pssh: Protection System Specific Header
        :param certificate: 设备证书
        :param cenc_data: pssh经过WidevineCencHeader转化后的数据
        """
        # used for NF key exchange, where they don't provide a valid PSSH
        # NF 应该是指 Netfix, 参考 https://news.ycombinator.com/item?id=28025758
        self.cenc_data = cenc_data
        self.is_raw_data = bool(self.cenc_data)
        if not self.is_raw_data:
            pssh = self._normalize_pssh(pssh)
            self.cenc_data = wv_proto2_pb2.WidevineCencHeader()
            self.cenc_data.ParseFromString(pssh[32:])
        self.is_privacy_mode = bool(certificate)
        if self.is_privacy_mode:
            self.certificate = certificate

    def _normalize_pssh(self, p: bytes):
        """标准化PSSH数据"""
        if p[12:28] == bytes(self.WV_SYSTEM_ID):
            np = p
        else:
            np = bytearray([0, 0, 0])
            np.append(32 + len(p))
            np[4:] = bytearray(b'pssh')
            np[8:] = [0, 0, 0, 0]
            np[13:] = self.WV_SYSTEM_ID
            np[29:] = [0, 0, 0, 0]
            np[31] = len(p)
            np[32:] = p
        return np

    @property
    def certificate(self):
        return self._certificate

    @certificate.setter
    def certificate(self, c: bytes):
        """设置设备证书
        在隐私模式下使用"""
        message = wv_proto2_pb2.SignedMessage()
        message.ParseFromString(c)
        device_cert = wv_proto2_pb2.SignedDeviceCertificate()
        if message.Type:
            device_cert.ParseFromString(message.Msg)
        else:
            device_cert.ParseFromString(c)
        self._certificate = device_cert

    def _get_encrypted_client_id(self, client_id):
        """获取加密后的设备ID
        在隐私模式下使用,通过设备证书加密设备"""
        key = os.urandom(16)
        iv = os.urandom(16)
        encrypted_client_id = wv_proto2_pb2.EncryptedClientIdentification()
        encrypted_client_id.ServiceId = self.certificate._DeviceCertificate.ServiceId
        encrypted_client_id.ServiceCertificateSerialNumber = self.certificate._DeviceCertificate.SerialNumber
        encrypted_client_id.EncryptedClientId = AES.new(key, AES.MODE_CBC, iv).encrypt(
            Padding.pad(client_id.SerializeToString(), 16))
        encrypted_client_id.EncryptedClientIdIv = iv
        encrypted_client_id.EncryptedPrivacyKey = PKCS1_OAEP.new(
            RSA.importKey(self.certificate._DeviceCertificate.PublicKey)).encrypt(key)
        return encrypted_client_id

    def get_license_request(self, private_key: bytes, raw_client_id: bytes, device: Device = None) -> LicenseRequest:
        """获取许可链接的请求数据
        是第二次请求许可链接的请求数据,并忽略第一次的请求
        请求数据包括PSSH数据,设备数据和摘要数据
        """
        if device is None:
            device = Device()

        # PSSH数据
        if self.is_raw_data:
            license_request = wv_proto2_pb2.SignedLicenseRequestRaw()
            license_request.Type = wv_proto2_pb2.SignedLicenseRequestRaw.MessageType.Value('LICENSE_REQUEST')
            license_request.Msg.ContentId.CencId.Pssh = self.cenc_data
        else:
            license_request = wv_proto2_pb2.SignedLicenseRequest()
            license_request.Type = wv_proto2_pb2.SignedLicenseRequest.MessageType.Value('LICENSE_REQUEST')
            license_request.Msg.ContentId.CencId.Pssh.CopyFrom(self.cenc_data)

        # 设备数据
        license_request.Msg.ContentId.CencId.LicenseType = wv_proto2_pb2.LicenseType.Value(
            'OFFLINE' if device.is_offline else 'DEFAULT')
        license_request.Msg.ContentId.CencId.RequestId = device.request_id
        license_request.Msg.Type = wv_proto2_pb2.LicenseRequest.RequestType.Value('NEW')
        license_request.Msg.RequestTime = int(time.time())
        license_request.Msg.ProtocolVersion = wv_proto2_pb2.ProtocolVersion.Value('CURRENT')
        # http://www.manongjc.com/detail/61-jnoxzevelgyhmua.html
        # KeyControlNonce是一个随机数，用于防止重放攻击
        license_request.Msg.KeyControlNonce = random.randrange(1, 2 ** 31)
        client_id = wv_proto2_pb2.ClientIdentification()
        client_id.ParseFromString(raw_client_id)
        if self.is_privacy_mode:
            license_request.Msg.EncryptedClientId.CopyFrom(self._get_encrypted_client_id(client_id))
        else:
            license_request.Msg.ClientId.CopyFrom(client_id)

        # 摘要数据
        signature = pss.new(RSA.importKey(private_key)).sign(SHA1.new(license_request.Msg.SerializeToString()))
        license_request.Signature = signature
        return LicenseRequest(
            raw=license_request.SerializeToString(),
            msg=license_request.Msg.SerializeToString()
        )
