#!/bin/bash
unset all_proxy ALL_PROXY http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1

cd /home/zhangxin/Shot2Story/code
conda run -n shot2story python -u demo_video.py --cfg-path lavis/projects/blip2/eval/demo.yaml
