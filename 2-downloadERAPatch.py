from download import downlaodERAProcess
import os


if __name__ == '__main__':
    output = r''
    for i in range(1980, 2021, 5):
        out = os.path.join(output, str(i))
        os.makedirs(out, exist_ok=True)
        downlaodERAProcess(jsonPath=r'area\shanghai.json', output=out, logsPath='era.csv', start=f'{i}-01-01', end=f'{i}-12-31', scale=27830)