from definitions import DUE_DATE_ICON, PRIORITY_ICONS, VALID_DEVICES
from taskHandling import Task, TaskDataset
from typing import Callable, List, Tuple
from dataclasses import dataclass
from fileHandling import File
import os.path as osp
from llm import Model
import shutil

@dataclass
class Obsidian:
    vault_path: str
    source_path: str
    device: str
    def __post_init__(self) -> None:
        assert (self.device in VALID_DEVICES), f"Not a valid device: {VALID_DEVICES}"
        self.project_name: str = osp.basename(self.vault_path)
        self.getTemplatePath: Callable[[str], str] = lambda x: osp.join(self.source_path, 'templates', x)
        self.getTargetPath: Callable[[str], str] = lambda x: osp.join(self.vault_path, self.project_name, x)
        self.model: Model = Model(self.device)
        self.taskDataset: TaskDataset = TaskDataset(self.source_path)

    def createMain(self) -> None:
        mainPath: str = self.getTemplatePath('main.md')
        targetPath: str = self.getTargetPath('main.md')
        shutil.copy(mainPath, targetPath)

        new_file: List[str] = []
        with open(mainPath, 'r') as file:
            for line in file.readlines():
                if '{{PROJECT_PLACEHOLDER}}' in line:
                    line.replace('{{PROJECT_PLACEHOLDER}}', self.project_name)
                new_file.append(line)

        with open(targetPath, 'w') as file:
            file.write('\n'.join(new_file))

    def deleteTasks(self, file: File) -> None:
        for task in file.tasks:
            self.writeTask(task)

    def deleteTask(self, task: Task) -> None:
        ind: str = task.context
        targetPath: str = self.getTargetPath('todo.md')

        with open(targetPath, 'r') as file:
            lines = file.readlines()
            blocks: List[str] = '\n'.join(lines).split('***')
            new_file: List[str] = [block for block in blocks if ind not in block]

        with open(targetPath, 'w') as file:
            file.write('***'.join(new_file))

    def createObsidianTask(self, task: Task) -> str:
        priority: str = PRIORITY_ICONS[task.priority]
        return f'- [ ] {task.description} {DUE_DATE_ICON}{task.dueDate}{priority}'

    def decodeBlock(self, block: str) -> Tuple[int, str]:
        for block_line in block.split('\n'):
            if 'path:' in block_line:
                filepath = block_line.split(':')[-1]
            if '- [ ]' in block_line:
                break

        with open(filepath, 'r') as file:
            for idx, line in enumerate(file.readlines()):
                if line == block_line:
                    line_idx = idx

        return line_idx, filepath

    def taskDone(self, block: str) -> None:
        line, filepath = self.decodeBlock(block)

        with open(filepath, 'r') as file:
            lines = file.readlines()

        del lines[line]

        with open(filepath, 'w') as file:
            file.writelines(lines)

    def writeTask(self, task: Task) -> None:
        templatePath: str = self.getTemplatePath('todo.md')
        targetPath: str = self.getTargetPath('todo.md')

        obsidianTask: str = self.createObsidianTask(task)
        code_block: str = task.context
        llama_inference: str = self.model(task.getQuery())

        with open(targetPath, 'a') as file, open(templatePath, 'r') as source:
            file.write('***\n')
            for line in source.readlines():
                if line:=line.strip():
                    if '{{LINE_PLACEHOLDER}}' in line:
                        line = line.replace('{{LINE_PLACEHOLDER}}', f'{task.line}')
                    elif '{{TASK_PLACEHOLDER}}' in line:
                        line = obsidianTask
                    elif '{{CODE_BLOCK_PLACEHOLDER}}' in line:
                        line = code_block
                    elif '{{LLAMA_SOLUTION_PLACEHOLDER}}' in line:
                        line = llama_inference

                    file.write(line + '\n')

    def writeTasks(self, file: File) -> None:
        for task in file.tasks:
            self.writeTask(task)

    def __call__(self, file: File) -> None:
        self.writeTasks(file)
        self.deleteTasks(file)

    def createTaskTemplate(self) -> None:
        taskPath: str = self.getTargetPath('todo.md')
        with open(taskPath, 'x') as file:
            file.write('This file is used to store all tasks, you\'ll be able to access each of them specifically through main.md')
