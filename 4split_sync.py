#!/usr/bin/env python3
"""
4-Split Video Sync Tool
타임스탬프 기반으로 여러 영상을 동기화하여 2x2 그리드로 합성

Usage:
    python3 4split_sync.py video1.mp4 video2.mp4 video3.mp4 video4.mp4 -o output.mp4
    python3 4split_sync.py *.mp4 --auto-sync  # 파일명 타임스탬프 자동 감지
"""

import argparse
import subprocess
import re
import os
import sys
from datetime import datetime
from pathlib import Path


def get_video_info(filepath):
    """ffprobe로 영상 정보 가져오기"""
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', filepath
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {filepath}")

    import json
    data = json.loads(result.stdout)

    # 영상 스트림 찾기
    video_stream = None
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_stream = stream
            break

    return {
        'duration': float(data['format'].get('duration', 0)),
        'width': video_stream.get('width', 1920) if video_stream else 1920,
        'height': video_stream.get('height', 1080) if video_stream else 1080,
        'creation_time': data['format'].get('tags', {}).get('creation_time', ''),
    }


def extract_timestamp_from_filename(filename):
    """파일명에서 타임스탬프 추출"""
    name = os.path.basename(filename)

    # 패턴들: YYYYMMDD_HHMMSS, YYYY-MM-DD HH-MM-SS, etc.
    patterns = [
        # 20251211183500 형식
        r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})',
        # 2025-12-11 18-35-02 형식
        r'(\d{4})-(\d{2})-(\d{2})[\s_](\d{2})[.-](\d{2})[.-](\d{2})',
        # 2025-12-11_18.35.02 형식
        r'(\d{4})-(\d{2})-(\d{2})_(\d{2})\.(\d{2})\.(\d{2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            groups = match.groups()
            try:
                dt = datetime(
                    int(groups[0]), int(groups[1]), int(groups[2]),
                    int(groups[3]), int(groups[4]), int(groups[5])
                )
                return dt
            except ValueError:
                continue

    return None


def extract_timestamp_from_metadata(filepath):
    """메타데이터에서 타임스탬프 추출"""
    info = get_video_info(filepath)
    creation_time = info.get('creation_time', '')

    if creation_time:
        # ISO 8601 형식 파싱
        try:
            # 2025-12-11T09:35:03.000000Z
            dt = datetime.fromisoformat(creation_time.replace('Z', '+00:00'))
            return dt
        except ValueError:
            pass

    return None


def calculate_offsets(videos, reference_idx=0):
    """기준 영상 대비 각 영상의 오프셋 계산"""
    timestamps = []

    for video in videos:
        # 파일명에서 먼저 시도
        ts = extract_timestamp_from_filename(video)
        if not ts:
            # 메타데이터에서 시도
            ts = extract_timestamp_from_metadata(video)
        timestamps.append(ts)

    # 기준 타임스탬프
    ref_ts = timestamps[reference_idx]
    if not ref_ts:
        print(f"Warning: Could not extract timestamp from reference video {videos[reference_idx]}")
        return [0.0] * len(videos)

    offsets = []
    for i, ts in enumerate(timestamps):
        if ts:
            # 기준 영상보다 먼저 시작한 경우 양수 오프셋
            delta = (ref_ts - ts).total_seconds()
            offsets.append(max(0, delta))
        else:
            print(f"Warning: Could not extract timestamp from {videos[i]}, using 0 offset")
            offsets.append(0.0)

    return offsets


def create_4split_video(videos, output, offsets=None, layout='2x2', resolution='1920x1080'):
    """4분할 영상 생성"""
    if len(videos) != 4:
        raise ValueError("Exactly 4 videos are required")

    if offsets is None:
        offsets = [0.0] * 4

    # 해상도 파싱
    out_w, out_h = map(int, resolution.split('x'))

    if layout == '2x2':
        cell_w, cell_h = out_w // 2, out_h // 2
    elif layout == 'main+3':
        # 메인 영상 크게, 나머지 작게
        cell_w, cell_h = out_w // 2, out_h // 2
    else:
        cell_w, cell_h = out_w // 2, out_h // 2

    # 가장 짧은 영상 길이 찾기
    durations = []
    for i, video in enumerate(videos):
        info = get_video_info(video)
        effective_duration = info['duration'] - offsets[i]
        durations.append(effective_duration)

    min_duration = min(durations)

    # ffmpeg 명령 구성
    cmd = ['ffmpeg', '-y']

    # 입력 파일들 (오프셋 적용)
    for i, (video, offset) in enumerate(zip(videos, offsets)):
        if offset > 0:
            cmd.extend(['-ss', str(offset)])
        cmd.extend(['-i', video])

    # 필터 복합체
    filter_parts = []

    # 각 영상 스케일링
    for i in range(4):
        filter_parts.append(
            f"[{i}:v]scale={cell_w}:{cell_h}:force_original_aspect_ratio=decrease,"
            f"pad={cell_w}:{cell_h}:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v{i}]"
        )

    # 2x2 그리드 합성
    filter_parts.append("[v0][v1]hstack=inputs=2[top]")
    filter_parts.append("[v2][v3]hstack=inputs=2[bottom]")
    filter_parts.append("[top][bottom]vstack=inputs=2[v]")

    filter_complex = ";".join(filter_parts)

    cmd.extend([
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-map', '0:a?',  # 첫 번째 영상의 오디오 (있으면)
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-t', str(min_duration),
        output
    ])

    print(f"Running ffmpeg...")
    print(f"Output: {output}")
    print(f"Duration: {min_duration:.2f}s")
    print(f"Offsets: {offsets}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False

    print(f"Success! Created {output}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='4-Split Video Sync Tool - 타임스탬프 기반 영상 동기화 및 2x2 합성'
    )
    parser.add_argument('videos', nargs='+', help='Input video files (exactly 4)')
    parser.add_argument('-o', '--output', default='4split_output.mp4', help='Output file')
    parser.add_argument('--auto-sync', action='store_true',
                        help='Automatically sync based on filename timestamps')
    parser.add_argument('--reference', type=int, default=0,
                        help='Reference video index (0-3) for sync')
    parser.add_argument('--offsets', nargs=4, type=float,
                        help='Manual offsets in seconds for each video')
    parser.add_argument('--resolution', default='1920x1080',
                        help='Output resolution (default: 1920x1080)')
    parser.add_argument('--layout', choices=['2x2', 'main+3', 'horizontal'],
                        default='2x2', help='Layout style')

    args = parser.parse_args()

    if len(args.videos) != 4:
        print(f"Error: Exactly 4 videos required, got {len(args.videos)}")
        sys.exit(1)

    # 파일 존재 확인
    for video in args.videos:
        if not os.path.exists(video):
            print(f"Error: File not found: {video}")
            sys.exit(1)

    # 오프셋 계산
    if args.offsets:
        offsets = args.offsets
    elif args.auto_sync:
        print("Auto-detecting timestamps...")
        offsets = calculate_offsets(args.videos, args.reference)
        for i, (video, offset) in enumerate(zip(args.videos, offsets)):
            print(f"  [{i}] {os.path.basename(video)}: {offset:.2f}s offset")
    else:
        offsets = [0.0] * 4

    # 4분할 영상 생성
    success = create_4split_video(
        args.videos,
        args.output,
        offsets=offsets,
        layout=args.layout,
        resolution=args.resolution
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
