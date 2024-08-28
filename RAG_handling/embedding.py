from utils import get_filepaths, get_language, get_languages, get_parser, setup_parsers
from transformers import RobertaTokenizer, RobertaModel
from tree_sitter import Parser
from typing import Dict, List
from torch import Tensor
import os.path as osp
import aiofiles
import asyncio
import torch
import os

class CodeEmbedding:
    def __init__(self, project_path: str) -> None:
        self.code: Dict[str, List[str]] = {}
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

    def preprocessAST(self, ast) -> List[str]:
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

    def readCode(self, asts: List, filepaths: List[str]) -> None:
        for ast, filepath in zip(asts, filepaths):
            blocks: List[str] = self.preprocessAST(ast)
            self.code[filepath] = blocks

    def on_written(self, filepath: str) -> Dict[str, List[Tensor]]:
        ast = self.getASTfromFile(filepath, get_language(filepath))
        self.readCode([ast], [filepath])
        return {
            filepath: [self.embed(code) for code in self.code[filepath]]
            for filepath in [filepath]
        }

    async def run_full_project(self, filepaths: List[str]) -> None:
        setup_parsers(self.project_path)
        asts: List = await asyncio.gather(*[self.getASTfromFile(filepath, get_language(filepath)) for filepath in filepaths])
        self.readCode(asts, filepaths)

    def whole_project(self) -> Dict[str, List[Tensor]]:
        filepaths: List[str] = get_filepaths(self.project_path)
        asyncio.run(self.run_full_project(filepaths))
        return {
            filepath: [self.embed(code) for code in self.code[filepath]]
            for filepath in filepaths
        }
