import geopandas as gpd


shpPath = r""
outPath = r""

# 把shp转换成geojson, 这样下载下来的tif形状与shp每个polygon要素形状一模一样
def convert(shpPath, outPath):
    gdf = gpd.read_file(shpPath)
    crs = gdf.crs
    if crs:
        if crs.to_epsg() == 4326:
            pass
        else:
            gdf = gdf.to_crs(epsg=4326)
        gdf.to_file(outPath, driver="GeoJSON")
    else:
        print('没有定义参考系统!')


# 把shp转换成geojson，并且是每个要素的bounding box，不是polygon的边界
def convert2bbox(shpPath, outPath):
    gdf = gpd.read_file(shpPath)
    crs = gdf.crs
    if crs:
        if crs.to_epsg() == 4326:
            pass
        else:
            gdf = gdf.to_crs(epsg=4326) #如果原坐标系不是wgs84就启用这行
        bounding_boxes = gdf.geometry.apply(lambda geom: geom.envelope)
        gdf['geometry'] = bounding_boxes
        gdf.to_file(outPath, driver="GeoJSON")
    else:
        print('没有定义参考系统!')


if __name__ == "__main__":
    convert(shpPath, outPath)