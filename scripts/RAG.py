from collections import defaultdict
from dataclasses import dataclass
from numpy.typing import NDArray
from typing import Coroutine, List, Dict
import os.path as osp
import numpy as np
from torch import Tensor
import asyncio
import faiss
import json

from taskHandling import Task
from utils import get_language
from codeHandling import Code
from embedding import Embedding
from fileHandling import File

@dataclass
class RagDataset:
    source_path: str
    project_name: str
    k: int

    def __post_init__(self) -> None:
        self.dataset_path: str = osp.join(self.source_path, self.project_name, 'ragDataset.index')
        self.embedding: Embedding = Embedding()
        self.metapath: str = osp.join(self.source_path, self.project_name, 'metadata.json')

    def loadFaiss(self) -> None:
        self.index = faiss.read_index(self.dataset_path)
        self.n_vectors = self.index.ntotal
        self.d = self.index.d


    def loadMetadata(self) -> None:
        with open(self.metapath, 'r') as file:
            self.metadata = json.load(file)

    def getDataset(self) -> NDArray:
        vectors: NDArray = np.zeros((self.n_vectors, self.d), dtype = np.float32)
        self.index.reconstruct_n(0, self.n_vectors, vectors)
        return vectors

    def updateRawDataset(self, rawDataset: NDArray, relativeInd: List[int], hiddenFeatures: List[Tensor]) -> NDArray:
        new_vectors: List[NDArray] = [
            vector for idx, vector in enumerate(rawDataset)
            if idx not in relativeInd
        ].extend(
            [
                e.numpy() for e in hiddenFeatures
            ]
        )
        new_vector: NDArray = np.stack(new_vectors, axis = 0)
        return new_vector

    def updateMetadata(self, filepath: str, len_feature: int) -> None:
        oldIdx: List[int] = self.metadata[filepath]
        maxId:int = sum(map(lambda x: len(x), self.metadata.values()))
        self.metadata.update({
            filepath: [maxId + idx for idx in range(len_feature)]
        })
        for path, value_list in self.metadata.items():
            for j, relIdx in enumerate(value_list):
                for k, (down, up) in enumerate(zip(oldIdx[:-1], oldIdx[1:])):
                    if down < relIdx < up:
                        self.metadata[path][j] -= k + 1
                        break
        with open(self.metapath, 'w') as file:
            json.dump(self.metadata, file, indent = 4)

    def updateDataset(self, file: File) -> None:
        hiddenFeatures: List[Tensor] = self.embedding(file.code)
        relativeInd: List[int] = self.metadata[file.path]
        rawDataset: NDArray = self.getDataset()
        newDataset: NDArray = self.updateRawDataset(rawDataset, relativeInd, hiddenFeatures)
        newIndex = faiss.IndexFlatL2(newDataset)
        faiss.write_index(newIndex, self.dataset_path)
        self.updateMetadata(file.path, len(hiddenFeatures))

    def addFilepath(self, hiddenFeatures: List[Tensor], filepath: str) -> None:
        rawDataset: NDArray = self.getDataset()
        add_vector = np.stack([e.numpy() for e in hiddenFeatures], axis = 0)
        new_dataset: NDArray = np.concatenate((rawDataset, add_vector), axis = 0)
        maxId:int = sum(map(lambda x: len(x), self.metadata.values()))
        self.metadata.update({
            filepath: [maxId + idx for idx in range(len(hiddenFeatures))]
        })
        new_index = faiss.IndexFlatL2(new_dataset)
        faiss.write_index(new_index, self.dataset_path)

    def getRAGcontext(self, task: Task) -> List[str]:
        query_embedded: NDArray = self.embedding(f"{task.context}{task.description}").numpy()
        _, I = self.index.search(query_embedded, self.k)
        return self.retrieveCode(I)

    def retrieveCode(self, idx: List[int]) -> List[str]:
        path_list: Dict[str, List[int]] = defaultdict(list)
        allowedPattern: Dict[str, List[int]] = defaultdict(list)

        for key, value_list in self.metadata.items():
            for i, value in enumerate(value_list):
                if value in idx:
                    path_list[key].append(value)
                    allowedPattern[key].append(i)

        codeList: List[Code] = [Code(path, get_language(path), self.project_name) for path in path_list]

        tasks: List[Coroutine] = [codeInst.renderFile() for codeInst in codeList]

        return asyncio.run(self.execute_ast(tasks, path_list, allowedPattern))

    async def execute_ast(self, tasks: List[Coroutine], path_list: Dict[str, List[int]], allowedPattern: Dict[str, List[int]]) -> List[str]:
        codes = await asyncio.gather(*tasks)
        return [
            codes[idx] for path in path_list for idx in allowedPattern[path]
        ]
