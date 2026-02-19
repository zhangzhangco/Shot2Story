#!/bin/bash 
set -x 

# Set project directory
S2S_DIR="/home/zhangxin/Shot2Story"
cd $S2S_DIR/code

# Setup data links (already done, but keep for reference)
# Data is linked at /export/home/.cache/lavis/annotations and /export/home/.cache/lavis/videos

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

CONFIG=lavis/projects/blip2/train/minigpt4_multishot_train.yaml

$CONDA_ENV_DIR/envs/shot2story/bin/python -m torch.distributed.run --nproc_per_node=$NGPUS --nnode=$WORKER_NUM --node_rank=$WORKER_ID --master_addr=$WORKER_0_HOST --master_port=$port train.py \
--cfg-path $CONFIG \
--options run.batch_size_train=1 \
run.batch_size_eval=1 \
model.max_txt_len=500 \
run.warmup_steps=200 \
model.whole_video=True \
model.multishot=True \
model.asr_audio=True \
model.prompt_path=prompts/alignment_av.txt \
run.num_workers=12 \
model.llama_model="/mnt/data/Shot2Story/vicuna-7b-v0" \
model.ckpt="${S2S_DIR}/code/pretrain/20k-version/shot_av_best_epoch.pth" \
model.question_prompt="'In the audio, I hear that: {asr}. Take a look at this video clip and describe what you notice.'" \
model.answer_prompt="''" \
"${@}"
