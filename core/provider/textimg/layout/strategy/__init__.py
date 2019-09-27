def check_two_box_is_overlap(a_box, b_box):
    """
    检查两个区域是否有交集
    :param a_box:
    :param b_box:
    :return:
    """
    in_h = min(a_box[2], b_box[2]) - max(a_box[0], b_box[0])
    in_w = min(a_box[3], b_box[3]) - max(a_box[1], b_box[1])
    inter = 0 if in_h < 0 or in_w < 0 else in_h * in_w
    return inter > 0


class Strategy:

    def __init__(self):
        pass

    def __repr__(self):
        return str(self.__class__.__name__)

    def name(self):
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

    @staticmethod
    def check_is_overlap(block_a, block_b):
        """
        检查两个block是否有覆盖情况
        :param block_a:
        :param block_b:
        :return:
        """
        a_box = block_a.outer_box
        b_box = block_b.outer_box
        return check_two_box_is_overlap(a_box, b_box)

    @staticmethod
    def check_has_overlap(block_group, block):
        """
        检查block是否与block_group中的block存在重叠现象
        :param block_group:
        :param block:
        :return:
        """
        for child_block in block_group.block_list:
            is_overlap = Strategy.check_is_overlap(child_block, block)
            if is_overlap:
                return True
        return False
