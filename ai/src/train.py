# src/train.py

import yaml
from training.full_trainer import FullTrainer

with open("src/configs/train.yaml") as f:
    cfg = yaml.safe_load(f)

trainer = FullTrainer(cfg)
trainer.train()
