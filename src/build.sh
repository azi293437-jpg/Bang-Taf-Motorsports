#!/usr/bin/env bash
# Full pipeline: voice-over -> audio mix -> animation render -> MP4 export.
#   MODELS=/path/to/models BUILD=/path/to/build ./build.sh [en|ms|all]
# MODELS must contain: kokoro/ (kokoro-v1.0.onnx, voices-v1.0.bin), mms-zlm/ (facebook/mms-tts-zlm),
#                      whisper/ (openai/whisper-small, used for Malay take selection + QA).
set -euo pipefail
cd "$(dirname "$0")"
MODELS=${MODELS:?set MODELS}; BUILD=${BUILD:?set BUILD}; OUT=${OUT:-../output}
mkdir -p "$BUILD" "$OUT"
langs=${1:-all}; [ "$langs" = all ] && langs="en ms"
for L in $langs; do
  python3 build_vo.py "$L" "$MODELS" "$BUILD"
  python3 build_audio.py "$L" "$BUILD"
  node render_video.js "$L" "$BUILD" video 3
  TITLE=$(python3 -c "import json;print(json.load(open('script.json'))['$L']['title'])")
  (cd "$BUILD" && ffmpeg -y -loglevel error -f concat -safe 0 -i "segs_$L.txt" -i "mix_$L.wav" \
     -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -profile:v high -level 4.2 -pix_fmt yuv420p -c:a aac -b:a 320k -ar 48000 -shortest -movflags +faststart \
     -metadata title="$TITLE" -metadata artist="BANG TAF" "$OUT/$TITLE.mp4")
  cp "$BUILD/$TITLE.srt" "$OUT/"
  echo "exported: $OUT/$TITLE.mp4"
done
