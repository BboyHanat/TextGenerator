from core.provider.textimg.layout.strategy import Strategy
from core.provider.textimg.layout.strategy import is_horizontal, is_vertical


class CustomizationStrategy1(Strategy):
    """
    定制策略1：

    左边一个竖直排列 右边一列水平排列
    """

    def logic(self, block_group, next_block) -> bool:
        init_x = block_group.group_box[0]
        init_y = block_group.group_box[1]

        if not block_group.block_list:
            # 放置第一个block  左侧的竖直block
            if is_vertical(next_block):
                next_block.locate_by_outter(init_x, init_y)
                if not self.check_is_out(block_group=block_group, block=next_block):
                    return True
        else:
            # 放置右侧的水平block
            if is_horizontal(next_block):
                first_block = block_group.block_list[0]
                if len(block_group.block_list) > 1:
                    last_block = block_group.block_list[-1]
                    next_y = last_block.outer_box[3] + 1
                else:
                    next_y = init_y
                next_x = first_block.outer_box[2] + 1
                next_block.locate_by_outter(next_x, next_y)
                if not self.check_is_out(block_group=block_group, block=next_block):
                    return True
        return False
