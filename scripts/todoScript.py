from RAG import RagDataset
from fileHandling import File
import os.path as osp
from typing import Tuple
from obsidianHandler import Obsidian
from scripts.observer import ProjectObserver

def separe_in_heads(filepath: str, project_path: str) -> str:
    values: Tuple[str, str] = osp.split(filepath)
    if values[0] == project_path:
        return values[-1]
    return separe_in_heads(values[0], project_path)

def main(filepath: str, project_path: str) -> None:

    source_path: str = '/usr/bin/todo-script/' #script location
    k: int = 5 #The amount of relevant indexes for RAG.
    vault_path: str = '~/OneDrive/Extracurricular/Ilustracion/projects/' #The path to your project vault.
    device: str = 'cuda' #The device in which the model will be running.

    project_name: str = separe_in_heads(filepath, project_path)
    mainFile: File = File(filepath, source_path, project_name)
    ragDataset: RagDataset = RagDataset(source_path, project_name, k)
    obsidian: Obsidian = Obsidian(vault_path, source_path, ragDataset, project_name, device)

    ragDataset.updateDataset(mainFile)
    obsidian(mainFile)

if __name__ == '__main__':
    project_path: str = '~/projects/' # The root directory of all projects (code)
    observer = ProjectObserver(project_path)
    observer(lambda filepath: main(filepath, project_path))




