import io
import torch
from diffusers import AmusedPipeline

import storyboardai_pb2, storyboardai_pb2_grpc

class ImageServiceServicer(storyboardai_pb2_grpc.ImageServiceServicer):
    def __init__(self):
        self.pipe = AmusedPipeline.from_pretrained(
            "../backend/models/image_model/amused_model",
            variant="fp16", torch_dtype=torch.float16
        )
        # move to GPU if available
        if torch.cuda.is_available():
            self.pipe = self.pipe.to("cuda")
        elif torch.backends.mps.is_available():
            self.pipe = self.pipe.to("mps")

    def split_chunks(self, text, n):
        # simple split by sentences; you can improve
        sentences = text.split(". ")
        avg = max(1, len(sentences)//n)
        return [" ".join(sentences[i:i+avg]) for i in range(0, len(sentences), avg)][:n]

    def GenerateImages(self, request, context):
        chunks = self.split_chunks(request.story, request.num_images)
        images_bytes = []
        for chunk in chunks:
            out = self.pipe(
                chunk,
                height=512, width=512,
                num_inference_steps=12,
                guidance_scale=7.5,
                negative_prompt="low quality, blurry",
                generator=torch.Generator().manual_seed(42)
            )
            img = out.images[0]
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            images_bytes.append(buf.getvalue())
        return storyboardai_pb2.ImageResponse(images=images_bytes)
