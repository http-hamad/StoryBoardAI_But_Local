import io
import os
import torch
import soundfile as sf
import numpy as np
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset

import storyboardai_pb2, storyboardai_pb2_grpc

class VoiceServiceServicer(storyboardai_pb2_grpc.VoiceServiceServicer):
    def __init__(self):
        proc_path = "/app/backend/models/voice_model/tts_processors/speecht5_tts"
        model_path = "/app/backend/models/voice_model/tts_models/speecht5_tts"
        vocoder_path = "/app/backend/models/voice_model/tts_vocoders/speecht5_hifigan"
        embedding_path = "/app/backend/models/voice_model/speaker_embedding.npy"

        self.processor = SpeechT5Processor.from_pretrained(proc_path)
        self.model = SpeechT5ForTextToSpeech.from_pretrained(model_path)
        self.vocoder = SpeechT5HifiGan.from_pretrained(vocoder_path)

        # Load or create speaker embedding
        if os.path.exists(embedding_path):
            self.speaker_embedding = torch.tensor(np.load(embedding_path)).unsqueeze(0)
        else:
            print("Generating speaker embedding...")
            ds = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            self.speaker_embedding = torch.tensor(ds[7306]["xvector"]).unsqueeze(0)
            # Save the embedding for future use
            os.makedirs(os.path.dirname(embedding_path), exist_ok=True)
            np.save(embedding_path, self.speaker_embedding.squeeze(0).numpy())
            print("Speaker embedding saved.")

    def GenerateVoice(self, request, context):
        # single-chunk for simplicity; split if needed
        inputs = self.processor(text=request.prompt, return_tensors="pt", truncation=True)
        speech = self.model.generate_speech(
            inputs["input_ids"], self.speaker_embedding, vocoder=self.vocoder
        )
        buf = io.BytesIO()
        sf.write(buf, speech.numpy(), samplerate=16000, format="WAV")
        return storyboardai_pb2.AudioResponse(audio=buf.getvalue())
