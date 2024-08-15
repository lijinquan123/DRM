# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2023/11/23 11:27
# @Version     : Python 3.12.2
"""
Widevine是Google开发的专有数字版权管理(DRM) 系统。
它为媒体提供内容保护。
Widevine 分为三个安全级别，根据设备上的硬件提供不同级别的保护。
Widevine 包含在大多数主要 Web 浏览器以及Android和iOS中。

Widevine 使用多种标准和规范，包括MPEG 通用加密(CENC)、加密媒体扩展(EME)、媒体源扩展(MSE) 和HTTP 动态自适应流式传输(DASH)。
此外，Widevine 支持Apple, Inc.于 2009 年开发的HTTP Live Streaming (HLS) 协议。

在 Widevine 的一种实现中，浏览器从内容分发网络(CDN) 接收加密内容。
然后，内容被发送到内容解密模块(CDM)，该模块创建许可证请求以发送到许可证服务器。
然后播放器从许可证服务器接收许可证并将其传递给 CDM。
为了解密流，CDM 将媒体和许可证发送到解密内容所需的 OEMCrypto 模块。
OEMCrypto 是 TEE 的接口；大多数实现确保会话密钥、解密的内容密钥和解密的内容流不能被其他正在运行的应用程序访问。
这通常是通过具有独立存储器的辅助处理器来完成的。
然后内容被发送到视频堆栈并以块的形式向最终用户显示。
许可证请求和许可证响应消息是使用Protocol Buffers发送和接收的。
"""
# https://github.com/sim0n00ps/OF-DL/tree/master
# https://github.com/dhavalhariyani/hs-widevine/tree/main
# https://github.com/go-webdl/drm/tree/master
