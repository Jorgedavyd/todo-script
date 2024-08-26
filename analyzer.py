from collections.abc import Coroutine
from typing import Dict, List, Union
from datetime import datetime
import os.path as osp
import aiofiles
import asyncio
import json
import os
import re
from utils import SCRIPT_PATH

VALID_PRIORITY = ['low', 'mid', 'high']

class Analyzer:
    def __init__(self, source_path: str) -> None:
        self.src = source_path
        self.db_path: str = osp.join(SCRIPT_PATH, osp.basename(source_path), 'metadata.json')
        self.def_lines: List[int] = []
        self.load_existing_data()

    def load_existing_data(self) -> None:
        try:
            with open(self.db_path, 'r') as file:
                data = json.load(file)
                self.def_lines = [entry['line'] for entry in data]
        except FileNotFoundError:
            with open(self.db_path, 'w') as file:
                json.dump([], file)
        except json.JSONDecodeError:
            with open(self.db_path, 'w') as file:
                json.dump([], file)

    def parse_line(self, line: str, idx: int) -> Dict[str, Union[str, int]]:
        pattern = r"TODO\s+(\d{2}\d{2}\d{2})\s+([A-Z])\s+(.*)"
        match = re.match(pattern, line)

        if match:
            date_str = match.group(1)
            priority = match.group(2).lower()
            description = match.group(3)

            if priority not in VALID_PRIORITY:
                raise ValueError(f'Invalid priority: {priority}, expected: {VALID_PRIORITY}')

            date_format = datetime.strptime(date_str, "%d%m%y").date()

            return {
                "line": idx,
                "date": date_format.isoformat(),
                "priority": priority,
                "description": description
            }
        else:
            raise ValueError('Not valid input query, TODO pattern doesn\'t match the expected one: TODO <date:%d%m%y> <priority> <description>')

    def new(self, line: str, idx: int) -> None:
        db_format: Dict[str, Union[str, int]] = self.parse_line(line, idx)
        with open(self.db_path, 'r') as file:
            data = json.load(file)

        data.append(db_format)
        with open(self.db_path, 'w') as file:
            json.dump(data, file, indent=4)

    def look_for_change(self, line: str, idx: int) -> None:
        db_format: Dict[str, Union[str, int]] = self.parse_line(line, idx)
        with open(self.db_path, 'r') as file:
            data = json.load(file)

        for entry in data:
            if entry['line'] == idx:
                if entry != db_format:
                    entry.update(db_format)
                    with open(self.db_path, 'w') as file:
                        json.dump(data, file, indent=4)
                break

    async def single_file(self, path: str) -> None:
        async with aiofiles.open(path, 'r') as file:
            lines = await file.readlines()
            for idx, line in enumerate(lines):
                if 'TODO' in line:
                    if idx not in self.def_lines:
                        self.new(line, idx)
                    else:
                        self.look_for_change(line, idx)

    def get_file_tasks(self) -> List[Coroutine]:
        filepaths: List[str] = self.get_filepaths()
        return [self.single_file(path) for path in filepaths]

    def get_filepaths(self) -> List[str]:
        filepaths = []
        for dirpath, _, filenames in os.walk(self.src):
            for filename in filenames:
                filepaths.append(osp.join(dirpath, filename))
        return filepaths

    async def main(self) -> None:
        await asyncio.gather(*self.get_file_tasks())

    def __call__(self) -> None:
        asyncio.run(self.main())

