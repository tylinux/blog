---
title: 解包 PyInstaller 生成的可执行文件
tags: None
category: None
date: 2023-09-05
---

# 解包 PyInstaller 生成的可执行文件

最近使用的一个小工具，想了解一下它的工作原理，原本以为是 Native 开发，拖入 IDA 发现大量 PyInstaller 相关字符串，意识到这个程序是使用 Python 开发，PyInstaller 打包成的应用，遂尝试了对其进行解包和解密，记录如下。

<!-- more -->

## 解包

首先找到了 [pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor) 这个工具，只有一个简单的 py 文件，即可从可执行文件中解包出来 `.pyc` 文件。不过遗憾的是对于 PyInstaller 生成的 `PYZ` 文件未能成功解出来，不知道是我的姿势问题还是工具未能支持。不过在这个项目的 [see-also](https://github.com/extremecoders-re/pyinstxtractor#see-also) 部分，发现了 [pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng) 和 [pyinstxtractor-web](https://github.com/pyinstxtractor/pyinstxtractor-go) 两个工具，
图简单直接使用了 `pyinstxtractor-web`，效果很好，一步到位就解包完成了。

```
.
├── PYZ-00.pyz_extracted
│   ├── __future__.pyc.pyc.encrypted
│   └── zipimport.pyc.pyc.encrypted
├── base_library.zip
├── certifi
│   ├── cacert.pem
│   └── py.typed
├── charset_normalizer
│   ├── md.cpython-310-darwin.so
│   └── md__mypyc.cpython-310-darwin.so
├── lib-dynload
│   └── zlib.cpython-310-darwin.so
├── libbz2.dylib
├── libcrypto.3.dylib
├── libffi.8.dylib
├── liblzma.5.dylib
├── libpython3.10.dylib
├── libssl.3.dylib
├── libz.1.dylib
├── main.pyc
├── pyi_rth_inspect.pyc
├── pyi_rth_pkgres.pyc
├── pyi_rth_pkgutil.pyc
├── pyiboot01_bootstrap.pyc
├── pyimod00_crypto_key.pyc
├── pyimod01_archive.pyc
├── pyimod02_importers.pyc
├── pyimod03_ctypes.pyc
├── struct.pyc
└── tinyaes.cpython-310-darwin.so

```

## 解密

对与 `.pyc` 文件，可以通过 [pycdc](https://github.com/zrax/pycdc) 项目提供的 `pycdc` 命令反编译为 `.py` 源码。但是项目中大部分的 `pyc` 文件都被 PyInstaller 加密的，无法直接反编译。
观察一下就能发现，`pyimod00_crypto_key.pyc` 这个文件可能就是加密的 key，而 `pyimod01_archive.pyc` 文件可能是打包的相关逻辑。使用 `pycdc` 反编译结果如下:

pyimod00_crypto_key.py:

```python
# Source Generated with Decompyle++
# File: pyimod00_crypto_key.pyc (Python 3.10)

key = 'xxxxxxxxxxxxx-'
```
pyimod01_archive.py:

```python
# Source Generated with Decompyle++
# File: pyimod01_archive.pyc (Python 3.10)

import sys
import os
import struct
import marshal
import zlib
import _frozen_importlib
PYTHON_MAGIC_NUMBER = _frozen_importlib._bootstrap_external.MAGIC_NUMBER
CRYPT_BLOCK_SIZE = 16
PYZ_ITEM_MODULE = 0
PYZ_ITEM_PKG = 1
PYZ_ITEM_DATA = 2
PYZ_ITEM_NSPKG = 3

class ArchiveReadError(RuntimeError):
    pass


class Cipher:
    '''
    This class is used only to decrypt Python modules.
    '''
    
    def __init__(self):
        import pyimod00_crypto_key
        key = pyimod00_crypto_key.key
    # WARNING: Decompyle incomplete

    
    def __create_cipher(self, iv):
        return self._aesmod.AES(self.key.encode(), iv)

    
    def decrypt(self, data):
        cipher = self.__create_cipher(data[:CRYPT_BLOCK_SIZE])
        return cipher.CTR_xcrypt_buffer(data[CRYPT_BLOCK_SIZE:])

# 省略大部分
```

可以可以看到加密的这部门逻辑，使用了 AES 加密，块大小16字节，依据 `CTR_xcrypt_buffer` 这个方法名可以找到对应的 package 是 [tinyaes](https://pypi.org/project/tinyaes/)。
再依据从网上找到的其他文章，解密 `pyc` 的脚本就出来了：

```py
#!/bin/env python3
import os
import tinyaes
import zlib

def decrypt(filepath, target_path):
    key = b'xxxxxxxxxxxxxxxx' # 加密密钥
    content = open(filepath, 'rb').read()
    CRYPT_BLOCK_SIZE = 16

    # 被加密文件的头 16 个字节是 iv
    iv = content[:CRYPT_BLOCK_SIZE] 
    cipher = tinyaes.AES(key, iv)
    try:
        # 解密结果需要解压
        decrypt_res = zlib.decompress(cipher.CTR_xcrypt_buffer(content[CRYPT_BLOCK_SIZE:]))
        with open('tmp.pyc', 'wb') as f:
            # pyc 文件的文件头被去掉了，需要手动补回来，16个字节
            f.write(b'\x6f\x0d\x0d\x0a\0\0\0\0\0\0\0\0\0\0\0\0')
            f.write(decrypt_res)
        # 这里直接调用 pycdc 反编译成 py 源码文件了
        os.system(f'pycdc tmp.pyc -o {target_path}')
    except zlib.error as e:
        print(filepath)
```

Done~

## 参考
1. [[原创]Python逆向——Pyinstaller逆向 ](https://bbs.kanxue.com/thread-271253.htm)
2. [pyinstaller 逆向筆記](https://hackmd.io/@foxo-tw/SJ5Ck2Ed8)