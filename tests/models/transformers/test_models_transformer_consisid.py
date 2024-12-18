# coding=utf-8
# Copyright 2024 HuggingFace Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import torch

from diffusers import ConsisIDTransformer3DModel
from diffusers.utils.testing_utils import (
    enable_full_determinism,
    torch_device,
)

from ..test_modeling_common import ModelTesterMixin


enable_full_determinism()


class ConsisIDTransformerTests(ModelTesterMixin, unittest.TestCase):
    model_class = ConsisIDTransformer3DModel
    main_input_name = "hidden_states"
    uses_custom_attn_processor = True

    @property
    def dummy_input(self):
        batch_size = 1
        num_channels = 16
        num_frames = 13
        height = 60
        width = 90
        embedding_dim = 4096
        sequence_length = 226

        hidden_states = torch.randn((batch_size, num_frames, num_channels, height, width)).to(torch_device)
        encoder_hidden_states = torch.randn((batch_size, sequence_length, embedding_dim)).to(torch_device)
        timestep = torch.randint(0, 1000, size=(batch_size,)).to(torch_device)
        id_vit_hidden = [torch.ones([batch_size, 577, 1024]).to(torch_device)] * 5
        id_cond = torch.ones(batch_size, 1280).to(torch_device)

        return {
            "hidden_states": hidden_states,
            "encoder_hidden_states": encoder_hidden_states,
            "timestep": timestep,
            "id_vit_hidden": id_vit_hidden,
            "id_cond": id_cond,
        }

    @property
    def input_shape(self):
        return (1, 13, 60, 90)

    @property
    def output_shape(self):
        return (13, 16, 60, 90)

    def prepare_init_args_and_inputs_for_common(self):
        init_dict = {
            "attention_head_dim": 64,
            "cross_attn_interval": 2,
            "dropout": 0.0,
            "flip_sin_to_cos": True,
            "freq_shift": 0,
            "in_channels": 16,
            "out_channels": 16,
            "is_kps": False,
            "is_train_face": True,
            "LFE_heads": 16,
            "LFE_num_tokens": 32,
            "LFE_output_dim": 2048,
            "local_face_scale": 1.0,
            "max_text_seq_length": 226,
            "num_attention_heads": 48,
            "num_layers": 2,
            "patch_size": 2,
            "sample_frames": 49,
            "sample_height": 60,
            "sample_width": 90,
            "text_embed_dim": 4096,
            "time_embed_dim": 512,
        }
        inputs_dict = self.dummy_input
        return init_dict, inputs_dict

    def test_gradient_checkpointing_is_applied(self):
        expected_set = {"ConsisIDTransformer3DModel"}
        super().test_gradient_checkpointing_is_applied(expected_set=expected_set)