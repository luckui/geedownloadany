from download import downloadProcess, downloadDEMProcess, downloadS1Process


jsonPath = r'grid\grid.json'
output = r'images\testVVint32'
logsPath = 'logsVV.csv'
start = '2023-08-01'
end = '2024-08-01'
scale = 10
nameField = 'alias'
dtype = 'float32'


if __name__ == '__main__':
    downloadS1Process(jsonPath, output, logsPath, start, end, scale, nameField=nameField, dtype=dtype, startId=1, endId=2)
