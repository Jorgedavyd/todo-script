from typing import List
from transformers import RobertaTokenizer, RobertaModel
from torch import Tensor
import torch

class Embedding:
    def __init__(self) -> None:
        self.init_model()

    def init_model(self) -> None:
        self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.model = RobertaModel.from_pretrained("microsoft/codebert-base")

    def __call__(self, x: str | List[str]) -> Tensor | List[Tensor]:
        if isinstance(x, str):
            inputs = self.tokenizer(x, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                embeddings = self.model(**inputs).last_hidden_state
                return embeddings.mean(dim=1)
        elif isinstance(x, list):
            return [self.__call__(i) for i in x]
