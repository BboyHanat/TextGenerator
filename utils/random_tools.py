import random
import time


class Random(object):
    @staticmethod
    def random_choice(prob_list: list, seed=None):
        """
        random choice a probability range
        :param prob_list:
        :param seed:
        :return:
        """
        prob_sum = sum(prob_list)
        prob_range_list = list()
        seek = 0.0
        for p in prob_list:
            prob_range_list.append((seek, seek + p))
            seek += p

        while True:
            random.seed(seed)
            prob = random.uniform(0, prob_sum)
            for index, p_range in enumerate(prob_range_list):
                if p_range[0] < prob <= p_range[1] or p_range[0] <= prob < p_range[1]:
                    return index

    @staticmethod
    def random_prob(prob_thresh: float):
        """
        get a probability and compare with 'prob_thresh'
        :param prob_thresh:
        :return: True or False
        """
        seed = time.time()
        random.seed(seed)
        return prob_thresh > random.uniform(0, 1)

    @staticmethod
    def random_int(low: int, high: int, seed=None):
        """
        get a integer number in range (low, high)
        :param low:
        :param high:
        :param seed:
        :return:
        """
        random.seed(seed)
        return random.randint(low, high)

    @staticmethod
    def random_bool(seed=None):
        random.seed(seed)
        return bool(random.getrandbits(1))

    @staticmethod
    def random_float(low: float, high: float):
        """
        get a float number in range (low, high)
        :param low:
        :param high:
        :return:
        """
        seed = time.time()
        random.seed(seed)
        return random.uniform(low, high)

    @staticmethod
    def random_choice_list(choice_list, seed=None):
        """

        :return:
        """
        random.seed(seed)
        return random.choice(choice_list)

    @staticmethod
    def shuffle(shuffle_list: list, seed=None):
        random.seed(seed)
        return random.shuffle(shuffle_list)
