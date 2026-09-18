"""耦合场 Euler 更新；回调只接收明确的场状态与流时间。"""


def _update(value, velocity, dt):
    if value.shape != velocity.shape:
        raise ValueError("场速度不能广播到不同形状状态")
    return value + velocity * dt


def synchronous_euler_step(states, time, dt, velocities, order, boundary=None):
    """全部速度读取同一旧状态，计算完成后一起提交。"""
    old = {key: value.clone() for key, value in states.items()}
    output = {key: _update(old[key], velocities[key](old, time), dt) for key in order}
    return boundary(output, time + dt) if boundary else output


def sequential_euler_step(states, time, dt, velocities, order, boundary=None):
    """按场顺序提交；后续速度使用前场新状态。"""
    output = {key: value.clone() for key, value in states.items()}
    for key in order:
        output[key] = _update(output[key], velocities[key](output, time), dt)
        if boundary:
            output = boundary(output, time + dt, field=key)
    return output
