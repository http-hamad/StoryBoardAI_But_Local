import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

import storyboardai_pb2, storyboardai_pb2_grpc

class StoryServiceServicer(storyboardai_pb2_grpc.StoryServiceServicer):
    def __init__(self):
        model_path = "../backend/models/text_model/txt_models/meta-llama/Llama-3.2-1B"
        tokenizer_path = "../backend/models/text_model/txt_tokenizers/meta-llama/Llama-3.2-1B"
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        if torch.backends.mps.is_available():
            self.model.to("mps")
        elif torch.cuda.is_available():
            self.model.to("cuda")
        else:
            self.model.to("cpu")
        self.generator = pipeline(
            "text-generation", model=self.model, tokenizer=self.tokenizer,
                        device_map="auto"
        )

    def GenerateStory(self, request, context):
        full_prompt = f"Theme: {request.theme}\nPrompt: {request.prompt}\nStory:"
        out = self.generator(
            full_prompt,
            do_sample=True, temperature=0.8,
            top_k=50, top_p=0.95,
            repetition_penalty=1.2,
            max_new_tokens=500
        )
        story = out[0]["generated_text"].replace(full_prompt, "").strip()
        return storyboardai_pb2.TextResponse(story=story)
