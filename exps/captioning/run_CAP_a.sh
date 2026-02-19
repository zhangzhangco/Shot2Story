#!/bin/bash 
set -x 

# Set project directory
S2S_DIR="/home/zhangxin/Shot2Story"
cd $S2S_DIR/code

# Setup cache (only if needed)
if [ ! -d ~/.cache/huggingface ]; then
    echo "Extracting BLIP cache..."
    cp ${S2S_DIR}/code/pretrain/BLIP.cache.tar ~/
    cd ~/
    tar xf BLIP.cache.tar
    cd -
fi

# Set environment variables
CONDA_ENV_DIR="/home/zhangxin/miniconda3"
NGPUS=${WORKER_GPU:-1}
WORKER_NUM=${WORKER_NUM:-1}
WORKER_ID=${WORKER_ID:-0}
WORKER_0_HOST=${WORKER_0_HOST:-localhost}
WORKER_0_PORT=${WORKER_0_PORT:-29500}

ports=(${WORKER_0_PORT//,/ })
port=${ports[0]}

CONFIG=lavis/projects/blip2/train/minigpt4_train_audio.yaml

$CONDA_ENV_DIR/envs/shot2story/bin/python -m torch.distributed.run --nproc_per_node=$NGPUS --nnode=$WORKER_NUM --node_rank=$WORKER_ID --master_addr=$WORKER_0_HOST --master_port=$port train.py \
--cfg-path $CONFIG \
--options model.asr_audio=True \
model.visual_target=False \
model.audio_target=True \
run.batch_size_train=4 \
run.batch_size_eval=8 \
run.warmup_steps=200 \
model.llama_model="/mnt/data/Shot2Story/vicuna-7b-v0" \
model.ckpt="${S2S_DIR}/code/pretrain/20k-version/single_shot_audio_av.pth" \
model.prompt_path=prompts/alignment_audio.txt \
model.question_prompt="'The audio transcripts are: {asr}. Describe the audio content of this video in detail.'" \
model.answer_prompt="''" $@