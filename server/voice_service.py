import io
import torch
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset

import storyboardai_pb2, storyboardai_pb2_grpc

class VoiceServiceServicer(storyboardai_pb2_grpc.VoiceServiceServicer):
    def __init__(self):
        proc_path = "../backend/models/voice_model/tts_processors/speecht5_tts"
        model_path = "../backend/models/voice_model/tts_models/speecht5_tts"
        vocoder_path = "../backend/models/voice_model/tts_vocoders/speecht5_hifigan"

        self.processor = SpeechT5Processor.from_pretrained(proc_path)
        self.model = SpeechT5ForTextToSpeech.from_pretrained(model_path)
        self.vocoder = SpeechT5HifiGan.from_pretrained(vocoder_path)

        ds = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
        self.speaker_embedding = torch.tensor(ds[7306]["xvector"]).unsqueeze(0)

    def GenerateVoice(self, request, context):
        # single-chunk for simplicity; split if needed
        inputs = self.processor(text=request.prompt, return_tensors="pt", truncation=True)
        speech = self.model.generate_speech(
            inputs["input_ids"], self.speaker_embedding, vocoder=self.vocoder
        )
        buf = io.BytesIO()
        sf.write(buf, speech.numpy(), samplerate=16000, format="WAV")
        return storyboardai_pb2.AudioResponse(audio=buf.getvalue())
