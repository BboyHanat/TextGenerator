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
from core import conf
import traceback

process_count = conf['gen_mode_conf']['process_count']


def start():
    try:
        pipeline.start()
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':

    print('Parent process %s.' % os.getpid())
    print("process count : {process_count}".format(process_count=process_count))
    p = Pool(process_count)
    for i in range(process_count):
        p.apply_async(start)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
