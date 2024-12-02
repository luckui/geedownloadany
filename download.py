import ee
import geemap
import os
import time
import pandas as pd


# jsonPath = r"area\area.json"  # 输入geojson文件的路径
# output = r"images" # 输出文件夹
# logsPath = './logs.csv' # 输出日志文件路径, csv格式
# start = "2023-06-01"
# end = "2024-06-30"
# scale = 10
# bands = ['B11', 'B8', 'B4', 'B3', 'B2']
# 以下参数如果使用的话，请在__main__下修改downloadProcess把以下参数添加进去
# startId, endId 的Id是要素的默认排序索引, 也即在ArcGIS打开属性表中的FID字段, 下载从startId开始到endId的要素, 前闭后开，默认全部下载
# startId = 1
# endId = -1
# 指定nameField即指定tif文件名字段，该字段为字符串类型
# nameField = 'areaName'


def maskS2clouds(image):
    qa = image.select('QA60')
    # Bits 10 and 11是云，我们要把它mask掉
    cloudBitMask = 1 << 10
    cirrusBitMask = 1 << 1
    # 这两个标志都应该设置为0，表示条件明确。
    mask = qa.bitwiseAnd(cloudBitMask).eq(0) \
        .And(qa.bitwiseAnd(cirrusBitMask).eq(0))
    # 哨兵的像元值是反射率的10000倍，要除以10000
    return image.updateMask(mask)


# Applies scaling factors.
def apply_scale_factors(image):
    optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2).multiply(10000)
    thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0).multiply(10000)
    return image.addBands(optical_bands, None, True).addBands(
        thermal_bands, None, True
    )


def L5_apply_scale_factors(image):
  optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2).multiply(10000)
  thermal_bands = image.select('ST_B6').multiply(0.00341802).add(149.0).multiply(10000)
  return image.addBands(optical_bands, None, True).addBands(
      thermal_bands, None, True
  )


def mask_edge(image):
  edge = image.lt(-30.0)
  masked_image = image.mask().And(edge.Not())
  return image.updateMask(masked_image).multiply(1000000)


# 循环每一个feature的边界裁剪后下载
def S2splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        imgcol = s2.filterDate(start, end)\
                   .filterBounds(geom)\
                   .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 10))\
                   .map(maskS2clouds)\
                   .select(bands)
        img = imgcol.median().clip(geom)
        img.rename(bands)

        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def L8splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        imgcol = l8.filterDate(start, end)\
                   .filterBounds(geom)\
                   .filter(ee.Filter.lt('CLOUD_COVER', 20))\
                   .map(apply_scale_factors)\
                   .select(bands)
        img = imgcol.median().clip(geom)
        img.rename(bands)

        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def L5splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        imgcol = l5.filterDate(start, end)\
                   .filterBounds(geom)\
                   .filter(ee.Filter.lt('CLOUD_COVER', 20))\
                   .map(L5_apply_scale_factors)\
                   .select(bands)
        img = imgcol.median().clip(geom)
        img.rename(bands)

        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def DEMsplitDownload(jsonPath, output, scale, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    dataset = ee.Image('CGIAR/SRTM90_V4')
    elevation = dataset.select('elevation')
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        img = elevation.clip(geom)

        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def S1splitDownload(jsonPath, output, start, end, scale, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
    # desc = img_vv.filter(ee.Filter.eq('orbitProperties_pass', 'DESCENDING'))
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        img = s1.filterBounds(geom)\
                .filterDate(start, end)\
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))\
                .filter(ee.Filter.eq('instrumentMode', 'IW'))\
                .filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))\
                .select('VV')\
                .map(mask_edge)\
                .median()\
                .clip(geom)
        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def ERASplitDownload(jsonPath, output, start, end, scale, startId, endId, nameField=None, dtype=None):
    ee.Initialize()
    era = ee.ImageCollection("ECMWF/ERA5/MONTHLY")
    featureCol = geemap.geojson_to_ee(jsonPath)
    mylist = featureCol.toList(featureCol.size())
    infos = mylist.getInfo()
    logs = []
    if endId == -1:
        endId = len(infos)
    for i in range(startId, endId):
        info = infos[i]
        geom = info["geometry"]
        img = era.filterBounds(geom)\
                .filterDate(start, end)\
                .select(['total_precipitation'])\
                .sum()\
                .clip(geom)
        tifname = 'FID_'+str(i)+".tif"
        if nameField!=None:
            tifname = info['properties'][nameField]+".tif"
        note = retryDown(img=img, output=output, tifname=tifname, scale=scale, geom=geom, dtype=dtype)
        logs.append(note)
    return logs


def retryDown(img, output, tifname, geom, scale, dtype=None, max_retries=10, delay=1):
    attempt = 0
    while attempt<max_retries:
        try:
            if dtype != None:
                geemap.download_ee_image(
                    image=img,
                    filename=os.path.join(output, tifname),
                    region=geom,
                    crs='EPSG:4326',
                    scale=scale,
                    dtype=dtype,
                    max_tile_size=4,
                )
            else:
                geemap.download_ee_image(
                    image=img,
                    filename=os.path.join(output, tifname),
                    region=geom,
                    crs='EPSG:4326',
                    scale=scale,
                    max_tile_size=4,
                )
            return f'{tifname}下载成功, {attempt+1}次完成'
        except Exception as e:
            attempt+=1
            print(f'{tifname}下载失败，第{attempt+1}次, 原因：{e}')
            if attempt<max_retries:
                time.sleep(delay)
            else:
                print('退出尝试')
                return f'{tifname}下载失败'
            

def downlaodERAProcess(jsonPath: str, output: str, logsPath: str, start: str, end: str, scale: int, **kwargs):
    startId = kwargs.get('startId', 0)
    endId = kwargs.get('endId', -1)
    nameField = kwargs.get('nameField', None)
    dtype = kwargs.get('dtype', None)
    if not os.path.exists(output):
        os.mkdir(output)
    logs = ERASplitDownload(jsonPath, output, start, end, scale, startId=startId, endId=endId, nameField=nameField, dtype=dtype)
    logs = pd.DataFrame(logs, columns=['record'])
    logs.to_csv(logsPath, index=False)


def downloadS1Process(jsonPath: str, output: str, logsPath: str, start: str, end: str, scale: int, **kwargs):
    startId = kwargs.get('startId', 0)
    endId = kwargs.get('endId', -1)
    nameField = kwargs.get('nameField', None)
    dtype = kwargs.get('dtype', None)
    if not os.path.exists(output):
        os.mkdir(output)
    logs = S1splitDownload(jsonPath, output, start, end, scale, startId=startId, endId=endId, nameField=nameField, dtype=dtype)
    logs = pd.DataFrame(logs, columns=['record'])
    logs.to_csv(logsPath, index=False)


def downloadDEMProcess(jsonPath: str, output: str, logsPath: str, scale: int, **kwargs):
    """
    总下载程序入口\n
    satellite: 三种选择，'S2'、'L8'、'L5'\n
    jsonPath: 输入geojson文件的路径\n
    output: 输出文件夹\n
    logsPath: 输出日志文件路径, csv格式\n
    scale: 分辨率\n
    **kwargs: {startId: 0, endId: -1, nameField: None} 是要素的默认排序索引, 也即在ArcGIS打开属性表中的FID字段, 下载从startId开始到endId的要素, 前闭后开，默认全部下载\n
    """
    startId = kwargs.get('startId', 0)
    endId = kwargs.get('endId', -1)
    nameField = kwargs.get('nameField', None)
    dtype = kwargs.get('dtype', None)
    if not os.path.exists(output):
        os.mkdir(output)
    logs = DEMsplitDownload(jsonPath, output, scale, startId=startId, endId=endId, nameField=nameField, dtype=dtype)
    logs = pd.DataFrame(logs, columns=['record'])
    logs.to_csv(logsPath, index=False)


def downloadProcess(satellite: str, jsonPath: str, output: str, logsPath: str, start: str, end: str, scale: int, bands: list, **kwargs):
    """
    总下载程序入口\n
    satellite: 三种选择，'S2'、'L8'、'L5'\n
    jsonPath: 输入geojson文件的路径\n
    output: 输出文件夹\n
    logsPath: 输出日志文件路径, csv格式\n
    start: 开始时间\n
    end: 结束时间\n
    scale: 分辨率\n
    bands: 波段列表, 注意波段名称正确, 下载结果波段顺序与输入一致\n
    **kwargs: {startId: 0, endId: -1, nameField: None} 是要素的默认排序索引, 也即在ArcGIS打开属性表中的FID字段, 下载从startId开始到endId的要素, 前闭后开，默认全部下载\n
    """
    startId = kwargs.get('startId', 0)
    endId = kwargs.get('endId', -1)
    nameField = kwargs.get('nameField', None)
    dtype = kwargs.get('dtype', None)
    if not os.path.exists(output):
        os.mkdir(output)
    if satellite == 'S2':
        logs = S2splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField, dtype=dtype)
    elif satellite == 'L8':
        logs = L8splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField, dtype=dtype)
    elif satellite == 'L5':
        logs = L5splitDownload(jsonPath, output, start, end, scale, bands, startId, endId, nameField, dtype=dtype)
    logs = pd.DataFrame(logs, columns=['record'])
    logs.to_csv(logsPath, index=False)


if __name__ == '__main__':
    # downloadProcess(jsonPath, output, logsPath, start, end, scale, bands)
    pass

