<!--Copyright 2024 The HuggingFace Team. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
-->
# ConsisID

[ConsisID](https://github.com/PKU-YuanGroup/ConsisID) is an identity-preserving text-to-video generation model, which keep the face consistent in the generated video by frequency decomposition. There is a [video](https://www.youtube.com/watch?v=PhlgC-bI5SQ) show its powerful function. It has the following features:

​	🔥 **Frequency Decomposition**: The characteristics of the DiT architecture are analyzed from the frequency domain perspective, and based on these characteristics, a reasonable control information injection method is designed.

​	🔥 **Consistency Training Strategy**: We propose a coarse-to-fine training strategy, dynamic masking loss, and dynamic cross-face loss, which further enhance the model's generalization ability and identity preservation performance.

​	🔥 **Inference Without Fine-Tuning**: Previous methods required case-by-case fine-tuning of the input ID before inference, leading to significant time and computational costs. In contrast, consisid is tuning-free.

For more information, please refer to the [paper](https://arxiv.org/abs/2411.17440). This guide will walk you through using ConsisID for use cases.

## Load Model Checkpoints
Model weights may be stored in separate subfolders on the Hub or locally, in which case, you should use the [`~DiffusionPipeline.from_pretrained`] method.


```python
import torch
from diffusers import ConsisIDPipeline
from diffusers.pipelines.consisid.util_consisid import prepare_face_models, process_face_embeddings_infer
from huggingface_hub import snapshot_download

# Download ckpts
snapshot_download(repo_id="BestWishYsh/ConsisID-preview", local_dir="BestWishYsh/ConsisID-preview")

# Load face helper model to preprocess input face image
face_helper_1, face_helper_2, face_clip_model, face_main_model, eva_transform_mean, eva_transform_std = prepare_face_models("BestWishYsh/ConsisID-preview", device="cuda", dtype=torch.bfloat16)

# Load consisid base model
pipe = ConsisIDPipeline.from_pretrained("BestWishYsh/ConsisID-preview", torch_dtype=torch.bfloat16)
pipe.to("cuda")
```

## Identity-Preserving Text-to-Video
For identity-preserving text-to-video, pass a text prompt and an image contain clear face (e.g., preferably half-body or full-body). By default, ConsisID generates a 720x480 video for the best results.

```python
from diffusers.utils import export_to_video

prompt = "A woman adorned with a delicate flower crown, is standing amidst a field of gently swaying wildflowers. Her eyes sparkle with a serene gaze, and a faint smile graces her lips, suggesting a moment of peaceful contentment. The shot is framed from the waist up, highlighting the gentle breeze lightly tousling her hair. The background reveals an expansive meadow under a bright blue sky, capturing the tranquility of a sunny afternoon."
image = "https://github.com/PKU-YuanGroup/ConsisID/blob/main/asserts/example_images/1.png?raw=true"

id_cond, id_vit_hidden, image, face_kps = process_face_embeddings_infer(face_helper_1, face_clip_model, face_helper_2, eva_transform_mean, eva_transform_std, face_main_model, "cuda", torch.bfloat16, image, is_align_face=True)
is_kps = getattr(pipe.transformer.config, 'is_kps', False)
kps_cond = face_kps if is_kps else None

video = pipe(image=image, prompt=prompt, use_dynamic_cfg=False, id_vit_hidden=id_vit_hidden, id_cond=id_cond, kps_cond=kps_cond, generator=torch.Generator("cuda").manual_seed(42))
export_to_video(video.frames[0], "output.mp4", fps=8)
```
<table>
  <tr>
    <th style="text-align: center;">Face Image</th>
    <th style="text-align: center;">Video</th>
    <th style="text-align: center;">Description</th
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/be0257b5-9d90-47ba-93f4-5faf78fd1859" style="height: auto; width: 600px;"></td>
    <td><img src="https://github.com/user-attachments/assets/f0e2803c-7214-4463-afd8-b28c0cd87c64" style="height: auto; width: 2000px;"></td>
    <td>The video features a woman in exquisite hybrid armor adorned with iridescent gemstones, standing amidst gently falling cherry blossoms. Her piercing yet serene gaze hints at quiet determination, as a breeze catches a loose strand of her hair ......</td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/c1418804-3e5b-4f8b-87f1-25d4ddeee99e" style="height: auto; width: 600px;"></td>
    <td><img src="https://github.com/user-attachments/assets/3491e75c-e01a-41d3-ae01-0c2535b7fa81" style="height: auto; width: 2000px;"></td>
    <td>The video features a baby wearing a bright superhero cape, standing confidently with arms raised in a powerful pose. The baby has a determined look on their face, with eyes wide and lips pursed in concentration, as if ready to take on a challenge ......</td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/2c4ea113-47cd-4295-b643-a10e2a566823" style="height: auto; width: 600px;"></td>
    <td><img src="https://github.com/user-attachments/assets/2ffb154f-23dc-4314-9976-95c0bd16810b" style="height: auto; width: 2000px;;"></td>
    <td>The video captures a boy walking along a city street, filmed in black and white on a classic 35mm camera. His expression is thoughtful, his brow slightly furrowed as if he's lost in contemplation. The film grain adds a textured ......</td>
  </tr>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/d48cb0be-0a64-40fa-8f86-ac406548d592" style="height: auto; width: 600px;"></td>
    <td><img src="https://github.com/user-attachments/assets/9eb298a3-4c2a-407e-b73b-32f88895df22" style="height: auto; width: 2000px;;"></td>
    <td>The video features a man standing at an easel, focused intently as his brush dances across the canvas. His expression is one of deep concentration, with a hint of satisfaction as each brushstroke adds color and form ......</td>
  </tr>
</table>

## Citation

If you find consisid useful in your research, please consider giving a star and citation.

```BibTeX
@article{yuan2024identity,
  title={Identity-Preserving Text-to-Video Generation by Frequency Decomposition},
  author={Yuan, Shenghai and Huang, Jinfa and He, Xianyi and Ge, Yunyuan and Shi, Yujun and Chen, Liuhan and Luo, Jiebo and Yuan, Li},
  journal={arXiv preprint arXiv:2411.17440},
  year={2024}
}
```
