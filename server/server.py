from concurrent import futures
import grpc
import storyboardai_pb2_grpc

from text_service import StoryServiceServicer
from image_service import ImageServiceServicer
from voice_service import VoiceServiceServicer
from video_service import VideoServiceServicer

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    storyboardai_pb2_grpc.add_StoryServiceServicer_to_server(StoryServiceServicer(), server)
    storyboardai_pb2_grpc.add_ImageServiceServicer_to_server(ImageServiceServicer(), server)
    storyboardai_pb2_grpc.add_VoiceServiceServicer_to_server(VoiceServiceServicer(), server)
    storyboardai_pb2_grpc.add_VideoServiceServicer_to_server(VideoServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("gRPC server listening on port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
