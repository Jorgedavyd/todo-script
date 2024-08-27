import transformers
import torch
from typing import Dict, Union
import os.path as osp
from utils import SCRIPT_PATH
import os

class Model:
    def __init__(self, source_path: str) -> None:
        self.root_path = osp.join(SCRIPT_PATH, osp.basename(source_path))
        os.makedirs(self.root_path, exist_ok = True)
        self.RAG_path = osp.join(self.root_path, 'rag.db') ## cuidado

    def create_prompt(self, data: Dict[str, Union[int, str]]) -> str:

        return
    def __call__(self, data: Dict[str, Union[int, str]]) -> str:
        prompt: str = self.create_prompt(data)
        return self.parsePrompt(prompt)

    def parsePrompt(self, prompt: str) -> str:
        pipeline = transformers.pipeline(
            "text-generation",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device="cuda",
        )
        out = pipeline(
            prompt,
            top_k = 50,
            top_p = 0.95,
            temperature = 0.7,
            num_return_sequences = 1,
        )

        return out[0]['generated_text']


