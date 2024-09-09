from dataclasses import dataclass
from typing import Dict, List, Tuple, Union
import os.path as osp
import json

from fileHandling import File
from RAG import RagDataset

@dataclass
class Task:
    description: str
    dueDate: str
    priority: str
    context: str

    def raw(self) -> Dict[str, str]:
        return {
            'description': self.description,
            'dueDate': self.dueDate,
            'priority': self.priority,
            'context': self.context,
        }

    def getQuery(self, dataset: RagDataset) -> str:
        rag_context: str = '\n'.join(dataset.getRAGcontext(self))
        return f"This is my codebase: {rag_context}\nThis is my current context: {self.context}\n Prompt: {self.description}"


@dataclass
class TaskDataset:
    src_path: str
    project_name: str

    def __post_init__(self) -> None:
        self.dataset_path: str = osp.join(self.src_path, self.project_name, 'taskDataset.json')

    def retrieveRaw(self) -> None:
        with open(self.dataset_path, 'r') as file:
            self.rawDataset = json.load(file)

    def __getitem__(self, filepath: str) -> Union[Tuple[int, List[Task]], None]:
        if not osp.exists(self.dataset_path):
            self.createDataset()

        self.retrieveRaw()

        for idx, (path, tasks) in enumerate(self.rawDataset.items()):
            if path == filepath:
                tasks: List[Task] = [Task(**rawData) for rawData in tasks]
                return idx, tasks
        return

    def createDataset(self) -> None:
        with open(self.dataset_path, 'x') as file:
            json.dump({}, file, indent = 4)

    def updateDataset(self, file: File, oldTasks: Union[List[Task], None], dataset_idx: int) -> None:
        newTasks: Union[List[Task], None] = file.tasks
        out: Union[Tuple[int, List[Task]], None] = self.__getitem__(file.path)

        if out is not None:
            dataset_idx, oldTasks = out

            if newTasks != oldTasks:
                if newTasks is None:
                    del self.rawDataset[dataset_idx]
                else:
                    self.rawDataset[dataset_idx] = file.raw()

        if newTasks is not None:
            self.rawDataset.append(file.raw())

        with open(self.dataset_path, 'w') as dataset:
            json.dump(self.rawDataset, dataset, indent = 4)
