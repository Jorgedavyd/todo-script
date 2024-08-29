import transformers
import torch

class Model:
    def __init__(self, device: str) -> None:
        self.device = device

    def __call__(self, prompt: str) -> str:
        return self.parsePrompt(prompt)

    def parsePrompt(self, prompt: str) -> str:
        pipeline = transformers.pipeline(
            "text-generation",
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device=self.device,
        )
        out = pipeline(
            prompt,
            top_k = 50,
            top_p = 0.95,
            temperature = 0.7,
            num_return_sequences = 1,
        )

        return out[0]['generated_text']


