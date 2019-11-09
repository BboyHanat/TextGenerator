from core.layout.strategy import Strategy


class VerticalFlowStrategy(Strategy):
    """
    生成一个竖直流式排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]
        next_x = init_x
        next_y = init_y

        max_r = 0
        lasb_block = None

        for block in block_group.block_list:
            r = block.outer_box[2]
            if max_r < r:
                max_r = r

            lasb_block = block

        if lasb_block:
            next_x = lasb_block.outer_box[0]
            next_y = lasb_block.outer_box[3] + 1

        next_block.locate_by_outter(next_x, next_y)
        if self.check_is_out(block_group=block_group, block=next_block):
            next_x = max_r + 1
            next_y = init_y
            next_block.locate_by_outter(next_x, next_y)
            if self.check_is_out(block_group=block_group, block=next_block):
                return False
        return True
