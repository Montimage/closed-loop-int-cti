# Introduction

This detector using Machine Learning to detect abnormal traffic go through a L4S switch.

The detector takes as input the output of the INT-collector. The input can be a csv file or via a communication bus of Redis.


# Installation

- Install `pandas`and the pythons' requirements: 

```bash
sudo apt install python3-pandas
python3 -m pip install -r requirements.txt
```

# Execution

## Input from Redis
```bash
#syntax: python3 main.py <REDIS-IP> <REDIS-PORT>

#For example (the output will be published to redis):
python3 main.py 127.0.0.1 6379
```