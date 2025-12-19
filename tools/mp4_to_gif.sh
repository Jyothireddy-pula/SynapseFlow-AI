#!/bin/bash
# Usage: ./mp4_to_gif.sh input.mp4 output.gif
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 input.mp4 output.gif"
  exit 1
fi
IN=$1
OUT=$2
# Create optimized GIF using ffmpeg; requires ffmpeg installed
ffmpeg -y -i "$IN" -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif -f gif temp.gif
# Optimize with gifsicle if available
if command -v gifsicle >/dev/null 2>&1; then
  gifsicle -O3 temp.gif -o "$OUT"
  rm temp.gif
else
  mv temp.gif "$OUT"
fi
echo "Created $OUT"
