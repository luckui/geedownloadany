from download import downloadProcess, downloadDEMProcess


jsonPath = r'grid\grid.json'
output = r'images\DEM'
logsPath = 'logsDEM.csv'
scale = 90
nameField = 'alias'


if __name__ == '__main__':
    downloadDEMProcess(jsonPath, output, logsPath, scale, nameField=nameField, dtype='int16')
    pass