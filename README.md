# StoryBoard AI

StoryBoard AI is a powerful AI-powered storytelling platform that generates complete storyboards with text, images, voice narration, and video. The system uses multiple AI models to create cohesive and engaging visual stories.

## Features

- **Story Generation**: Creates engaging stories using Llama 3.2
- **Image Generation**: Converts story segments into images using Amused model
- **Voice Synthesis**: Generates natural-sounding voice narration using SpeechT5
- **Video Creation**: Combines images and audio into a cohesive video

## Architecture

The project follows a microservices architecture using gRPC:

- **Text Service**: Story generation
- **Image Service**: Image generation from text
- **Voice Service**: Text-to-speech conversion
- **Video Service**: Video compilation and effects

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- FFmpeg
- Required AI models (see Setup section)

## Setup

1. **Clone the repository**
```bash
git clone https://github.com/http-hamad/NLP.git
cd NLP/v2
```

2. **Download Required Models**
Place the following models in the `backend/models` directory:

```
backend/models/
├── text_model/
│   ├── txt_models/
│   │   └── meta-llama/
│   │       └── Llama-3.2-1B/
│   │   └── txt_tokenizers/
│   │       └── meta-llama/
│   │           └── Llama-3.2-1B/
│   ├── image_model/
│   │   └── amused_model/
│   └── voice_model/
│       ├── tts_models/
│       │   └── speecht5_tts/
│       ├── tts_processors/
│       │   └── speecht5_tts/
│       └── tts_vocoders/
│           └── speecht5_hifigan/
```

3. **Build and Run with Docker**
```bash
docker-compose up --build
```

## Usage

The service exposes a gRPC API on port 50051. You can use the provided `client_test.py` to test the service:

```bash
python client_test.py
```

### API Endpoints

1. **Generate Story**
   - Input: Theme and prompt
   - Output: Generated story text

2. **Generate Images**
   - Input: Story text and number of images
   - Output: List of generated images

3. **Generate Voice**
   - Input: Text to narrate
   - Output: Audio file

4. **Generate Video**
   - Input: Images, voiceover, and optional music
   - Output: Final video file

## Project Structure

```
v2/
├── backend/
│   └── models/          # AI models directory
├── proto/              # Protocol buffer definitions
├── server/             # gRPC service implementations
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── requirements.txt    # Python dependencies
```

## Development

1. **Local Development**
   - Install dependencies: `pip install -r requirements.txt`
   - Run server: `python server/server.py`

2. **Testing**
   - Use `client_test.py` for integration testing
   - Modify test parameters in the script

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Llama 3.2 for text generation
- Amused model for image generation
- SpeechT5 for voice synthesis
- MoviePy for video processing 