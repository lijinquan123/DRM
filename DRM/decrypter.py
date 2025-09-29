# -*- coding: utf-8 -*-
# @Author      : LJQ
# @Time        : 2025/9/29 17:33
# @Version     : Python 3.13.2
import os
import platform
from pathlib import Path


def decrypting_file(encrypt_path: str, decrypt_path: str, key: str, init_path: str = None):
    binaries_dir = Path(__file__).resolve().parent / 'binaries'
    decrypt_programs = {
        'Windows': binaries_dir / 'mp4decrypt.exe',
        'Linux': binaries_dir / 'mp4decrypt_linux',
        'Darwin': binaries_dir / 'mp4decrypt_mac',
    }
    command = f'{decrypt_programs[platform.system()].as_posix()} --key "{key}" "{encrypt_path}" "{decrypt_path}"'
    if init_path:
        command += f' --fragments-info "{init_path}"'
    os.system(command)


def has_decrypted(encrypt_file: str, decrypt_file: str, read_size: int = 1 * 1024 * 1024):
    # AES-CBC模式必须使用填充,因此加密后的文件长度比解密的文件长度大.
    # AES-CTR模式不使用填充,因此加密后的文件长度和解密的文件长度相同.
    # 因此通过`截取文件后1M并比较是否相等`的方式来判断是否解密成功
    encrypt_size = os.path.getsize(encrypt_file)
    decrypt_size = os.path.getsize(decrypt_file)
    if encrypt_size != decrypt_size:
        return True
    with open(encrypt_file, mode='rb') as f:
        f.seek(max(0, encrypt_size - read_size))
        encrypt_bytes = f.read()
    with open(decrypt_file, mode='rb') as f:
        f.seek(max(0, decrypt_size - read_size))
        decrypt_bytes = f.read()
    return encrypt_bytes != decrypt_bytes
