from definitions import DUE_DATE_ICON, PRIORITY_ICONS, VALID_DEVICES
from scripts.RAG import RagDataset
from scripts.utils import get_comment
from taskHandling import Task, TaskDataset, taskParser
from typing import Callable, List, Union
from dataclasses import dataclass
from fileHandling import File
import os.path as osp
from llm import Model
import shutil
import re

@dataclass
class Obsidian:
    vault_path: str
    source_path: str
    ragDataset: RagDataset
    project_name: str
    device: str

    def __post_init__(self) -> None:
        assert (self.device in VALID_DEVICES), f"Not a valid device: {VALID_DEVICES}"
        self.project_name: str = osp.basename(self.vault_path)
        self.getTemplatePath: Callable[[str], str] = lambda x: osp.join(self.source_path, 'templates', x)
        self.getTargetPath: Callable[[str], str] = lambda x: osp.join(self.vault_path, self.project_name, x)
        self.model: Model = Model(self.device)
        self.taskDataset: TaskDataset = TaskDataset(self.source_path, self.project_name)

    def createMain(self) -> None:
        mainPath: str = self.getTemplatePath('main.md')
        targetPath: str = self.getTargetPath('main.md')
        shutil.copy(mainPath, targetPath)

        with open(mainPath, 'r') as file:
            new_file = '\n'.join(file.readlines()).replace('{{PROJECT_PLACEHOLDER}}', self.project_name)

        with open(targetPath, 'w') as file:
            file.write(new_file)

    def deleteTasks(self, oldTasks: Union[List[Task], None]) -> None:
        if oldTasks is not None:
            for task in oldTasks:
                self.deleteTask(task)

    def deleteTask(self, task: Task) -> None:
        ind_1: str = task.context
        ind_2: str = task.dueDate
        ind_3: str = task.priority

        targetPath: str = self.getTargetPath('todo.md')

        with open(targetPath, 'r') as file:
            lines = file.readlines()
            blocks: List[str] = '\n'.join(lines).split('***')
            new_file: List[str] = [block for block in blocks
                if ind_1 not in block and \
                ind_2 not in block and \
                ind_3 not in block\
            ]

        with open(targetPath, 'w') as file:
            file.write('***'.join(new_file))

    def createObsidianTask(self, task: Task) -> str:
        priority: str = PRIORITY_ICONS[task.priority]
        return f'- [ ] {task.description} {DUE_DATE_ICON}{task.dueDate}{priority}'

    def decodeBlock(self, block: str) -> str:
        new_match = re.search(r"path: (.*)", block)
        filepath: str = new_match.group(1)
        return filepath

    def taskDone(self, block: str, language: str, task: Task) -> None:
        filepath = self.decodeBlock(block)
        new_file: List[str] = []
        with open(filepath, 'r') as file:
            for line in file.readlines():
                if 'TODO' in line and \
                    task.context in line and \
                    task.priority in line and \
                    task.dueDate in line:
                    new_file.append(line.split(get_comment(language))[0])
                else:
                    new_file.append(line)

        with open(filepath, 'w') as file:
            file.writelines(new_file)

    def writeTask(self, task: Task, filepath: str) -> None:
        templatePath: str = self.getTemplatePath('todo.md')
        targetPath: str = self.getTargetPath('todo.md')

        obsidianTask: str = self.createObsidianTask(task)
        code_block: str = task.context

        llama_inference: str = self.model(task.getQuery(self.ragDataset))

        with open(targetPath, 'a') as file, open(templatePath, 'r') as source:
            block = '\n'.join(source.readlines())
            block.replace('{{TASK_PLACEHOLDER}}', obsidianTask)\
                    .replace('{{PATH_PLACEHOLDER}}', filepath) \
                    .replace('{{CODE_BLOCK_PLACEHOLDER}}', code_block) \
                    .replace('{{LLAMA_SOLUTION_PLACEHOLDER}}', llama_inference)
            file.write(block)

    def writeTasks(self, tasks: Union[List[Task], None], filepath: str) -> None:
        if tasks is not None:
            for task in tasks:
                self.writeTask(task, filepath)

    def handleDoneTasks(self, todoPath: str, language: str) -> Union[List[Task], None]:
        tasks: List[Task] = []
        file_input: List[str] = []

        with open(todoPath, 'r') as file:
            iterable: List[str] = '\n'.join(file.readlines()).split('***')
            if iterable is not None:
                if len(iterable) > 0:
                    for obsidian_block in iterable:
                        if '- [X]' not in obsidian_block:
                            file_input.append(obsidian_block)
                        else:
                            task: Task = taskParser(obsidian_block)
                            tasks.append(task)
                            self.taskDone(obsidian_block, language, task)

        if len(tasks) > 0:
            with open(todoPath, 'w') as file:
                file.write('***'.join(file_input))
            return tasks


    def __call__(self, file: File) -> None:
        todoPath: str = self.getTemplatePath('todo.md')
        if osp.exists(todoPath):
            doneTasks: Union[List[Task], None] = self.handleDoneTasks(todoPath, file.code.language)
        else:
            self.createTaskTemplate()
            doneTasks = None

        oldTasks: Union[List[Task], None] = file.oldTasks
        newTasks: Union[List[Task], None] = file.tasks

        if oldTasks == newTasks:
            return
        else:
            if doneTasks is not None:
                if oldTasks is not None:
                    oldTasks = list(set(oldTasks) - set(doneTasks))

                if newTasks is not None:
                    newTasks = list(set(newTasks) - set(doneTasks))

            self.deleteTasks(oldTasks)
            self.writeTasks(newTasks, file.path)

    def createTaskTemplate(self) -> None:
        taskPath: str = self.getTargetPath('todo.md')
        with open(taskPath, 'x') as file:
            file.write('This file is used to store all tasks, you\'ll be able to access each of them specifically through main.md')
