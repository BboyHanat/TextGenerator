from core.layout.strategy import Strategy
from utils.random_tools import Random


class RandomPasteStrategy(Strategy):
    """
    随机粘贴策略
    """
    # 随机种子必须设置为空 否则每次都会贴在同一区域，导致重叠而帖失败
    seed = None

    def logic(self, block_group, next_block) -> bool:
        gbl = block_group.group_box[0]
        gbt = block_group.group_box[1]
        gbr = block_group.group_box[2]
        gbb = block_group.group_box[3]

        if gbr - next_block.outer_width < gbl or gbb - next_block.outer_height < gbt:
            return False

        x = Random.random_int(gbl, gbr - next_block.outer_width, seed=self.seed)
        y = Random.random_int(gbt, gbb - next_block.outer_height, seed=self.seed)

        next_block.locate_by_outter(x, y)

        is_out = self.check_is_out(block_group=block_group, block=next_block)
        has_overlap = self.check_has_overlap(block_group=block_group, block=next_block)
        is_ok = not is_out and not has_overlap

        if is_ok:
            return True
        return False
