from download import downloadProcess, downloadDEMProcess

satellite = 'L8' # S2 L8 or L5
jsonPath = r"area\area.json"  # 输入geojson文件的路径
output = r"images" # 输出文件夹
logsPath = './logs.csv' # 输出日志文件路径, csv格式
start = "2019-01-01"
end = "2019-12-30"
scale = 30
bands = ['SR_B6', 'SR_B5', 'SR_B4', 'SR_B3', 'SR_B2']
# startId, endId 的 Id是要素的默认排序索引, 也即在ArcGIS打开属性表中的FID字段, 下载从startId开始到endId的要素, 前闭后开，默认全部下载
startId = 0
endId = -1
# 指定nameField即指定tif文件名字段，该字段为字符串类型
nameField = 'name'


if __name__ == '__main__':
    downloadProcess(satellite, jsonPath, output, logsPath, start, end, scale, bands, startId=startId, endId=endId, nameField=nameField)

