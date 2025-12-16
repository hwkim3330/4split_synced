# 4-Split Video Sync

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.7+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/javascript-ES6+-yellow.svg" alt="JavaScript">
</p>

<p align="center">
  <strong>Synchronize multiple videos based on timestamps and combine them into a 2x2 grid layout</strong>
</p>

<p align="center">
  타임스탬프 기반으로 여러 영상을 동기화하여 2x2 그리드로 합성
</p>

<p align="center">
  <a href="https://hwkim3330.github.io/4split_synced/">Live Demo</a> •
  <a href="#web-version">Web Version</a> •
  <a href="#cli-version">CLI Version</a> •
  <a href="#use-cases">Use Cases</a>
</p>

---

## Preview

```
+-------------------+-------------------+
|                   |                   |
|     Video 1       |     Video 2       |
|   (Top Left)      |   (Top Right)     |
|                   |                   |
+-------------------+-------------------+
|                   |                   |
|     Video 3       |     Video 4       |
|  (Bottom Left)    |  (Bottom Right)   |
|                   |                   |
+-------------------+-------------------+
```

## Features

| Feature | Web | CLI |
|---------|:---:|:---:|
| 2x2 Grid Layout | O | O |
| Time Offset Sync | O | O |
| Auto Timestamp Detection | - | O |
| Real-time Preview | O | - |
| Custom Resolution | O | O |
| Quality Settings | O | O |
| Batch Processing | - | O |
| Audio Track | O | O |

---

## Web Version

**Try it now**: [https://hwkim3330.github.io/4split_synced/](https://hwkim3330.github.io/4split_synced/)

### How to Use

1. **Upload Videos** - Click each slot (1-4) to upload video files
2. **Set Offsets** - Adjust time offset for each video to sync them
3. **Preview** - Click Play to preview the synchronized result
4. **Export** - Click Export to download the merged video

### Supported Formats

- MP4, WebM, MOV, and other browser-supported formats
- Output: WebM (VP9)

### Browser Compatibility

- Chrome 60+
- Firefox 55+
- Edge 79+
- Safari 14.1+

---

## CLI Version

For batch processing, higher quality output, or automation.

### Requirements

- Python 3.7+
- FFmpeg

```bash
# Ubuntu/Debian
sudo apt install ffmpeg python3

# macOS
brew install ffmpeg python3
```

### Installation

```bash
git clone https://github.com/hwkim3330/4split_synced.git
cd 4split_synced
chmod +x 4split_sync.py
```

### Usage

#### Basic (No Sync)

```bash
python3 4split_sync.py video1.mp4 video2.mp4 video3.mp4 video4.mp4 -o output.mp4
```

#### Auto Sync (Recommended)

Automatically detect timestamps from filenames:

```bash
python3 4split_sync.py \
  IMG_0013.MOV \
  screenrecord_20251211183500.mp4 \
  "Screencast from 2025-12-11 18-35-02.webm" \
  recording-2025-12-11_18.35.02.mp4 \
  --auto-sync \
  -o synced_output.mp4
```

#### Manual Offsets

Specify exact offset (in seconds) for each video:

```bash
python3 4split_sync.py \
  video1.mp4 video2.mp4 video3.mp4 video4.mp4 \
  --offsets 0 3 1 1 \
  -o output.mp4
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output filename | `4split_output.mp4` |
| `--auto-sync` | Auto-detect timestamps from filenames | Off |
| `--reference N` | Reference video index (0-3) | 0 |
| `--offsets A B C D` | Manual offset per video (seconds) | - |
| `--resolution WxH` | Output resolution | `1920x1080` |
| `--layout` | Layout style (`2x2`, `main+3`, `horizontal`) | `2x2` |

### Supported Timestamp Formats

The auto-sync feature recognizes these filename patterns:

| Pattern | Example |
|---------|---------|
| `YYYYMMDDHHMMSS` | `video_20251211183500.mp4` |
| `YYYY-MM-DD HH-MM-SS` | `Screencast from 2025-12-11 18-35-02.webm` |
| `YYYY-MM-DD_HH.MM.SS` | `recording-2025-12-11_18.35.02.mp4` |

---

## Use Cases

### Multi-angle Recording

Synchronize videos shot from multiple angles at the same event:

```bash
# Wedding video from 4 cameras
python3 4split_sync.py \
  camera1_front.mp4 \
  camera2_side.mp4 \
  camera3_back.mp4 \
  camera4_drone.mp4 \
  --auto-sync -o wedding_multiview.mp4
```

### Screen + Camera Recording

Combine screen recordings with face camera:

```bash
# Tutorial with screen recording + webcam
python3 4split_sync.py \
  screen_record.mp4 \
  webcam.mp4 \
  terminal.mp4 \
  browser.mp4 \
  --offsets 0 0.5 0 0 -o tutorial.mp4
```

### Multi-device Live Stream

Merge recordings from multiple phones/devices:

```bash
# Concert recorded from 4 phones
python3 4split_sync.py \
  iphone_*.MOV \
  --auto-sync -o concert_4view.mp4
```

### Gaming / Sports Analysis

Compare multiple perspectives or replays:

```bash
python3 4split_sync.py \
  player1_pov.mp4 \
  player2_pov.mp4 \
  spectator.mp4 \
  minimap.mp4 \
  --offsets 0 0.2 0.1 0 -o game_analysis.mp4
```

---

## How It Works

### Timestamp Extraction

1. **Filename parsing**: Extracts datetime from filename patterns
2. **Metadata reading**: Falls back to file creation time from video metadata
3. **Offset calculation**: Computes relative offsets based on reference video

### Video Processing

1. **Scaling**: Each video is scaled to fit its quadrant (960x540 for 1080p output)
2. **Padding**: Letterboxing/pillarboxing preserves aspect ratio
3. **Composition**: Videos are arranged in 2x2 grid using ffmpeg filter_complex
4. **Audio**: First video's audio track is preserved

---

## Examples

### Input

| Position | File | Start Time | Offset |
|----------|------|------------|--------|
| Top Left | IMG_0013.MOV | 18:35:03 | 0s (reference) |
| Top Right | outgoing_20251211183500.mp4 | 18:35:00 | 3s |
| Bottom Left | Screencast 2025-12-11 18-35-02.webm | 18:35:02 | 1s |
| Bottom Right | simplescreenrecorder_18.35.02.mp4 | 18:35:02 | 1s |

### Command

```bash
python3 4split_sync.py \
  IMG_0013.MOV \
  outgoing_20251211183500.mp4 \
  "Screencast from 2025-12-11 18-35-02.webm" \
  simplescreenrecorder-2025-12-11_18.35.02.mp4 \
  --auto-sync \
  --reference 0 \
  -o 4split_synced.mp4
```

### Output

Single 1920x1080 MP4 with all 4 videos synchronized and playing together.

---

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Author

**hwkim3330** - [GitHub](https://github.com/hwkim3330)

---

<p align="center">
  Made with Claude Code
</p>
