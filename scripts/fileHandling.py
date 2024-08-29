from dataclasses import dataclass
from typing import List, Dict

from taskHandling import TaskDataset, Task
from codeHandling import Code
from utils import get_language

@dataclass
class File:
    path: str
    src_path: str
    project_name: str

    def __post_init__(self) -> None:
        self.getOldTasks()
        self.getCode()
        self.getTasks()
        self.taskDataset = TaskDataset(self.src_path)
        self.updateDatasets()

    def getOldTasks(self) -> None:
        self.oldTasks: List[Task] = self.taskDataset[self.path]

    def getCode(self) -> None:
        self.code: Code = Code(self.path, get_language(self.path), self.project_name)

    def getTasks(self) -> None:
        self.tasks: List[Task] = self.code.getTasks()

    def raw(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            self.path: [task.raw() for task in self.tasks]
        }

    def updateDatasets(self) -> None:
        self.taskDataset.updateDataset(self)

