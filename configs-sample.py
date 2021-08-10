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
domain = None  # COS的自定义源站域名或自定义CDN加速域名,结尾不要加"/", 如果使用全球加速域名, 则设置成对应的域名, 如mybucket-01234.cos.accelerate.myqcloud.com，开启全球加速请参考https://cloud.tencent.com/document/product/436/38864
Bucket = 'BucketName-APPID'  # Bucket 由 BucketName-APPID 组成

# Server酱·Turbo版配置信息，用于程序执行错误时向用户发送通知
SendKey = '*********************************'
