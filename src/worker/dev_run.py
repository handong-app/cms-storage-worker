from src.tasks.video_tasks import transcode_video_task

if __name__ == "__main__":
    transcode_video_task.delay("somefile.mp4")