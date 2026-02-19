# AGENTS.md - Development Guidelines for Shot2Story

This file provides guidance for agentic coding agents working in this repository.

## Project Overview

Shot2Story is a multi-shot video understanding benchmark built on Salesforce's LAVIS library. The codebase is in `/home/zhangxin/Shot2Story/code/` and provides models for video summarization, single-shot captioning, and video QA tasks.

---

## Build and Environment Setup

### Environment Creation
```bash
cd /home/zhangxin/Shot2Story/code
conda env create -f conda_env.yml
conda activate shot2story
```

### Installation
```bash
cd /home/zhangxin/Shot2Story/code
pip install -e .
```

### Pre-commit Hooks
```bash
cd /home/zhangxin/Shot2Story/code
pre-commit install
```

---

## Testing

### Run All Tests
```bash
cd /home/zhangxin/Shot2Story/code
pytest
```

### Run Single Test File
```bash
cd /home/zhangxin/Shot2Story/code
pytest tests.py
```

###/models/test_blip Run Single Test
```bash
cd /home/zhangxin/Shot2Story/code
pytest tests/models/test_blip.py::TestBlip::test_caption
```

### Run with Verbose Output
```bash
cd /home/zhangxin/Shot2Story/code
pytest -v
```

---

## Linting and Code Quality

### Pre-commit Checks (Runs black, flake8, and pre-commit-hooks)
```bash
cd /home/zhangxin/Shot2Story/code
pre-commit run --all-files
```

### Black (Format Code)
```bash
cd /home/zhangxin/Shot2Story/code
black <file_or_directory>
```

### Flake8 (Lint)
```bash
cd /home/zhangxin/Shot2Story/code
flake8 <file_or_directory>
```

---

## Code Style Guidelines

### General Rules
- Python 3.8.16 (see `conda_env.yml` for exact version)
- Follow existing code patterns in the codebase
- Keep lines under 120 characters when practical

### Imports
- Standard library imports first, then third-party, then local
- Use absolute imports from `lavis` package
- Example:
  ```python
  import logging
  import os

  import numpy as np
  import torch
  import torch.nn as nn
  from omegaconf import OmegaConf

  from lavis.models import load_model
  from lavis.common.dist_utils import is_dist_avail_and_initialized
  ```

### Naming Conventions
- Classes: `CamelCase` (e.g., `BaseModel`, `BlipCaption`)
- Functions/methods: `snake_case` (e.g., `load_checkpoint`, `from_pretrained`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_IMAGE_SIZE`)
- Private methods: prefix with underscore (e.g., `_setup_model`)

### Type Hints
- Use type hints for function parameters and return values when beneficial
- Prefer `torch.device` over strings for device specification

### Error Handling
- Use specific exception types (e.g., `RuntimeError`, `ValueError`)
- Include descriptive error messages

### Docstrings
- Use Google-style docstrings for public methods
- Include description, args, and return types

### File Headers
Include license header in new files:
```python
"""
 Copyright (c) 2022, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""
```

---

## Running the Demo

**IMPORTANT**: Agents should NOT run the demo directly. Always ask the user to run it.

The demo is a long-running Gradio web application that requires:
- User interaction through a web browser
- Continuous process monitoring
- Proper proxy/network configuration
- Manual termination when done

### Demo Command (for user to run)

```bash
cd /home/zhangxin/Shot2Story/code && \
source ~/miniconda3/etc/profile.d/conda.sh && \
conda activate shot2story && \
unset all_proxy ALL_PROXY http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && \
export PYTHONUNBUFFERED=1 && \
CUDA_VISIBLE_DEVICES=0 python -u demo_video.py --cfg-path lavis/projects/blip2/eval/demo.yaml
```

**What the demo does**:
1. Loads the VideoMiniGPT4 model (~6GB VRAM)
2. Starts a Gradio web interface (usually on http://127.0.0.1:7860)
3. Allows users to upload videos and ask questions
4. Generates video summaries and answers based on visual content

**Agent responsibilities**:
- ✅ Prepare code and fix bugs
- ✅ Provide the command to the user
- ❌ Do NOT run the demo yourself
- ❌ Do NOT try to monitor or interact with the running demo

---

## Project Structure
```
code/
├── lavis/              # Core library (models, datasets, processors)
├── projects/           # Project-specific implementations
├── tests/              # Test suite (pytest)
├── run_scripts/        # Training/inference scripts
├── examples/           # Example scripts
├── demo_video.py       # Gradio demo
├── train.py            # Training entry point
├── evaluate.py         # Evaluation entry point
└── setup.py            # Package setup
```

---

## Key Libraries
- **PyTorch**: Deep learning framework (v2.0.1)
- **transformers**: Hugging Face transformers (v4.28.1)
- **salesforce-lavis**: Base vision-language library
- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Linter
- **omegaconf**: Configuration management
- **gradio**: Demo UI

---

## Notes for Agents
- Always run `pre-commit run --all-files` before committing
- Test changes with `pytest` before submitting
- Use absolute paths when referencing project files
- The project uses conda environment named `shot2story`
- GPU is required for most model operations (CUDA)
