import logging
import yaml
from piaxe import miner
from shared import shared
import time
import yaml
import random

# use fixed seed
random.seed(12345)

# root logger
def setup_logging(log_level, log_filename):
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # If a log filename is provided, also log to a file
    if log_filename:
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def setup_logging_benchy(log_level, log_filename):
    # Create a logger
    logger = logging.getLogger("benchlog")
    logger.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # If a log filename is provided, also log to a file
    file_handler = logging.FileHandler(log_filename, mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def submit_cb(result):
    return True

def testrun(config):
    piaxeMiner = miner.BM1366Miner(config, "bc1q7utau3qcy8hcjze9zsddg839sels90qyup5pv2", shared.BitcoinNetwork.MAINNET)
    piaxeMiner.init()
    piaxeMiner.set_difficulty(512)
    piaxeMiner.set_submit_callback(submit_cb)
    piaxeMiner.start_job(job)

    start_time = time.time()
    while True:
        with piaxeMiner.stats.lock:
            if time.time() - start_time > 15 * 60:
                break
#            if piaxeMiner.stats.valid_shares > 1000:
#                break
#
#            logging.info("left: %d", 1000-piaxeMiner.stats.valid_shares)

        time.sleep(1)

    elapsed = time.time() - start_time

    piaxeMiner.shutdown()

    return piaxeMiner.hash_rate(time_period=elapsed), elapsed

job={
    "job_id": "658dd1e40000ab91",
    "prevhash": "b064adaf22d7ac0ccc834a7fdcf88e55333a985b00010eda0000000000000000",
    "coinb1": "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff2e03ab980c00046b94a165044953f30d0c",
    "coinb2": "0a636b706f6f6c0a2f736f6c6f206361742fffffffff027b441f2700000000160014f717de441821ef890b25141ad41e25867f02bc040000000000000000266a24aa21a9ed6b7aba5e30acf45bf9b8dbd65ce56a1d33bca0ab92f496f77ce9f8b4032cf8cd00000000",
    "merkle_branches": [
        "1eb4b7263d4cff7da31b12d229f5fff449a2b562b0125ad2d5fafd61553bb304",
        "cdf92795c97d3e605fa106b9fa0bb9117396285a17a5a712bfd185394c5e90d1",
        "df24f3058e2b27517e509959480dccd4d01109f302c82457125af158e02588c5",
        "1e325663cf83f80fb8e96a9003b7c6df511ecfae833e80fa4a7ce9821c9043ec",
        "86b131ccc80a41c7b6bb394d0f50172f39e821fd637f8614a3d38287d7dc7e42",
        "02224547803fc9afe7c1e9a54015a0c4165841e34117f08836f6dc7381757611",
        "637669c49a27971f7bb0b8ea9d06135070077c76878a1e4530d982fcc573ba10",
        "7af9a915bd396db4de93991ead88589be7704892d7e581a3b384f7bf7c418e0a",
        "f8e5d51530b415c31bc481b34035edaa820631e22507af682708231a5ea3be77",
        "35607c594892da344cbc0d0714ef3ab6fbdefc2b7c134bf3e73b0ca4563e48bd",
        "b4f6e62611b0be3d0147e39dfdbeb4c872c5b6a27a265b6eddc013573eee84a1",
        "024e88f023fd4f3b1de233e11afe5010af5fc0812dbceffc9cc76d7e65b20735"
    ],
    "version": "20000000",
    "nbits": "1703d869",
    "ntime": "65a1946b",
    "extranonce1": "63d38d65",
    "extranonce2_size": 8,
    "extranonce2": "000000000852f6ca",
    "merkle_root": "fbf0774adc895ea5e33b033fcadbf4f6f22ffd86751f4b12644502f78e8c8edf"
}
job = shared.Job.from_dict(job)

setup_logging(logging.DEBUG, "benchmark.log")
benchlog = setup_logging_benchy(logging.DEBUG, "benchmark_results.log")

# Load configuration from YAML
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

def frequency_generator():
    for clock in range(460, 500, 5):
        yield [(clock, "asic_frequency")]

def enonce2_interval_generator():
    for enonce2_interval in range(3300, 10000, 100):
        yield [(enonce2_interval / 1000.0, "extranonce2_interval")]

def pwm1_generator():
    for pwm1 in range(0, 100, 5):
        yield [(pwm1 / 100.0, "fan_speed_1")]

def dummy_generator():
    while True:
        yield [(0, "unused")]

def chip_sweep_generator():
    for chips in [0, 1, 2, 3]:
        for clock in range(460, 480, 1):
            yield [(clock, "asic_frequency"), ([chips], 'chips_enabled')]

#modifier_func = enonce2_interval_generator
#modifier_func = frequency_generator
#modifier_func = pwm1_generator
modifier_func = dummy_generator
#modifier_func = chip_sweep_generator

for modifications in modifier_func():
    benchlog.info("=========================================================")
    benchlog.info("starting run ...")

    for modified_setting in modifications:
        value = modified_setting[0]
        name = modified_setting[1]
        logging.info(f"modifying {name}, new value: {value}")
        config['qaxe'][name] = value

    benchlog.info(yaml.dump(config['qaxe']))
    hash_rate, elapsed = testrun(config)
    benchlog.info("finished, elapsed: %s, hashrate: %.3fGH/s", elapsed, hash_rate)

