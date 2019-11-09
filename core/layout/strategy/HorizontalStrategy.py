from core.layout.strategy import Strategy


class HorizontalStrategy(Strategy):
    """
    只生成一个水平排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]
        next_x = init_x
        next_y = init_y

        for block in block_group.block_list:
            r = block.outer_box[2]
            if r > next_x:
                next_x = r
        next_x += 1
        next_block.locate_by_outter(next_x, next_y)
        if self.check_is_out(block_group=block_group, block=next_block):
            return False
        return True
