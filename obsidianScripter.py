import os.path as osp
import shutil
from typing import Dict, Union
from utils import SCRIPT_PATH
from ..model_pipeline import Model
import os

class Handler:
    def __init__(self, source_path: str) -> None:
        self.target_path = osp.join('~/OneDrive/Extracurricular/Ilustración/projects/', osp.basename(source_path))
        os.makedirs(self.target_path, exist_ok = True)
        self.main_path: str = osp.join(SCRIPT_PATH, 'templates/main.md')
        self.todo_path: str = osp.join(SCRIPT_PATH, 'templates/todo.md')
        self.model = Model(source_path)

    def createTODO(self) -> None:
        with open(self.todo_path, 'x') as file:
            pass

    def createMain(self) -> None:
        shutil.copy(self.main_path, self.target_path)

    def inference(self, data: Dict[str, Union[str, int]]) -> str:
        return self.model(data)

    def get_code_block(self, data: Dict[str, Union[int, str]]) -> str:

    def get_obsidian_task(self, data: Dict[str, Union[int, str]]) -> str:

    def next_TODO(self, data: Dict[str, Union[int, str]]) -> None:
        ## create parser for Tasks of obsidian
        obsidian_tasks: str = self.get_obsidian_task(data)
        code_block: str = self.get_code_block(data)
        ## Add the inference from pipeline
        llama_inference: str = self.inference(data)

        with open(osp.join(self.target_path, 'TODO.md'), 'a') as file, open(self.todo_path, 'r') as source:
            file.write('***\n')
            for line in source.readlines():
                if line:=line.strip():
                    if '{{LINE_PLACEHOLDER}}' in line:
                        line = line.replace('{{LINE_PLACEHOLDER}}', f'{data["line"]}')
                    elif '{{TASK_PLACEHOLDER}}' in line:
                        line = obsidian_tasks
                    elif '{{CODE_BLOCK_PLACEHOLDER}}' in line:
                        line = code_block
                    elif '{{LLAMA_SOLUTION_PLACEHOLDER}}' in line:
                        line = llama_inference

                    file.write(line + '\n')

