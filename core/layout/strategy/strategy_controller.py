from core.layout.strategy import Strategy
from utils.random_tools import Random
from core.layout.strategy.HorizontalStrategy import HorizontalStrategy
from core.layout.strategy.VerticalStrategy import VerticalStrategy
from core.layout.strategy.HorizontalFlowStrategy import HorizontalFlowStrategy
from core.layout.strategy.VerticalFlowStrategy import VerticalFlowStrategy
from core.layout.strategy.RandomPasteStrategy import RandomPasteStrategy
from core.layout.strategy.CustomizationStrategy1 import CustomizationStrategy1
from service import conf
from utils import log

horizontal_strategy = HorizontalStrategy()
vertical_strategy = VerticalStrategy()
horizontal_flow_strategy = HorizontalFlowStrategy()
vertical_flow_strategy = VerticalFlowStrategy()
random_paste_strategy = RandomPasteStrategy()
customization_strategy_1 = CustomizationStrategy1()

strategy_list = [
    horizontal_strategy,
    vertical_strategy,
    horizontal_flow_strategy,
    vertical_flow_strategy,
    random_paste_strategy,
    customization_strategy_1
]


def get_strategy_by_name(name):
    for strategy in strategy_list:
        if strategy.__class__.__name__ == name:
            return strategy
    return None


def pick() -> Strategy:
    """
    选择一个策略
    :return:
    """
    layout_strategy_conf = dict(conf['layout_strategy_conf'])
    strategy_list = list(layout_strategy_conf.keys())
    strategy_values = list(layout_strategy_conf.values())
    index = Random.random_choice(list(strategy_values))

    strategy_name = strategy_list[index]
    strategy = get_strategy_by_name(strategy_name)

    log.info("pick strategy: {strategy}".format(strategy=strategy_name))
    return strategy
