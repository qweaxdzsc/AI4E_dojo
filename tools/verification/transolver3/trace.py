"""只读观察原入口实际输入与轮次提交，不替代参考训练循环。"""

import random
import shutil

import torch

from ai4e_core.abilities.data.validate.fingerprint import fingerprint


def install(training, output):
    """包装已有调用边界，摘要计算不消费参考随机流。"""
    trace = {"initialization": None, "inputs": [], "transport_corrections": []}
    build = training.build_training_model
    save = training.atomic_torch_save
    dataset = training.RandomChunkDataset
    read = dataset.__getitem__
    load_checkpoint = training.load_checkpoint

    def load(path, device):
        state = load_checkpoint(path, device)
        # torch 的 CPU 生成器只接受 CPU ByteTensor；不改变保存的随机状态值。
        rng = state["torch_random_state"]
        if rng.device.type != "cpu":
            state["torch_random_state"] = rng.cpu()
            trace["transport_corrections"].append("torch_random_state_to_cpu")
        if state.get("cuda_random_state") is not None:
            state["cuda_random_state"] = [value.cpu() for value in state["cuda_random_state"]]
        return state

    def construct(config):
        model = build(config)
        trace["initialization"] = fingerprint(model.state_dict())
        return model

    def item(self, index):
        rng = random.Random()
        rng.setstate(random.getstate())
        part, offset = rng.randrange(self.chunk_count), rng.randrange(4)
        features, labels, name = read(self, index)
        ids = torch.arange(part, self.manifest["point_count"], self.chunk_count)[offset::4][None]
        trace["inputs"].append(
            {
                "identity": [
                    {
                        "sample": name,
                        "index": index,
                        "chunk": part,
                        "offset": offset,
                        "partition": "train",
                    }
                ],
                "digest": fingerprint(
                    {
                        "inputs": {"features": features[None]},
                        "targets": {"fields": labels[None]},
                        "ids": ids,
                    }
                ),
            }
        )
        return features, labels, name

    def checkpoint(path, payload):
        save(path, payload)
        if path.name == "latest.pt":
            shutil.copyfile(path, path.with_name(f"epoch-{payload['epoch'] + 1}.pt"))

    training.build_training_model = construct
    training.load_checkpoint = load
    training.atomic_torch_save = checkpoint
    dataset.__getitem__ = item
    return trace
