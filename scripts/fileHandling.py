from dataclasses import dataclass
from typing import List, Dict, Tuple, Union
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
        self.taskDataset: TaskDataset = TaskDataset(self.src_path, self.project_name)
        self.updateDatasets()

    def getOldTasks(self) -> None:
        out:Union[Tuple[int, List[Task]], None]  = self.taskDataset[self.path]
        if out is not None:
            self.idx, self.oldTasks = out

    def getCode(self) -> None:
        self.code: Code = Code(self.path, get_language(self.path), self.project_name)

    def getTasks(self) -> None:
        self.tasks: Union[List[Task], None] = self.code.getTasks(self.oldTasks)

    def raw(self) -> Union[Dict[str, List[Dict[str, str]]], None]:
        if self.tasks is not None:
            return {
                self.path: [task.raw() for task in self.tasks]
            }
        return

    def updateDatasets(self) -> None:
        if getattr(self, 'oldTasks') is not None:
            self.taskDataset.updateDataset(self, self.oldTasks, self.idx)

