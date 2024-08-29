from RAG import RagDataset
from fileHandling import File
import os.path as osp

from obsidianHandler import Obsidian
from scripts.observer import ProjectObserver

def main(filepath: str) -> None:

    source_path: str = '/usr/bin/todo-script/' #script location
    k: int = 5 #The amount of relevant indexes for RAG.
    vault_path: str = '~/OneDrive/Extracurricular/Ilustracion/projects/' #The path to your project vault.
    device: str = 'cuda' #The device in which the model will be running.
    project_path: str = '~/projects/' # The root directory of all projects (code)

    project_name: str = osp.basename(project_path)
    mainFile: File = File(filepath, source_path)
    ragDataset: RagDataset = RagDataset(source_path, project_name, k)
    obsidian: Obsidian = Obsidian(vault_path, source_path, device)
    ragDataset.updateDataset(mainFile)
    obsidian(mainFile)

if __name__ == '__main__':
    observer = ProjectObserver('~/projects')
    observer(main)




