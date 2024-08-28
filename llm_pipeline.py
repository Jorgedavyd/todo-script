from embedding import CodeEmbedding
from collections.abc import Coroutine
from typing import Dict, List, Union
from collections import defaultdict
from numpy._typing import NDArray
from utils import SCRIPT_PATH, get_language
import os.path as osp
import transformers
import asyncio
import torch
import faiss
import os

class Model:
    def __init__(self, project_path: str, device: str, k: int) -> None:
        self.k = k
        self.root_path = osp.join(SCRIPT_PATH, osp.basename(project_path))
        os.makedirs(self.root_path, exist_ok = True)
        self.src = '/usr/bin/todo-script'
        self.dataset_path: str = osp.join(self.src, 'dataset', osp.basename(self.root_path), 'data.index')
        self.device = device
        self.index = faiss.read_index(self.dataset_path)
        self.embedding = CodeEmbedding(project_path)

    def retrieveCode(self, idx: List[int], metadata: Dict[str, List[int]]) -> str:
        path_list: Dict[str, List[int]] = defaultdict(list)
        allowedPattern: Dict[str, List[int]] = defaultdict(list)

        for key, value_list in metadata.items():
            for i, value in enumerate(value_list):
                if value in idx:
                    path_list[key].append(value)
                    allowedPattern[key].append(i)

        tasks: List[Coroutine] = [self.embedding.getASTfromFile(path, get_language(path)) for path in path_list]

        rag_context: str = asyncio.run(self.execute_ast(tasks, path_list, allowedPattern))

        return rag_context

    async def execute_ast(self, tasks: List[Coroutine], path_list: Dict[str, List[int]], allowedPattern: Dict[str, List[int]]) -> str:
        asts = await asyncio.gather(*tasks)

        self.embedding.readCode(asts, list(path_list.keys()))

        output_list: List[str] = [
            self.embedding.code[path][idx] for path in path_list
            for idx in allowedPattern[path]
        ]

        output: str = ''
        for value in output_list:
            output += value + '\n'*2

        return output

    def create_prompt(self, data: Dict[str, Union[int, str]], metadata: Dict[str, List[int]]) -> str:
        actual_instance: str = self.retrieveCode(data['line'], metadata)
        query_embedded: NDArray = self.embedding.embed(f"{actual_instance}{data['description']}").numpy()
        _, I = self.index.search(query_embedded, self.k)
        rag_context: str = self.retrieveCode(I, metadata)
        return f"{actual_instance}\n\n{rag_context} Question: {data['description']}"

    def __call__(self, data: Dict[str, Union[int, str]], metadata: Dict[str, List[int]]) -> str:
        prompt: str = self.create_prompt(data, metadata)
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


