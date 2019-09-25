class Strategy:

    def __init__(self):
        pass

    def __repr__(self):
        return str(self.__class__.__name__)

    def logic(self, block_group, next_block) -> bool:
        pass

    @staticmethod
    def check_is_out(block_group, block):
        """
        检查block是否超出了block_group的边界
        :param block_group:
        :param block:
        :return:
        """
        if block.outer_box[0] < block_group.group_box[0]:
            return True
        elif block.outer_box[1] < block_group.group_box[1]:
            return True
        elif block.outer_box[2] > block_group.group_box[2]:
            return True
        elif block.outer_box[3] > block_group.group_box[3]:
            return True
        return False
