# 说明
## 文件夹说明
```
area 放了示例下载区域的shp文件对应的geojson文件，是通过1-shp2geojson.py转换成json格式。
grid 放置了全国滨海格网和对应的json
``` 
## 文件说明
### Step0
0-auth.ipynb(GEE登录验证)
选择自己的项目生成token验证登录
### Step1
1-shp2geojson.py(shp转GeoJson)
需要注意的是，1-shp2geojson.py里可以选择convert和convert2bbox方法，convert方法会把shp的每个feature原原本本的转换成geojson，但是convert2bbox方法会把它shp的每个feature转换成bounding box即矩形框。
### Step2
2-downloadPatch.py(批下载程序)
downloadProcess()方法用来下载S2 L8 L5的遥感影像。其示例参数如下：
```
satellite = 'L8' # 选择下载的影像，可选值有S2、L8或者L5
jsonPath = r"area\area.json"  # 输入下载区geojson文件的路径
output = r"images" # 输出文件夹
logsPath = './logs.csv' # 输出日志文件路径, csv格式
start = "2019-01-01"
end = "2019-12-30"
scale = 30
# 需要指定下载波段，band名称要正确，数据下载下来的波段顺序就是这里的顺序
bands = ['SR_B6', 'SR_B5', 'SR_B4', 'SR_B3', 'SR_B2'] 

# 以下参数可以不输入，有默认值
# 如果指定了nameField就可以指定输出tif文件名，该字段为字符串类型，输出名为[指定字段值].tif，如果不指定就会以FID_[ID].tif输出文件
nameField = 'name' # 这里指定了name字段为输出名称
# startId, endId所指的Id是要素的默认排序索引, 也即在ArcGIS打开属性表中的FID字段, 下载从startId开始到endId的要素, 前闭后开，默认全部下载
startId = 0
endId = -1
```