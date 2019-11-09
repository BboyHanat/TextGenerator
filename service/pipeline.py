from service.base import gen_all_pic


class Pipeline:

    def start(self):
        # 批量生成图片
        gen_all_pic()


pipeline = Pipeline()
# pipeline.start()
