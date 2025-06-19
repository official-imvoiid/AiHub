Colab Tool Limitations - Read Before Use

1. AUTOMATIC1111:
   - ❌ Not usable on Colab. Requires high VRAM, And is Heavy on Colab T4 GPUs.
   - Use RunPod for Stable Diffusion.
   - Alternative use Comfyui Which works fine in Google colab free and is widely supported by community.

2. FramePack:
   - ❌ Broken on Colab. Needs newer GPUs (A100/3090+).
   - T4 GPUs are outdated and unsupported.

3. RVC (Voice Conversion):
   - ✅ Use on Colab only with pre-trained .pth models.
   - ❌ Training is not feasible. Use RunPod for that.

4. ImageCaption:
   - ✅ Works for up to 132 images.
   - ⚠️ GPU session ends after that due to limits.

➡️ For These 4 Tools i have Given Runpod version books utilize those.
Use RunPod for anything heavy, training, or production-grade work.
