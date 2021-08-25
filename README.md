# BingWallpaper2COS

**本项目基于 Python + PHP，旨在帮助用户自动、高效地在本地和腾讯云 COS 中储存 Bing 每日壁纸，并提供用于随机调用图片的 API 。**

由于 Bing 国内版和国际版的壁纸不尽相同，项目对此作出区分，将 Bing 国内版和国际版的每日壁纸存储在不同的文件夹，同时，为了保证日期的完整性，项目不对壁纸做去重处理。国内版和国际版均保留分辨率为`1920x1080`的版本和 UHD 版本，其中，UHD 版本分辨率不定，但要高于`1920x1080`。

项目主要可以实现以下功能：

* 保存当日的 Bing 壁纸至本地，包括分辨率为`1920x1080`的版本和 UHD 版本；
* 将分辨率为`1920x1080`的版本上传至腾讯云 COS，并获得图片的访问地址，可用于网站背景图等；
* 将相关信息写入数据库，以便后续读取；
* 访问`myexample.com/BingWallpaper2COS`时可以随机返回一张分辨率为`1920x1080`的图片。

# 部署

1. 下载项目并进入项目文件夹：

   ```shell
   cd /www/wwwroot/myexample.com  # 根据实际情况修改路径
   git clone https://github.com/ikaleo/BingWallpaper2COS.git
   cd BingWallpaper2COS
   ```

2. 安装 Python 相关依赖：

   ```shell
   pip3 install -r requirements.txt
   ```
   
3. 根据`configs-sample.py`生成`configs.py`，并依据实际情况修改`configs.py`的相关配置：

   ```
   cp configs-sample.py configs.py
   ```

   `configs.py`示例如下：

   ```python
   # -*- coding: UTF-8 -*-
   from qcloud_cos import CosConfig
   from qcloud_cos import CosS3Client
   from qcloud_cos import CosServiceError
   from qcloud_cos import CosClientError
   
   import sys
   import logging
   
   # 腾讯云COS配置信息
   secret_id = '************************************'  # 替换为用户的secret_id
   secret_key = '********************************'  # 替换为用户的secret_key
   region = 'ap-shanghai'  # 替换为用户的region，例如：ap-shanghai
   token = None  # 使用临时密钥需要传入Token，默认为空,可不填
   domain = None  # COS的自定义源站域名或自定义CDN加速域名,结尾不要加"/", 如果使用全球加速域名, 则设置成对应的域名
   Bucket = 'BucketName-APPID'  # Bucket 由 BucketName-APPID 组成
   
   # Server酱·Turbo版配置信息，用于程序执行错误时向用户发送通知
   SendKey = '*********************************'
   ```

4. 设置定时执行`main.py`，可以在宝塔面板的计划任务中添加一个定时任务，任务类型设定为`Shell脚本`，执行周期自定，每日定时执行一次即可，脚本内容如下：

   ```shell
   # 根据实际情况修改路径
   cd /www/wwwroot/myexample.com/BingWallpaper2COS
   python3 /www/wwwroot/myexample.com/BingWallpaper2COS/main.py
   ```

**项目在首次运行成功后会自动生成`Bing.db`数据库文件以及`BingWallpaper`文件夹**，此时本地项目的目录结构应如下所示：

```
│  Bing.db
│  configs.py
│  index.php
│  main.py
│  requirements.txt
│          
├─BingWallpaper
│  ├─domestic
│  │  └─2021
│  │      └─08
│  │          20210801_domestic@1920x1080.jpg
│  │          20210801_domestic@UHD.jpg
│  │              
│  └─international
│      └─2021
│          └─08
│              20210801_international@1920x1080.jpg
│              20210801_international@UHD.jpg
│                  
└─__pycache__
        configs.cpython-37.pyc
```

腾讯云 COS 的目录结构应如下所示：

```
├─domestic
│  └─2021
│      └─08
│          20210801_domestic@1920x1080.jpg
│              
└─international
    └─2021
        └─08
            20210801_international@1920x1080.jpg
```

# 调用 API

访问`myexample.com/BingWallpaper2COS`，可以随机返回一张图片，其分辨率为`1920x1080`。

出于存储空间费用和外网下行流量费用的考虑，**本项目并未将 UHD 版本的图片上传至腾讯云 COS、图片的访问地址写入数据库**，仅本地保留图片文件，若需要上传，请自行修改`main.py`，如需通过 API 调用，请同时修改`index.php`。

# To Do List

- [ ] 为 API 添加调用参数，使其支持调用指定日期或指定版本（国内版/国际版）的图片

