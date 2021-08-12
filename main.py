# -*- coding: UTF-8 -*-
import urllib.request
import json
import requests
import time
import os
import sqlite3
import hashlib

import configs  # 导入配置文件

global time_Y, time_m, time_d
# 设置请求头Request Headers
global headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Mobile Safari/537.36'
}
global set_mkt
set_mkt = ['zh-cn', 'en-us', 'ja-jp', 'en-ww', 'en-gb', 'en-au', 'en-ca', 'fr-fr', 'de-de', 'pt-br']


# 确定网址
def get_image_json_url(num):
    global set_mkt
    image_json_url = 'https://global.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&setmkt=' + set_mkt[num]
    return image_json_url


# 根据网址获取json
def get_record(url):
    global headers
    req = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(req)
    ele_json = json.loads(response.read().decode())
    return ele_json


# 计算文件的MD5
def md5(path):
    myhash = hashlib.md5()
    f = open(path, 'rb')
    while True:
        b = f.read(8096)
        if not b:
            break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()


# 保存图片
def save_image(img_url, object_key):
    pic_path, pic_name = os.path.split('BingWallpaper' + '/' + object_key)
    try:
        if not os.path.exists(pic_path):  # 判断目录是否存在,若不存在则新建目录
            os.makedirs(pic_path)
        global headers
        image = requests.get(img_url, headers=headers)
        f = open('BingWallpaper' + '/' + object_key, 'ab')
        f.write(image.content)
        f.close()
        # 判断图片是否大于100KB，若大于，则视为图片保存成功
        # 若图片保存失败，则通过Server酱发送消息通知
        if os.path.getsize('BingWallpaper' + '/' + object_key) / 1024 > 100:
            print(pic_name + '保存成功！')
            save_image_status = 1
        else:
            print(pic_name + '保存失败，尝试通过Server酱发送通知！')
            requests.post('https://sctapi.ftqq.com/' + configs.SendKey + '.send',
                          data={'text': "必应每日一图保存失败！", 'desp': pic_name + "保存失败！"})
            save_image_status = 0
        return save_image_status
    except:
        print(pic_name + '保存失败，尝试通过Server酱发送通知！')
        requests.post('https://sctapi.ftqq.com/' + configs.SendKey + '.send',
                      data={'text': "必应每日一图保存失败！", 'desp': pic_name + "保存失败！"})
        save_image_status = 0
        return save_image_status


# 上传图片到腾讯云COS
def upload2cos(object_key, pic_md5):
    pic_path, pic_name = os.path.split('BingWallpaper' + '/' + object_key)
    try:
        configs.logging.basicConfig(level=configs.logging.INFO, stream=configs.sys.stdout)
        config = configs.CosConfig(Region=configs.region, SecretId=configs.secret_id,
                                   SecretKey=configs.secret_key, Token=configs.token,
                                   Domain=configs.domain)  # 获取配置对象
        client = configs.CosS3Client(config)
        with open('BingWallpaper' + '/' + object_key, 'rb') as fp:
            response = client.put_object(
                Bucket=configs.Bucket,
                Body=fp,
                Key=object_key,
            )
        # 判断本地图片和腾讯云COS中的图片的MD5值是否相等
        # 若MD5值不相等，则图片上传失败，通过Server酱发送消息通知
        if response['ETag'].split('"')[1] == pic_md5:  # 由'ETag'返回的MD5值自带双引号，形如"6b16281f8f07e029485c0efe10657b23"！！！
            print(pic_name + '上传成功！')
            upload2cos_status = 1
        else:
            print(pic_name + '上传失败，尝试通过Server酱发送通知！')
            requests.post('https://sctapi.ftqq.com/' + configs.SendKey + '.send',
                          data={'text': "必应每日一图上传失败！", 'desp': pic_name + "上传失败！"})
            upload2cos_status = 0
        return upload2cos_status
    except:
        print(pic_name + '上传失败，尝试通过Server酱发送通知！')
        requests.post('https://sctapi.ftqq.com/' + configs.SendKey + '.send',
                      data={'text': "必应每日一图上传失败！", 'desp': pic_name + "上传失败！"})
        upload2cos_status = 0
        return upload2cos_status


# 将图片信息插入数据库
def insert2db(date, title, region, url_base, url_1920x1080, url_1920x1080_via_cos, url_uhd):
    try:
        conn = sqlite3.connect("Bing.db")  # 在此文件所在的文件夹打开或创建数据库文件
        c = conn.cursor()  # 设置游标
        # 创建一个含有id，date，hsh，title，region，URL_base，MD5_1920x1080，URL_1920x1080，URL_1920x1080_via_COS，MD5_UHD，
        # URL_UHD以及URL_UHD_via_COS字段的表Bing_info
        c.execute('''CREATE TABLE IF NOT EXISTS Bing_info
                 (id integer primary key autoincrement, 
                 date text,
                 title text,
                 region text,
                 URL_base text,
                 URL_1920x1080 text,
                 URL_1920x1080_via_COS text,
                 URL_UHD text)''')
        c.execute("INSERT INTO Bing_info VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)",
                  (date, title, region, url_base, url_1920x1080, url_1920x1080_via_cos, url_uhd))
        print('数据库写入成功！')
        insert2db_status = 1
        return insert2db_status
    except:
        print('操作数据库出错，尝试通过Server酱发送通知！')
        requests.post('https://sctapi.ftqq.com/' + configs.SendKey + '.send',
                      data={'text': "必应每日一图操作数据库出错！", 'desp': "操作数据库出错！"})
        insert2db_status = 0
        return insert2db_status
    finally:
        # 关闭Cursor
        c.close()
        # 提交事务
        conn.commit()
        # 关闭Connection
        conn.close()


if __name__ == '__main__':
    # 获取当前时间
    time_Y = time.strftime("%Y", time.localtime())
    time_m = time.strftime("%m", time.localtime())
    time_d = time.strftime("%d", time.localtime())

    # 判断用户是否自定义COS源站域名或CDN加速域名
    if configs.domain == None:
        MyDomin = configs.Bucket + '.cos.' + configs.region + '.myqcloud.com'
    else:
        MyDomin = configs.domain

    # 获取国内版每日一图
    image_json_url = 'https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&setmkt=zh_cn'
    image_json = get_record(image_json_url)
    # 基准文件名，类似于"20210807_"的形式，之后继续添加分辨率和文件后缀即可
    # 完整的文件名形如"20210807_international_001@1920x1080.jpg"
    pic_name_base = [time_Y + time_m + time_d + '_' + 'domestic',
                     time_Y + time_m + time_d + '_' + 'international']
    # 分辨率为1920x1080的图片链接
    image_url_1920x1080 = 'https://cn.bing.com' + image_json['images'][0]['urlbase'] + '_1920x1080.jpg'
    # 分辨率为1920x1080的图片的保存路径+文件名
    object_key_1920x1080 = 'domestic' + '/' + time_Y + '/' + time_m + '/' + pic_name_base[0] + '@1920x1080' + '.jpg'
    save_image_status_1920x1080 = save_image(image_url_1920x1080, object_key_1920x1080)
    # 计算并返回图片的MD5值，用于判断上传到腾讯云COS的图片的完整性
    pic_md5_1920x1080 = md5('BingWallpaper' + '/' + object_key_1920x1080)
    upload2cos_status_1920x1080 = upload2cos(object_key_1920x1080, pic_md5_1920x1080)
    # 清晰度为UHD(分辨率不定，但大于1920x1080)的图片链接
    image_url_uhd = 'https://cn.bing.com' + image_json['images'][0]['urlbase'] + '_UHD.jpg'
    # 清晰度为UHD的图片的保存路径+文件名
    object_key_uhd = 'domestic' + '/' + time_Y + '/' + time_m + '/' + pic_name_base[0] + '@UHD' + '.jpg'
    save_image_status_uhd = save_image(image_url_uhd, object_key_uhd)
    # 计算并返回图片的MD5值，用于判断上传到腾讯云COS的图片的完整性
    # pic_md5_uhd = md5('BingWallpaper' + '/' + object_key_uhd)
    # 清晰度为UHD的图片，只保存在本地，暂不上传到腾讯云COS
    # upload2cos_status_uhd = upload2cos(object_key_uhd, pic_md5_uhd)
    insert2db_status = insert2db(time_Y + time_m + time_d,
                                 image_json['images'][0]['copyright'],
                                 'zh-cn',
                                 image_json['images'][0]['urlbase'],
                                 image_url_1920x1080,
                                 'https://' + MyDomin + '/' + object_key_1920x1080,
                                 image_url_uhd)
    if save_image_status_1920x1080 and upload2cos_status_1920x1080 and save_image_status_uhd and insert2db_status:
        domestic_FLAG = 1
    else:
        domestic_FLAG = 0

    # 获取国际版每日一图
    for i in range(1, len(set_mkt)):
        # 由于前面已经获取了国内版每日一图，故for循环从1开始，跳过zh-cn
        # 事实上，也可以在for循环中使i从0开始，直接获取国内版每日一图，但由于https://global.bing.com对应的服务器位于美国，
        # 高峰时期可能出现time out的情况，一般建议国内版每日一图从https://cn.bing.com抓取
        if i == 0:
            region = 'domestic'
            temp = 0
        else:
            region = 'international'
            temp = 1
        image_json_url = get_image_json_url(i)
        image_json = get_record(image_json_url)
        # 分辨率为1920x1080的图片链接
        image_url_1920x1080 = 'https://global.bing.com' + image_json['images'][0]['urlbase'] + '_1920x1080.jpg'
        # 分辨率为1920x1080的图片的保存路径+文件名
        object_key_1920x1080 = region + '/' + time_Y + '/' + time_m + '/' + pic_name_base[temp] + '@1920x1080' + '.jpg'
        save_image_status_1920x1080 = save_image(image_url_1920x1080, object_key_1920x1080)
        # 计算并返回图片的MD5值，用于判断上传到腾讯云COS的图片的完整性
        pic_md5_1920x1080 = md5('BingWallpaper' + '/' + object_key_1920x1080)
        upload2cos_status_1920x1080 = upload2cos(object_key_1920x1080, pic_md5_1920x1080)
        # 清晰度为UHD(分辨率不定,但大于1920x1080)的图片链接
        image_url_uhd = 'https://global.bing.com' + image_json['images'][0]['urlbase'] + '_UHD.jpg'
        # 清晰度为UHD的图片的保存路径+文件名
        object_key_uhd = region + '/' + time_Y + '/' + time_m + '/' + pic_name_base[temp] + '@UHD' + '.jpg'
        save_image_status_uhd = save_image(image_url_uhd, object_key_uhd)
        # 计算并返回图片的MD5值，用于判断上传到腾讯云COS的图片的完整性
        # pic_md5_uhd = md5('BingWallpaper' + '/' + object_key_uhd)
        # 清晰度为UHD的图片，只保存在本地，暂不上传到腾讯云COS
        # upload2cos_status_uhd = upload2cos(object_key_uhd, pic_md5_uhd)
        if save_image_status_1920x1080 and upload2cos_status_1920x1080 and save_image_status_uhd:
            international_FLAG = 1
            break
        else:
            international_FLAG = 0
            time.sleep(3)  # 等待3秒后再继续循环
    # 插入数据库的操作放在循环外的原因是防止在循环中同一张图片被插入多条记录
    insert2db_status = insert2db(time_Y + time_m + time_d,
                                 image_json['images'][0]['copyright'],
                                 set_mkt[i],
                                 image_json['images'][0]['urlbase'],
                                 image_url_1920x1080,
                                 'https://' + MyDomin + '/' + object_key_1920x1080,
                                 image_url_uhd)
    if insert2db_status:  # 判断插入数据库是否成功
        international_FLAG = 1
    else:
        international_FLAG = 0
    if domestic_FLAG and international_FLAG:
        print('所有操作成功完成！')
    else:
        print('存在操作失败的情况，请检查！')
