from dataclasses import dataclass
from typing import Dict, List
import os.path as osp
import json

from fileHandling import File
from codeHandling import Code
from RAG import RagDataset

@dataclass
class Task:
    line: int
    description: str
    dueDate: str
    priority: str
    context: Code
    ragIdx: List[int] ## Index array for every indexing into FAISS

    def raw(self) -> Dict[str, List[int] | str | int]:
        return {
            'line': self.line,
            'description': self.description,
            'dueDate': self.dueDate,
            'priority': self.priority,
            'context': self.context.getNL(),
        }

    def getQuery(self, dataset: RagDataset) -> str:
        rag_context: str = self.getFromFAISS(dataset)
        return f"This is my codebase: {rag_context}\nThis is my current context: {self.context}\n Prompt: {self.description}"

    def getFromFAISS(self, dataset: RagDataset) -> str:

        return code.raw()


@dataclass
class TaskDataset:
    src_path: str
    project_path: str

    def __post_init__(self) -> None:
        self.dataset_path: str = osp.join(self.src_path, osp.basename(self.project_path), 'taskDataset.json')

    def retrieveRaw(self) -> None:
        with open(self.dataset_path, 'r') as file:
            self.rawDataset = json.load(file)

    def __getitem__(self, filepath: str) -> List[Task]:
        if osp.exists(self.dataset_path):
            self.retrieveRaw()
        else:
            self.createDataset()
            self.retrieveRaw()

        fileDataset: List[Dict[str, List[int] | str | int]] = self.rawDataset[filepath]
        tasks: List[Task] = [Task(**rawData) for rawData in fileDataset]
        return tasks

    def createDataset(self) -> None:
        with open(self.dataset_path, 'x') as file:
            json.dump({}, file, indent = 4)

    def updateDataset(self, file: File) -> None:
        updatedDataset: Dict[str, List[Dict[str, str]]] = self.rawDataset.update(
            file.raw()
        )

        with open(self.dataset_path, 'w') as dataset:
            json.dump(updatedDataset, dataset, indent = 4)

