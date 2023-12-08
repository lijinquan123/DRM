# DRM
DRM秘钥解密程序

### 使用方式
```
from DRM.widevine.cdm import ContentDecryptionModules
from DRM.widevine.oemcrypto import OEMCrypto

cdm = ContentDecryptionModules(pssh)
license_request = cdm.get_license_request(private_key, raw_client_id)
# 通过请求许可链接获取许可数据
license_data = ...
oem = OEMCrypto(license_data, license_request.msg, private_key)
# 打印出解密秘钥
print(oem.decrypt().tolist())
```
