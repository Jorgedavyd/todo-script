import json
import faiss
from typing import Any, List
from RAG_handling.embedding import CodeEmbedding
import os
import os.path as osp
from torch import Tensor
import numpy as np

class Dataset:
    def __init__(self, dataset_path: str, meta_path: str) -> None:
        self.dataset_path = dataset_path
        with open(meta_path, 'r') as file:
            self.metadata = json.load(file)
    def setIndex(self, hidden_dim: int):
        if osp.exists(self.dataset_path):
            self.index = faiss.read_index(self.dataset_path)
        else:
            self.index = faiss.IndexFlatL2(hidden_dim)
    def addVector(self,
class FAISS_handler(CodeEmbedding):
    def __init__(self, project_path: str) -> None:
        super().__init__(project_path)

    async def handleFile(self, filepath: str) -> None:
        if self.findDatabase():
            if path:=self.findFileDataset(filepath):
                await self.update(path)
            else:
                await self.add(path)
        else:
            self.create()

    def findFileDataset(self, filepath: str) -> Any:
        ## index into the FAISS dataset

    def findDatabase(self) -> Any:
        return self.dataset_path if osp.exists(self.dataset_path) else False

    async def add(self, filepath: str) -> None:

    async def update(self, filepath: str) -> None:

    def create(self) -> None:
        embedded_codebase: List[Tensor] = self.whole_project()
        embedding = np.array([e.numpy() for e in embedded_codebase])
        index = faiss.IndexFlatL2(embedding.shape[1])
        index.add(embedding)

