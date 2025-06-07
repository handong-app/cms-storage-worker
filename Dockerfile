FROM python:3.12-slim
# 베이스 이미지 (slim 은 일부 기본 라이브러리 제외한 버전, 가벼움)

LABEL authors="callein"


WORKDIR /src

RUN apt-get update && apt-get install -y ffmpeg

ENV PYTHONPATH=/src

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt


COPY ./src ./src

CMD ["celery", "-A", "src.worker.celery_worker.celery_app", "worker", "--loglevel=info"]
