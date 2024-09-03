from RAG import RagDataset
from fileHandling import File
import os.path as osp

from obsidianHandler import Obsidian
from scripts.observer import ProjectObserver

def main(filepath: str) -> None:

    source_path: str = '/usr/bin/todo-script/' #script location
    k: int = 5 #The amount of relevant indexes for RAG.
    vault_path: str = '~/OneDrive/Extracurricular/Ilustracion/projects/' #The path to your project vault.
    device: str = 'cpu' #The device in which the model will be running.


    project_name: str = osp.basename(filepath)
    mainFile: File = File(filepath, source_path, project_name)
    ragDataset: RagDataset = RagDataset(source_path, project_name, k)
    obsidian: Obsidian = Obsidian(vault_path, source_path, ragDataset, project_name, device)

    ragDataset.updateDataset(mainFile)
    obsidian(mainFile)

if __name__ == '__main__':
    project_path: str = '~/projects/' # The root directory of all projects (code)
    observer = ProjectObserver(project_path)
    observer(main)




