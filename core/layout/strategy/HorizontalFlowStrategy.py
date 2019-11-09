from core.layout.strategy import Strategy


class HorizontalFlowStrategy(Strategy):
    """
    生成一个水平流式排布的文本贴图布局
    """

    def logic(self, block_group, next_block) -> bool:
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]
        next_x = init_x
        next_y = init_y

        max_b = 0
        lasb_block = None

        for block in block_group.block_list:
            b = block.outer_box[3]
            if max_b < b:
                max_b = b

            lasb_block = block

        if lasb_block:
            next_x = lasb_block.outer_box[2] + 1
            next_y = lasb_block.outer_box[1]

        next_block.locate_by_outter(next_x, next_y)
        if self.check_is_out(block_group=block_group, block=next_block):
            next_x = init_x
            next_y = max_b + 1
            next_block.locate_by_outter(next_x, next_y)
            if self.check_is_out(block_group=block_group, block=next_block):
                return False
        return True
