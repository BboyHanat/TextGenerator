from core.base import gen_all_pic, gen_label_data, gen_all_voc


class Pipeline:

    def start(self):
        # 批量生成图片
        gen_all_pic()
        # 生成标签文件
        gen_label_data()
        # 生成voc数据集
        gen_all_voc()


pipeline = Pipeline()
# pipeline.start()
