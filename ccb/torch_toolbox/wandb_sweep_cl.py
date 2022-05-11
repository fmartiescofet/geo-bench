#!/usr/bin/env python
"""
Trains the model using job information contained in the current directory.
Expects to find files "hparams.json" and "task_specs.json".
Usage: trainer.py --model-generator path/to/my/model/generator.py
"""
import argparse

from ccb.torch_toolbox.dataset import DataModule
from ccb.experiment.experiment import get_model_generator, Job
import pytorch_lightning as pl


def train(args):
    
    model_gen = get_model_generator(args.model_generator)
    job = Job(args.job_dir)

    hparams = job.hparams
    seed = hparams.get("seed", None)
    if seed is not None:
        pl.seed_everything(seed, workers=True)

    model = model_gen.generate(job.task_specs, hparams)
    datamodule = DataModule(
        job.task_specs,
        batch_size=hparams["batch_size"],
        num_workers=hparams["num_workers"],
        train_transform=model_gen.get_transform(job.task_specs, hparams, train=True),
        eval_transform=model_gen.get_transform(job.task_specs, hparams, train=False),
        collate_fn=model_gen.get_collate_fn(job.task_specs, hparams),
    )
    logger_type = hparams.get("logger", None)
    loggers = [pl.loggers.CSVLogger(str(job.dir), name="lightning_logs")]
    logger_type = "wandb"
    if logger_type is None:
        logger_type = ""
    if logger_type.lower() == "wandb":
        loggers.append(
            pl.loggers.WandbLogger(project="ccb", name=str(job_dir) + "/" + hparams["backbone"], save_dir=str(job.dir))
        )
    elif logger_type.lower() == "csv":
        pass  # csv in in loggers by default
    else:
        raise ValueError(f"Logger type ({logger_type}) not recognized.")

    trainer = pl.Trainer(
        # gpus=hparams.get("n_gpus", 1),
        gpus=1,
        max_epochs=hparams["max_epochs"], # number of epochs
        max_steps=hparams.get("train_iters", None), # num of optimzing steps
        limit_val_batches=hparams.get("limit_val_batches", 1.0),
        limit_test_batches=hparams.get("limit_val_batches", 1.0),
        val_check_interval=hparams.get("val_check_interval", 1.0),
        accelerator=hparams.get("accelerator", None),
        deterministic=hparams.get("deterministic", False),
        progress_bar_refresh_rate=0,
        logger=loggers,
    )
    trainer.fit(model, datamodule)
    trainer.test(model, datamodule)

def start():
    # Command line arguments
    parser = argparse.ArgumentParser(
        prog="wandb_sweep_cl.py",
        description="Conducts wandb sweep.",
    )
    parser.add_argument(
        "--model_generator",
        help="Module name that defines a model generator. Must be in PYTHONPATH and expects a model_generator variable to exist.",
        required=True,
    )
    parser.add_argument(
        "--job_dir",
        help="Path to the job.",
        required=True,
    )
    args = parser.parse_args()
    print(args)
    train(args)
    
if __name__ == "__main__":
    start()