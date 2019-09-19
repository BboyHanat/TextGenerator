import random
import time


class Random(object):
    @staticmethod
    def random_choice(prob_list: list):
        """
        random choice a probability range
        :param prob_list:
        :return:
        """

        prob_sum = np.sum(np.asarray(prob_list))
        assert prob_sum == 1
        prob_range_list = list()
        seek = 0.0
        for p in prob_list:
            prob_range_list.append((seek, p))
            seek += p

        while True:
            seed = time.time()
            random.seed(seed)
            prob = random.uniform(0, 1)
            for index, p_range in enumerate(prob_range_list):
                if p_range[0] < prob <= p_range[1] or p_range[0] <= prob < p_range[1]:
                    return index

    @staticmethod
    def random_prob(prob_thresh):
        """
        get a probability and compare with 'prob_thresh'
        :param prob_thresh:
        :return: True or False
        """
        return prob_thresh > random.uniform(0, 1)

    @staticmethod
    def random_int(low, heigh):
        """
        get list seek
        :param low:
        :param heigh:
        :return:
        """
        return random.randint(low, heigh)
