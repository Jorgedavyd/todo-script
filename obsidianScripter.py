import os.path as osp
import shutil
from typing import Dict, List, Union
from utils import SCRIPT_PATH
from llm_pipeline import Model
import os

DUE_DATE_ICON =

PRIORITY_ICONS = {
    'low': ,
    'mid': ,
    'high':
}

VALID_DEVICES = ['cpu', 'cuda']

class Handler:
    def __init__(self, source_path: str, obsidian_vault_project_path: str, device: str) -> None:
        assert (device in VALID_DEVICES), "Not valid device"
        self.project_name: str = osp.basename(source_path)
        self.target_path = osp.join(obsidian_vault_project_path, self.project_name)
        os.makedirs(self.target_path, exist_ok = True)
        self.main_path: str = osp.join(SCRIPT_PATH, 'templates/main.md')
        self.todo_path: str = osp.join(SCRIPT_PATH, 'templates/TODO.md')
        self.model = Model(source_path, device)

    def createTODO(self) -> None:
        with open(self.todo_path, 'x') as file:
            pass

    def createMain(self) -> None:
        shutil.copy(self.main_path, self.target_path)
        new_file: List[str] = []
        with open(self.main_path, 'r') as file:
            for line in file.readlines():
                if '{{PROJECT_PLACEHOLDER}}' in line:
                    line.replace('{{PROJECT_PLACEHOLDER}}', self.project_name)
                new_file.append(line)
        with open(self.target_path, 'w') as file:
            file.write('\n'.join(new_file))

    def inference(self, data: Dict[str, Union[str, int]]) -> str:
        return self.model(data)

    def get_code_block(self, data: Dict[str, Union[int, str]]) -> str:
        idx: int = data['line']
        path: str = data['path']
        language: str = data['language']
        with open(path, 'w') as file:
            lines = file.readlines()
            return f'```{language}\n' + '\n'.join(lines[idx-7:idx+7]) + '\n```'

    def get_obsidian_task(self, data: Dict[str, Union[int, str]]) -> str:
        desc: str = data['description']
        due_date: str = data['date']
        priority: str = PRIORITY_ICONS[data['priority']]
        return f'- [ ] {desc} {DUE_DATE_ICON}{due_date}{priority}'

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
