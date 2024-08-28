from utils import SCRIPT_PATH
from typing import Dict, Union
import os.path as osp
import transformers
import torch
import os

class Model:
    def __init__(self, project_path: str, device: str) -> None:
        self.root_path = osp.join(SCRIPT_PATH, osp.basename(project_path))
        os.makedirs(self.root_path, exist_ok = True)
        self.src = '/usr/bin/todo-script'
        self.dataset_path: str = osp.join(self.src, 'dataset', osp.basename(self.root_path), 'data.index')
        self.device = device

    def create_prompt(self, data: Dict[str, Union[int, str]]) -> str:
        #TODO
        return

    def __call__(self, data: Dict[str, Union[int, str]]) -> str:
        prompt: str = self.create_prompt(data)
        return self.parsePrompt(prompt)

    def parsePrompt(self, prompt: str) -> str:
        pipeline = transformers.pipeline(
            "text-generation",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=self.device,
        )
        out = pipeline(
            prompt,
            top_k = 50,
            top_p = 0.95,
            temperature = 0.7,
            num_return_sequences = 1,
        )

        return out[0]['generated_text']


