from embedding import CodeEmbedding
from RAG_handling.FAISS import FAISS
from typing import Dict, List
from torch import Tensor
import logging

class UpdateDatabaseRuntimeHandler:
    def __init__(self, project_path: str, dataset_path: str, meta_path: str, hidden_dim: int) -> None:
        self.faiss = FAISS(dataset_path, meta_path, hidden_dim)
        self.embedding = CodeEmbedding(project_path)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def on_written(self, filepath: str) -> None:
        try:
            hidden_dict: Dict[str, List[Tensor]] = self.embedding.on_written(filepath)
            self.faiss.on_written(hidden_dict)
        except Exception as e:
            self.logger.error(f"Error writing single file {filepath}: {e}")

    def whole_project(self, source_path: str) -> None:
        try:
            hidden_dict: Dict[str, List[Tensor]] = self.embedding.whole_project()
            self.faiss.whole_project(hidden_dict)
        except Exception as e:
            self.logger.error(f"Error writing whole project {source_path}: {e}")
