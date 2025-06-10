![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License: MIT](https://img.shields.io/badge/license-MIT-red.svg)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Deployed-blue?logo=kubernetes)
![Container](https://img.shields.io/badge/Container-Docker-blue?logo=docker)
![Python](https://img.shields.io/badge/Worker-Python%203.12-blue?logo=python)
![Celery](https://img.shields.io/badge/Celery-5.3.1-brightgreen?logo=celery)
![RabbitMQ](https://img.shields.io/badge/Queue-RabbitMQ-FF6600?logo=rabbitmq)
![Redis](https://img.shields.io/badge/Redis-7.x-red?logo=redis)
![FFmpeg](https://img.shields.io/badge/Transcoder-FFmpeg-black?logo=ffmpeg)
![Storage](https://img.shields.io/badge/S3%20(MinIO)-storage-red?logo=minio)
![Infisical](https://img.shields.io/badge/Secrets-Infisical-yellow)

# 📦 CMS Transcode Worker

**cms-transcode-worker**는 CMS 시스템의 **비디오 트랜스코딩**을 담당하는 파이썬 Celery 워커입니다.  
사용자가 업로드한 비디오를 HLS로 변환(480p/1080p)하고, 진행 상황을 실시간으로 전달합니다.

---

## 🎨 아키텍처 다이어그램

![Architecture Diagram](./Architecture_Diagram_v3.png)
> 이해를 위해 RabbitMQ 를 분할하였습니다.  
> 실제 작동시에 RabbitMQ 는 독립된 컨테이너에 위치합니다.

---

## 📚 목차

1. [🌟 개요](#-개요)  
2. [🛠️ 주요 기능](#-주요-기능)  
3. [🔧 실행 방법](#-실행-방법)  
4. [🚀 트랜스코딩 파이프라인](#-트랜스코딩-파이프라인)  
5. [⚙️ 주요 기술 및 구성 요소](#-주요-기술-및-구성-요소)  
6. [☸️ 쿠버네티스 배포](#-쿠버네티스-배포)  
7. [📂 디렉토리 구조](#-디렉토리-구조)  
8. [📝 기여 및 라이선스](#-기여-및-라이선스)
---

## 🌟 개요

- **CMS BE(Spring Boot)** 에서 **Transcode.Request MQ**로 **트랜스코딩 요청**을 발행  
- **Transcode Consumer**가 요청을 받아서 **Transcode broker**(Celery with RabbitMQ)에 **enqueue**  
- **Transcode Worker**가 **FFmpeg**로 **비디오를 HLS로 변환**  
- 진행률과 상태는 **Redis / RabbitMQ**로 CMS BE에 전달  
- 최종 결과는 **S3(Minio)** 에 업로드  
- 최근에는 **쿠버네티스 환경으로 이전**하여 안정성과 유연성을 강화했습니다.

---

## 🛠️ 주요 기능

✅ **480p / 1080p HLS 변환**  
✅ **진행률 실시간 업데이트 (Redis / RabbitMQ)**  
✅ **트랜스코딩 상태 업데이트 (Success / Fail)**  
✅ **S3에 HLS 세그먼트 업로드**

---


## 🔧 실행 방법

```bash
# 1. 환경 변수 파일 복사 및 수정
cp .env.example .env
# .env 파일에서 RabbitMQ, Redis, S3 등 연결 정보 설정

# 2. Docker Compose로 서비스 실행
docker-compose up --build
```

## 🚀 트랜스코딩 파이프라인

1️⃣ **사용자 요청 → CMS BE**  
- 사용자가 CMS FE(React)에서 파일 업로드를 완료하면, CMS BE(Spring Boot)로 "S3 업로드 완료" 요청이 전송됩니다.

2️⃣ **트랜스코딩 요청 → Transcode.Request MQ**  
- CMS BE는 트랜스코딩 요청을 **Transcode.Request MQ(RabbitMQ)**로 발행(PUB)합니다.  
- 이 메시지에는 S3 경로, 파일명, 파일타입 등의 메타데이터가 담깁니다.

3️⃣ **Transcode Consumer → 브로커 → 워커**  
- **Transcode Consumer**(Python)는 Transcode.Request MQ를 구독(SUB)하여 새로운 요청을 수신합니다.  
- 요청을 Celery 기반의 **Transcode broker**로 enqueue(등록)합니다.  
- **Transcode Worker**(Celery Worker)는 큐에서 작업을 꺼내서 **FFmpeg**로 HLS 변환을 수행합니다.
  - 변환 중 **Redis**로 진행률을 실시간 업데이트합니다.
  - 진행률과 상태는 **Transcode.Status MQ**로 발행됩니다.
  > `transcode_service` 에서 redis 와 rabbitMQ 둘 다 사용해 진행률을 보내주고 있습니다.   
  > 사용하지 않는 Notifire 는 주석처리해도 무관합니다.

4️⃣ **진행 상태 전송 → CMS BE**  
- CMS BE는 **Transcode.Status MQ**를 구독(SUB)하여 트랜스코딩의 상태 및 진행률을 실시간으로 확인합니다.

5️⃣ **트랜스코딩 결과 → S3 & FE**  
- 변환된 HLS 출력(m3u8, ts 파일들)은 **S3**에 업로드됩니다.  
- 최종적으로, CMS BE는 변환된 HLS 경로 정보를 **CMS FE**로 전달하여 사용자에게 알려줍니다.

---

## ⚙️ 주요 기술 및 구성 요소

- **Spring Boot (CMS BE)**: API 서버, MQ 연동
- **React (CMS FE)**: 사용자 인터페이스
- **RabbitMQ**: 트랜스코딩 요청/상태 처리용 메시지 큐
- **Celery Worker**: 트랜스코딩 태스크 처리
- **FFmpeg**: 비디오를 HLS(480p/1080p)로 변환
- **S3(MinIO)**: 영상 파일 저장소
- **Redis**: 트랜스코딩 진행률 실시간 업데이트
- **Kubernetes**: 컨테이너 오케스트레이션, 배포 자동화

---

## ☸️ 쿠버네티스 배포

본 프로젝트는 현재 **쿠버네티스(Kubernetes)** 환경에서 배포 및 운영됩니다.  
이를 통해 컨테이너 기반의 서비스를 보다 유연하고 안정적으로 관리하고 있습니다.

---

## 📂 디렉토리 구조

```plaintext
.
├── Architecture_Diagram_v3.png
├── Dockerfile
├── docker-compose.yml
├── k8s/                            # 쿠버네티스 매니페스트
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── cms-transcode-consumer/
│   │   └── deployment.yaml
│   ├── cms-transcode-worker/
│   │   └── deployment.yaml
│   └── redis/
│       ├── deployment.yaml
│       └── service.yaml
├── requirements.txt
├── src/                            # 소스 코드
│   ├── consumer/                   # RabbitMQ 컨슈머
│   │   └── request_consumer.py
│   ├── core/                       # 설정 및 공통 모듈
│   │   ├── config.py
│   │   └── s3.py
│   ├── notifiers/                  # MQ 및 Redis 알림
│   │   ├── rabbitmq_notifier.py
│   │   └── redis_notifier.py
│   ├── services/                   # 트랜스코딩 서비스 로직
│   │   └── transcode_service.py
│   ├── tasks/                      # Celery 태스크
│   │   └── transcode_video_task.py
│   ├── tests/                      # 테스트 유틸리티
│   │   ├── redis_subscriber.py
│   │   └── send_transcode_request.py
│   ├── utils/                      # 유틸리티
│   │   ├── date_utils.py
│   │   ├── io_utils.py
│   │   └── logging_utils.py
│   └── worker/
│       └── celery_worker.py
└── README.md
```

## 📝 기여 및 라이선스

이 프로젝트는 [MIT License](LICENSE)로 배포됩니다.  
이슈나 PR은 언제든 환영합니다! 🙌  
문의나 요청사항은 [Issues](https://github.com/handong-app/cms-transcode-worker/issues)에 남겨주세요.

---

🌟 **감사합니다!** 🌟