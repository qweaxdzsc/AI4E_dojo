"""WDNO 作者数值定义；来源和抽取记录见 model/wdno/source.json。"""
import torch

def mse_deviation(u1, u2, report_all=False):
    u1, u2 = u1.clone(), u2.clone()
    if report_all:
        mse = (u1 - u2).square().mean((-1, -2))
        mae = (u1 - u2).abs().mean((-1, -2))
        ep = 1e-5
        return mse, mae, mse / (u2 + ep).square().mean(), mae / (u2 + ep).abs().mean()
    return (u1 - u2).square().mean((-1, -2))
