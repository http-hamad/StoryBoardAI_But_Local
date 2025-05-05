import io, tempfile
from pydub import AudioSegment
from moviepy.editor import *
import numpy as np
import os

import storyboardai_pb2, storyboardai_pb2_grpc

class VideoServiceServicer(storyboardai_pb2_grpc.VideoServiceServicer):
    def GenerateVideo(self, request, context):
        try:
            # Step 1: Save images
            img_paths = []
            for i, img_bytes in enumerate(request.images):
                tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                tf.write(img_bytes)
                tf.flush()
                img_paths.append(tf.name)

            # Step 2: Save voiceover
            voice_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            with open(voice_path, "wb") as vf:
                vf.write(request.voiceover)

            # Step 3: Save background music (if any)
            music_path = None
            if request.music_track:
                music_path = f"../backend/models/voice_model/music/{request.music_track}"

            # Step 4: Mix audio using pydub
            voice = AudioSegment.from_file(voice_path)
            total_duration_ms = len(voice)

            if music_path:
                music = AudioSegment.from_file(music_path) - 5  # lower music volume
                music = music[:len(voice)]
                combined = music.overlay(voice)
            else:
                combined = voice

            # Export mixed audio
            mixed_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            combined.export(mixed_audio_path, format="wav")

            # Step 5: Prepare video clips with animated zoom
            total_duration = total_duration_ms / 1000
            img_dur = total_duration / len(img_paths)

            def animated_image(path, duration):
                img = ImageClip(path, duration=duration)
                return img.resize(lambda t: 1.05 + 0.02 * np.sin(2 * np.pi * t / duration)).fadein(1).fadeout(1)

            clips = []
            for p in img_paths:
                clips.append(animated_image(p, img_dur))

            video_clip = concatenate_videoclips(clips, method="compose", padding=-1)
            
            # Step 6: Handle audio properly
            audio_clip = AudioFileClip(mixed_audio_path)
            final_video = video_clip.set_audio(audio_clip)
            final_video = final_video.set_duration(total_duration)

            # Step 7: Export final video
            tf_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            final_video.write_videofile(
                tf_out.name,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                threads=4,
                preset='ultrafast'
            )

            # Step 8: Read and return video
            with open(tf_out.name, "rb") as f:
                data = f.read()

            # Cleanup
            os.remove(voice_path)
            os.remove(mixed_audio_path)
            for p in img_paths:
                os.remove(p)
            os.remove(tf_out.name)

            return storyboardai_pb2.VideoResponse(video=data)
            
        except Exception as e:
            # Cleanup in case of error
            if 'voice_path' in locals() and os.path.exists(voice_path):
                os.remove(voice_path)
            if 'mixed_audio_path' in locals() and os.path.exists(mixed_audio_path):
                os.remove(mixed_audio_path)
            if 'img_paths' in locals():
                for p in img_paths:
                    if os.path.exists(p):
                        os.remove(p)
            if 'tf_out' in locals() and os.path.exists(tf_out.name):
                os.remove(tf_out.name)
            raise e
