# Shot2Story 调试与修复总结

## 项目信息
- **项目**: Shot2Story - 多镜头视频理解基准
- **模型**: VideoMiniGPT4 (BLIP2 + Vicuna-7B v0)
- **日期**: 2026-02-19

---

## 问题描述

模型生成完全无意义的乱码输出，例如：
```
bo / a, -- 2/349999999999999999999999999...
```

---

## 根本原因

**使用了错误的推理路径**，绕过了正确的prompt格式化和处理流程。

### 错误做法
直接调用 `model.llama_model.generate()`，导致：
- ❌ 缺少正确的prompt模板（`###Human: ... ###Assistant:`）
- ❌ 缺少停止标准（`###` token）
- ❌ 缺少shot信息和frame placeholders的正确处理

### 正确做法
使用 `Chat.answer()` 方法，它会：
- ✅ 正确格式化prompt
- ✅ 处理多镜头信息
- ✅ 应用停止标准
- ✅ 正确拼接视觉和文本embeddings

---

## 关键发现

### 1. 投影层输出norm不是bug
- 投影层输出norm ~184 是**正常的**
- 之前错误地与词表embedding norm (1.23) 比较
- 应该与LLM内部hidden state比较
- LLM输入范围 `[-25.5, 27.5]` 是合理的

### 2. Checkpoint加载正确
- ✅ llama_proj和Qformer权重完全匹配
- ✅ 804个missing keys都是LLM权重（预期行为，使用预训练Vicuna）
- ✅ 无critical keys缺失

### 3. Vicuna版本正确
- 论文使用：Vicuna v0-7B
- 我们使用：`helloollel/vicuna-7b` (标准v0合并版)
- ✅ Embedding统计与v1.3几乎完全一致

---

## 修复内容

### Commit 1: 代码格式化和可选导入
```
8119935 - chore: code formatting and fix optional imports
```
- 使用black格式化代码
- 使HDFS/KVReader/nlgeval导入可选
- 添加Whisper lazy loading
- 更新TransNetV2权重路径

### Commit 2: 使用正确的推理路径
```
48900c8 - fix: use correct inference path with Chat.answer()
```
- 修改为使用 `Chat.answer()` 而不是直接调用 `generate()`
- 更新demo.yaml使用Vicuna v0-7B路径
- 添加 `test_chat_inference.py` 作为正确示例

**结果**: 从乱码变为连贯的1097字符视频描述

### Commit 3: 清理测试文件
```
3afa478 - chore: cleanup test files and add .gitignore
```
- 删除6个无用的调试测试文件
- 创建 `.gitignore` 排除大文件
- 保留 `test_chat_inference.py` 和 `run_demo.sh`

### Commit 4: 修复路径和错误处理
```
c20e829 - fix: update paths and handle dataset errors in demo
```
- 更新cache_root: `/export/home/.cache/lavis` → `/mnt/data/Shot2Story`
- 修复NumPy数组不可写警告（添加 `np.copy()`）
- 添加dataset为None时的错误处理
- 修复Gradio API兼容性（移除 `enable_queue`）

### Commit 5: 显示视频摘要
```
7ea486d - fix: display video summary in chatbot after upload
```
- 修复chatbot不显示生成结果的问题
- 在 `upload_vid` 返回值中添加chatbot输出
- 现在会显示初始问答对

### Commit 6: 使用用户输入的问题
```
73092e9 - fix: use user's question from text input instead of hardcoded question
```
- 读取用户在文本框中输入的实际问题
- 不再硬编码"Please describe this video in detail."
- 文本框从一开始就可交互
- 正确显示用户问题和针对性回答

---

## 最终工作流程

1. **上传视频** → 选择视频文件
2. **输入问题** → 在User文本框输入问题（如"What is the woman doing?"）
3. **可选设置**:
   - Manual shots: 手动指定镜头时间戳或选择"Automatic detection"
   - Story generation temperature: 0.1（准确）到 2.0（创意）
4. **点击按钮** → "Upload & Start Chat"
5. **查看结果** → Chatbot显示用户问题和模型回答
6. **继续对话** → 可以继续提问

---

## 技术细节

### 模型架构
```
VIT (EVA-CLIP-G) → Q-Former → Linear Projection (llama_proj) → Vicuna-7B
```

### 关键组件
- **Shot Detection**: TransNetV2（自动）或手动指定
- **ASR**: Whisper large-v2（lazy loading）
- **LLM**: Vicuna-7B v0 (frozen)
- **Trainable**: Q-Former + llama_proj

### Checkpoint信息
- 路径: `pretrain/20k-version/sum_shot_best_epoch.pth`
- 训练轮数: 11 epochs
- 包含: Q-Former (255 keys) + llama_proj (2 keys) + query_tokens (1 key)

---

## 测试结果

### 测试视频: v_-EIsT868Trw.mp4
**生成描述**（部分）:
```
This is a video that shows a woman sitting in a glass cube suspended 
high above the ground. She is wearing a grey shirt and black leggings. 
The video then shifts to a group of people standing on a pillar near a 
railroad track...
```

- ✅ 1097个字符
- ✅ 语义连贯
- ✅ 语法正确
- ✅ 描述详细

---

## 重要经验教训

1. **不要直接调用底层generate方法**
   - 必须使用封装好的推理接口（如 `Chat.answer()`）
   - 底层方必要的处理步骤

2. **Norm比较要用正确的基线**
   - 不要拿投影层输出和词表embedding比较
   - 应该和LLM内部激活分布比较

3. **Checkpoint加载要严格验证**
   - 检查missing keys是否critical
   - 验证关键模块（llama_proj, Qformer）是否真正加载

4. **推理流程要与训练一致**
   - Prompt模板必须完全匹配
   - Shot信息、ASR字段、停止标准都要对齐

---

## 文件清单

### 保留的文件
- `test_chat_inference.py` - 正确的推理示例
- `run_demo.sh` - Demo启动脚本
- `.gitignore` - 排除大文件和临时文件

### 关键配置文件
- `lavis/projects/blip2/eval/demo.yaml` - 模型配置
- `lavis/configs/default.yaml` - 缓存路径配置

### 修改的核心文件
- `demo_video.py` - Gradio界面
- `lavis/conversation/conversation.py` - Chat类和推理逻辑
- `lavis/models/blip2_models/video_minigpt4.py` - 模型定义

---

## 启动命令

```bash
cd /home/zhangxin/Shot2Story/code && \
source ~/miniconda3/etc/profile.d/conda.sh && \
conda activate shot2story && \
unset all_proxy ALL_PROXY http_proxy https_proxy HTTP_PROXY HTTPS_PROXY && \
export PYTHONUNBUFFERED=1 && \
CUDA_VISIBLE_DEVICES=0 python -u demo_video.py --cfg-path lavis/projects/blip2/eval/demo.yaml
```

---

## 环境信息

- Python: 3.8.16
- PyTorch: 2.0.1
- transformers: 4.28.1
- Vicuna: v0-7B (helloollel/vicuna-7b)
- CUDA: 可用

---

## 总结

通过系统性的调试和专家建议，成功定位并修复了模型生成乱码的问题。关键是使用正确的推理路径，而不是直接调用底层A常工作，能够准确回答用户关于视频内容的问题。

**状态**: ✅ 完全修复，功能正常
