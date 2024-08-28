import json

from numpy._typing import NDArray
import tree_sitter
from utils import get_filepaths, get_language, get_languages, get_parser, setup_parsers
from transformers import RobertaTokenizer, RobertaModel
from tree_sitter import Parser
from typing import Dict, List
from torch import Tensor
import aiofiles
import asyncio
import torch
import os
import os.path as osp

class CodeEmbedding:
    def __init__(self, project_path: str) -> None:
        self.code: List[str] = []
        self.project_path: str = project_path
        self.parser: Dict[str, Parser] = {language: get_parser(language, project_path) for language in get_languages(self.project_path)}
        self.src: str = '/usr/bin/todo-script'
        self.init_model()
        self.dataset_path: str = osp.join(self.src, 'dataset', osp.basename(self.project_path), 'data.index')
        self.meta_path: str = osp.join(self.src, 'dataset', osp.basename(self.project_path), 'metadata')
        os.makedirs(osp.dirname(self.meta_path), exist_ok = True)

    def init_model(self) -> None:
        self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = RobertaModel.from_pretrained("microsoft/codebert-base")

    def embed(self, code: str) -> Tensor:
        inputs = self.tokenizer(code, return_tensors='pt', padding=True, truncation=True)
        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state
            return embeddings.mean(dim=1)

    async def getASTfromFile(self, path: str, language: str):
        async with aiofiles.open(path, 'r') as file:
            code = await file.read()
        parser = self.parser.get(language)
        if parser is None:
            raise ValueError(f"No parser available for language: {language}")
        ast = parser.parse(bytes(code, 'utf-8'))
        return ast.root_node

    def preprocessAST(self, ast, filepath: str) -> List[str]:
        blocks: List[str] = []

        def traverse(node):
            if node.type in ['class_definition', 'function_definition']:
                blocks.append(node.text.decode('utf8'))
            elif node.type not in ['comment', 'string']:
                if not any(child.type in ['class_definition', 'function_definition'] for child in node.children):
                    blocks.append(node.text.decode('utf8'))

            for child in node.children:
                traverse(child)

        traverse(ast)


        return blocks

    def updateIdx(self, new_data: Dict[str, List[int]], filepath: str) -> None:

        with open(self.meta_path, 'r') as file:
            data = json.load(file)

        codeIdxs: List[int] = data[filepath]
        # pos: relative idx for blocks
        ## Contains a list of the indices referencing position in FAISS

        new_data: Dict[str, List[int]] = {

        }
        actual_values: List[int] = [*chain.from_iterable(data.values())]

        missing_values: List[int] = [
            num for num in range(1, max(actual_values))
            if num not in actual_values
        ]
        if len(
        for path, value_list in data.items():
            for j, relIdx in enumerate(value_list):
                for k, miss_value in enumerate(missing_values):
                    if relIdx < miss_value:
                        data[path][j] += k
                        break

        keep: List[NDArray] = [vec for i, vec in enumerate(
        data.update({filepath: []})

        with open(self.meta_path, 'w') as file:
            json.dump(data, file, indent = 4)

    def readCode(self, asts: List, filepath: str) -> None:
        for ast in asts:
            blocks: List[str] = self.preprocessAST(ast, filepath)
            self.code.extend(blocks)

    def on_written(self, filepath: str) -> List[Tensor]:
        ast = self.getASTfromFile(filepath, get_language(filepath))
        self.readCode([ast])
        return [self.embed(code) for code in self.code]

    async def run_full_project(self) -> None:
        setup_parsers(self.project_path)
        filepaths: List[str] = get_filepaths(self.project_path)
        asts: List = await asyncio.gather(*[self.getASTfromFile(filepath, get_language(filepath)) for filepath in filepaths])
        self.readCode(asts)

    def whole_project(self) -> List[Tensor]:
        asyncio.run(self.run_full_project())
        return [self.embed(code) for code in self.code]
