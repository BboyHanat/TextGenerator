from core.provider.textimg.layout.strategy import Strategy


class VerticalStrategy(Strategy):
    """
    只生成一个竖直排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]
        next_x = init_x
        next_y = init_y

        for block in block_group.block_list:
            b = block.outer_box[3]
            if b > next_y:
                next_y = b
        next_y += 1
        next_block.locate_by_outter(next_x, next_y)
        if self.check_is_out(block_group=block_group, block=next_block):
            return False
        return True
