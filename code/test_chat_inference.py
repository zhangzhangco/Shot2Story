"""
Test using the correct inference path: Chat.answer()
Simplified version without dataset loading
"""

import os

os.environ["NO_PROXY"] = "localhost"

import torch
from lavis.common.config import Config
from lavis.common.registry import registry
from lavis.conversation.conversation import Chat, CONV_VISION_MS

# imports modules for registration
from lavis.datasets.builders import *
from lavis.models import *
from lavis.processors import *


# Load config
class Args:
    cfg_path = "lavis/projects/blip2/eval/demo.yaml"
    gpu_id = 0
    options = None


args = Args()
cfg = Config(args)

print("=" * 80)
print("Loading model...")
print("=" * 80)

model_config = cfg.model_cfg
model_config.device_8bit = args.gpu_id
model_cls = registry.get_model_class(model_config.arch)
model = model_cls.from_config(model_config).to("cuda:{}".format(args.gpu_id))

# Setup processor
pre_cfg = cfg.config.preprocess
vis_processor_cfg = pre_cfg.vis_processor.eval
vis_processor = registry.get_processor_class(vis_processor_cfg.name).from_config(
    vis_processor_cfg
)

# Create Chat instance WITHOUT dataset (we'll manually prepare samples)
chat = Chat(
    model, vis_processor, task=None, dataset=None, device="cuda:{}".format(args.gpu_id)
)

print("\n" + "=" * 80)
print("Model loaded successfully!")
print("=" * 80)

# Test with example video
video_path = "examples/videos/v_-EIsT868Trw.mp4"
print(f"\nTesting with video: {video_path}")

print("\n" + "=" * 80)
print("Step 1: Process video manually")
print("=" * 80)

# Process video
video_tensor = vis_processor(video_path)
print(f"Video tensor shape: {video_tensor.shape}")

# Add batch dimension and move to GPU
video_tensor = video_tensor.unsqueeze(0).cuda()

# Prepare samples dict (mimicking what upload_video_ms_standalone does)
# For simplicity, we'll use a single shot with 4 frames
samples = {
    "video": video_tensor,
    "shot_split": [4],  # Single shot with 4 frames
    "shot_ids": [0],
    "whole_asr": [""],  # Empty ASR for now
}

# Store samples in chat
chat.samples = samples

print("\n" + "=" * 80)
print("Step 2: Build prompt using task.get_prompt() logic")
print("=" * 80)

# Manually build the prompt following the training format
# From minigpt4_multishot_train.yaml:
# prompt_template: '###Human: {} ###Assistant: '
# multishot_prompt: "This is a video with {num_shot} shots. "
# multishot_secondary_prompt: "The {shot_idx_text} shot is "

num_shots = len(samples["shot_split"])
prompt_prefix = f"This is a video with {num_shots} shots. "
prompt_prefix += "The first shot is "
for i in range(samples["shot_split"][0]):
    prompt_prefix += "<Img><ImageHere></Img>"
prompt_prefix += ". "

# Add ASR part
asr_text = samples["whole_asr"][0] if samples["whole_asr"][0] else "no speech"
full_prompt = f"###Human: {prompt_prefix}The audio transcripts are: {asr_text}. Please describe the video in detail. ###Assistant:"

print(f"Prompt: {full_prompt[:200]}...")

# Initialize chat state
chat_state = CONV_VISION_MS.copy()
chat_state.append_message(
    chat_state.roles[0],
    prompt_prefix
    + "The audio transcripts are: "
    + asr_text
    + ". Please describe the video in detail.",
)

print("\n" + "=" * 80)
print("Step 3: Generate answer using Chat.answer()")
print("=" * 80)

try:
    # Generate answer
    summary = chat.answer(
        conv=chat_state,
        num_beams=1,
        temperature=1.0,
        max_new_tokens=300,
        max_length=2048,
    )[0][0]

    print("\n" + "=" * 80)
    print("VIDEO DESCRIPTION:")
    print("=" * 80)
    print(summary)
    print("\n" + "=" * 80)

    # Check quality
    print("\nQuality check:")
    print(f"  Length: {len(summary)} characters")
    print(f"  Unique chars: {len(set(summary))}")

    if len(summary) < 10:
        print("  ⚠️  WARNING: Output too short!")
    elif summary.count("0") > len(summary) * 0.3:
        print("  ⚠️  WARNING: Output contains too many '0's!")
    elif summary.count("9") > len(summary) * 0.3:
        print("  ⚠️  WARNING: Output contains too many '9's!")
    elif len(set(summary)) < 10:
        print("  ⚠️  WARNING: Very low character diversity!")
    else:
        print("  ✓ Output looks reasonable!")

except Exception as e:
    print(f"ERROR during generation: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
