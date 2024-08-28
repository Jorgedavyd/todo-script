from numpy._typing import NDArray
from utils import get_filepaths
from torch import Tensor
from typing import Dict, List
import os.path as osp
import numpy as np
import faiss
import json

class FAISS:
    def __init__(self, dataset_path: str, meta_path: str, hidden_dim: int) -> None:
        self.dataset_path: str = dataset_path
        self.meta_path: str = meta_path
        with open(meta_path, 'r') as file:
            self.metadata = json.load(file)
        self.setIndex(hidden_dim)
        self.n_vectors = self.index.ntotal
        self.d = self.index.d

    def setIndex(self, hidden_dim: int):
        if osp.exists(self.dataset_path):
            self.index = faiss.read_index(self.dataset_path)
        else:
            self.index = faiss.IndexFlatL2(hidden_dim)

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

        with open(self.meta_path, 'w') as file:
            json.dump(self.metadata, file, indent = 4)

    def updateFilepath(self, hiddenFeatures: List[Tensor], filepath: str) -> None:
        relativeInd: List[int] = self.metadata[filepath]
        vectors: NDArray = np.zeros((self.n_vectors, self.d), dtype = np.float32)
        self.index.reconstruct_n(0, self.n_vectors, vectors)
        new_vectors: List[NDArray] = [
            vector for idx, vector in enumerate(vectors)
                if idx not in relativeInd].extend(
                e.numpy() for e in hiddenFeatures)
        new_vector: NDArray = np.stack(new_vectors, axis = 0)
        new_index = faiss.IndexFlatL2(new_vector)
        faiss.write_index(new_index, self.dataset_path)
        self.updateMetadata(filepath, len(hiddenFeatures))

    def createFilepath(self, hiddenFeatures: List[Tensor], filepath: str) -> None:
        vectors: NDArray = np.zeros((self.n_vectors, self.d), dtype = np.float32)
        self.index.reconstruct_n(0, self.n_vectors, vectors)
        add_vector = np.stack([e.numpy() for e in hiddenFeatures], axis = 0)
        new_dataset: NDArray = np.concatenate((vectors, add_vector), axis = 0)
        maxId:int = sum(map(lambda x: len(x), self.metadata.values()))
        self.metadata.update({
            filepath: [maxId + idx for idx in range(len(hiddenFeatures))]
        })
        new_index = faiss.IndexFlatL2(new_dataset)
        faiss.write_index(new_index, self.dataset_path)

    def on_written(self, hiddenDict: Dict[str, List[Tensor]]) -> None:
        hiddenFeatures: List[Tensor] = list(hiddenDict.values())
        filepath: str = list(hiddenDict.keys())[0]
        if self.metadata.get(filepath) is not None:
            self.updateFilepath(hiddenFeatures, filepath)
        else:
            self.createFilepath(hiddenFeatures, filepath)

    def whole_project(self, hiddenDict: Dict[str, List[Tensor]]) -> None:
        for filepath, hiddenFeature in hiddenDict.items():
            if self.metadata.get(filepath) is not None:
                self.updateFilepath(hiddenFeature, filepath)
            else:
                self.createFilepath(hiddenFeature, filepath)

