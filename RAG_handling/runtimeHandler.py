from RAG_handling.FAISS import FAISS_handler
from typing import Any, Dict, List, Union
from collections.abc import Coroutine
from utils import get_filepaths
import os.path as osp
import asyncio
import os

class DatasetHandler(FAISS_handler):
    def __init__(self, project_path: str) -> None:
        super().__init__(project_path)
        self.src: str = '/usr/bin/todo-script/'
        os.makedirs(osp.join(self.src, 'dataset'), exist_ok = True)

    async def singleDB(self, filepath: str) -> None:
        if path:=self.findFileDataset(filepath):
            await self.updateDB(path)
        else:
            await self.addDB(path)

    def findFileDataset(self, filepath: str, data: Dict[str, Union[str, int]]) -> :

    def findDatabase(self) -> Any:
        database_path: str = osp.join(self.src, 'dataset', osp.basename(self.project_path) + '.index')
        if osp.exists(database_path):
            return database_path
        else:
            return False

    def single_file(self, filepath: str) -> None:
        asyncio.run(self.singleDB(filepath))

    def on_written(self, data: Dict[str, Union[str, int]]) -> None:
        filepath: str = data["path"] # return the value for the written file
        self.single_file(filepath) # updates or creates FAISS dataset

    async def whole_project(self, source_path: str) -> None:
        filepaths: List[str] = get_filepaths(source_path)
        tasks: List[Coroutine] = [self.singleDB(filepath) for filepath in filepaths]
        await asyncio.gather(*tasks)

