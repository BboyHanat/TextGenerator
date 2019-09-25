from core.provider.textimg.layout.strategy import Strategy
from utils.random_tools import Random
from core.provider.textimg.layout.strategy.HorizontalStrategy import HorizontalStrategy
from core.provider.textimg.layout.strategy.VerticalStrategy import VerticalStrategy
from core.provider.textimg.layout.strategy.HorizontalFlowStrategy import HorizontalFlowStrategy

horizontal_strategy = HorizontalStrategy()
vertical_strategy = VerticalStrategy()
horizontal_flow_strategy = HorizontalFlowStrategy()

strategy_list = [horizontal_strategy, vertical_strategy, horizontal_flow_strategy]


def pick(target: Strategy = None) -> Strategy:
    """
    选择一个策略
    :param target:
    :return:
    """
    if target:
        strategy = target
    else:
        strategy = Random.random_choice_list(strategy_list)
    print(strategy)
    return strategy
