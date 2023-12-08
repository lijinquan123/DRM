# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/12/8 11:40
# @Version     : Python 3.6.4
"""OEMCrypto(DRM秘钥解密模块)

验证发往和来自许可证服务器的消息的真实性
建立可用于解密消息中包含的密钥材料的密钥加密密钥（从设备密钥派生的密钥）
将加密的内容密钥加载到受信任的环境中并解密它们
使用内容密钥生成解密流以进行解码和渲染
"""
import hashlib
import hmac

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import CMAC
from Crypto.PublicKey import RSA
from Crypto.Util import Padding

from DRM.exceptions import *
from DRM.widevine.formats import wv_proto2_pb2
from DRM.widevine.structs import Key, Keys


class OEMCrypto(object):
    def __init__(self, license_data: bytes, msg: bytes, private_key: bytes):
        """DRM秘钥解密模块
        通过服务器返回的许可数据,请求数据中的消息数据,设备私钥来获取解密秘钥
        解密秘钥只和这三个数据有关
        此类可脱离DRM模块,嵌入到任何模块中
        :param license_data: 服务器返回的许可数据
        :param msg: 请求数据中的消息数据
        :param private_key: 设备私钥
        """
        self.license = license_data
        self.msg = msg
        self.private_key = private_key

    def decrypt(self) -> Keys:
        """解密服务端返回的许可数据,得出DRM解密秘钥
        解密前必须先验证服务器返回的摘要和生成的摘要是否一致
        解密出的数据包括KID和KEY,KID可在文件头中找到,解密文件必须使用对应的KID秘钥
        """
        signed_license = wv_proto2_pb2.SignedLicense()
        signed_license.ParseFromString(self.license)

        # 计算数据摘要
        session_key = PKCS1_OAEP.new(RSA.importKey(self.private_key)).decrypt(signed_license.SessionKey)
        encryption = b"\x01ENCRYPTION\x00" + self.msg + b"\x00\x00\x00\x80"
        decrypt_key = CMAC.new(session_key, encryption, ciphermod=AES).digest()
        verify_key = b''
        for i in range(2):
            authentication = chr(i + 1).encode('utf-8') + b"AUTHENTICATION\x00" + self.msg + b"\x00\x00\x02\x00"
            verify_key += CMAC.new(session_key, authentication, ciphermod=AES).digest()
        verification = hmac.new(verify_key, signed_license.Msg.SerializeToString(), digestmod=hashlib.sha256).digest()

        # 验证摘要数据是否一致
        if verification != signed_license.Signature:
            raise LicenseSignatureUnmatchedError(f'{signed_license.Signature} != {verification}')

        # 解密,秘钥通过AES加密,解密后即是真实的秘钥
        # 每个KID对应一个秘钥,KID存放在视频文件头中,解密文件需使用对应的KID秘钥
        keys = Keys()
        for key_container in signed_license.Msg.Key:
            key_type = wv_proto2_pb2.License.KeyContainer.KeyType.Name(key_container.Type)
            if key_container.Id:
                kid = key_container.Id
            else:
                kid = key_type.encode('utf-8')
            key = Padding.unpad(AES.new(decrypt_key, AES.MODE_CBC, iv=key_container.Iv).decrypt(key_container.Key), 16)
            if key_type == "OPERATOR_SESSION":
                permissions = []
                for descriptor, value in key_container._OperatorSessionKeyPermissions.ListFields():
                    if value == 1:
                        permissions.append(descriptor.name)
            else:
                permissions = []
            keys.append(Key(kid.hex(), key_type, key.hex(), permissions))
        return keys
