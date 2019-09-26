from core.provider.textimg.layout.strategy import Strategy
from utils.random_tools import Random
from core.provider.textimg.layout.strategy.HorizontalStrategy import HorizontalStrategy
from core.provider.textimg.layout.strategy.VerticalStrategy import VerticalStrategy
from core.provider.textimg.layout.strategy.HorizontalFlowStrategy import HorizontalFlowStrategy
from core.provider.textimg.layout.strategy.VerticalFlowStrategy import VerticalFlowStrategy
from core.provider.textimg.layout.strategy.RandomPasteStrategy import RandomPasteStrategy

horizontal_strategy = HorizontalStrategy()
vertical_strategy = VerticalStrategy()
horizontal_flow_strategy = HorizontalFlowStrategy()
vertical_flow_strategy = VerticalFlowStrategy()
random_paste_strategy = RandomPasteStrategy()

strategy_list = [
    horizontal_strategy,
    vertical_strategy,
    horizontal_flow_strategy,
    vertical_flow_strategy,
    random_paste_strategy
]


def pick(target: Strategy = None) -> Strategy:
    """
    选择一个策略
    :param target:
    :return:
    """
    # todo: 更智能的策略选择
    if target:
        strategy = target
    else:
        strategy = Random.random_choice_list(strategy_list)
    print(strategy)
    return strategy
