class Strategy:

    def __init__(self):
        pass

    def logic(self, block_group, next_block) -> bool:
        pass


class OnlyOneHorizontalStrategy(Strategy):
    """
    只生成一个水平排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        pass


class OnlyOneVerticalStrategy(Strategy):
    """
    只生成一个竖直排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        if next_block.outer_width > block_group.width:
            return False
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]
        next_x = init_x
        next_y = init_y

        for b in block_group.block_list:
            b = b.outer_box[3]
            if b > next_y:
                next_y = b
        next_y += 1
        if next_y + next_block.outer_height - init_y > block_group.height:
            return False

        next_block.locate_by_outter(next_x, next_y)
        return True


only_one_horizontal_strategy = OnlyOneHorizontalStrategy()
only_one_vertical_strategy = OnlyOneVerticalStrategy()
