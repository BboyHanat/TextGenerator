"""
Name : run.py.py
Author  : Hanat
Contect : hanati@tezign.com
Time    : 2019-09-18 11:55
Desc:
"""
from core.pipeline import pipeline
from multiprocessing import Pool
import os

process_count = 20


def start():
    pipeline.start()


if __name__ == '__main__':

    print('Parent process %s.' % os.getpid())
    p = Pool(process_count)
    for i in range(process_count):
        p.apply_async(start)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
