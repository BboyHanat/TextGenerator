from core import conf
from core.base import gen_all_pic, gen_label_data
from utils import log


class Pipeline:

    def start(self):
        # gen_all_pic()
        gen_label_data()


pipeline = Pipeline()
pipeline.start()
