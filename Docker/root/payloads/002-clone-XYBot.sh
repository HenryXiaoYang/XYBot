#!/usr/bin/env bash

sudo -u app bash -c "cd /home/app || exit && git clone https://github.com/HenryXiaoYang/XYBot.git && cd XYBot || exit && git checkout dev"