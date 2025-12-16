# 4-Split Video Sync Tool

타임스탬프 기반으로 여러 영상을 동기화하여 2x2 그리드로 합성하는 도구

Synchronize multiple videos based on timestamps and combine them into a 2x2 grid layout.

![4-Split Demo](https://raw.githubusercontent.com/hwkim3330/4split_synced/main/demo.png)

## Features

- **Auto Sync**: 파일명 또는 메타데이터의 타임스탬프를 자동 감지하여 동기화
- **2x2 Grid Layout**: 4개의 영상을 균등하게 2x2 그리드로 배치
- **Flexible Input**: MP4, MOV, WebM 등 다양한 포맷 지원
- **Custom Resolution**: 출력 해상도 지정 가능 (기본 1920x1080)
- **Audio Preservation**: 기준 영상의 오디오 트랙 유지

## Requirements

- Python 3.7+
- FFmpeg (ffmpeg, ffprobe)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Installation

```bash
git clone https://github.com/hwkim3330/4split_synced.git
cd 4split_synced
chmod +x 4split_sync.py
```

## Usage

### Basic Usage

```bash
# 4개 영상을 2x2로 합성 (동기화 없이)
python3 4split_sync.py video1.mp4 video2.mp4 video3.mp4 video4.mp4 -o output.mp4
```

### Auto Sync (Recommended)

파일명에 타임스탬프가 포함된 경우 자동 동기화:

```bash
python3 4split_sync.py \
  IMG_0013.MOV \
  screenrecord_20251211183500.mp4 \
  "Screencast from 2025-12-11 18-35-02.webm" \
  recording-2025-12-11_18.35.02.mp4 \
  --auto-sync \
  -o synced_output.mp4
```

### Manual Offsets

각 영상의 시작 오프셋을 수동으로 지정:

```bash
python3 4split_sync.py video1.mp4 video2.mp4 video3.mp4 video4.mp4 \
  --offsets 0 3 1 1 \
  -o output.mp4
```

### Options

| Option | Description |
|--------|-------------|
| `-o, --output` | 출력 파일명 (기본: 4split_output.mp4) |
| `--auto-sync` | 파일명/메타데이터 타임스탬프로 자동 동기화 |
| `--reference N` | 기준 영상 인덱스 (0-3, 기본: 0) |
| `--offsets A B C D` | 각 영상별 수동 오프셋 (초) |
| `--resolution WxH` | 출력 해상도 (기본: 1920x1080) |
| `--layout` | 레이아웃 스타일 (2x2, main+3, horizontal) |

## Supported Timestamp Formats

파일명에서 자동 인식되는 타임스탬프 형식:

- `20251211183500` (YYYYMMDDHHMMSS)
- `2025-12-11 18-35-02` (YYYY-MM-DD HH-MM-SS)
- `2025-12-11_18.35.02` (YYYY-MM-DD_HH.MM.SS)

## Layout

```
+------------+------------+
|  Video 1   |  Video 2   |
|  (0:v)     |  (1:v)     |
+------------+------------+
|  Video 3   |  Video 4   |
|  (2:v)     |  (3:v)     |
+------------+------------+
```

## Example Use Cases

### Multi-angle Recording
동시에 여러 각도로 촬영한 영상을 동기화하여 합성

### Screen + Camera Recording
화면 녹화와 카메라 녹화를 동기화하여 튜토리얼 영상 제작

### Multi-device Live Stream
여러 디바이스에서 녹화한 영상을 하나의 화면에 합성

## License

MIT License

## Author

[hwkim3330](https://github.com/hwkim3330)
