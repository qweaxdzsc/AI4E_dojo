"""本地抽样规则；轮次、随机状态和尾批由 Dojo 数据流管理。"""


def epoch_records(rng, epoch, *, count):
    """每轮产生一次完整排列；用户可在这里改变记录抽样规则。"""
    return rng.permutation(count).tolist()
