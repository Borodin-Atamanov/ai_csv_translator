#!/usr/bin/bash
fps=001;
ffmpeg_path='ffmpeg';
NEWDIR="$HOME/timelapse/";
CUR_RESOLUTION=`xdpyinfo | grep 'dimensions:'| awk '{print $2}'`;
echo $CUR_RESOLUTION;
mkdir -p "$NEWDIR";
cd "$NEWDIR";

time ${ffmpeg_path} -hide_banner -r ${fps} -f x11grab -s $CUR_RESOLUTION -i :0.0 -pix_fmt yuv420p -vf null -af anull -profile:v baseline -vcodec libx264 -preset ultrafast -crf 24 -movflags +faststart -f segment -segment_time 10:00:00 -reset_timestamps 1 $NEWDIR$(($(find . -type f -name "*.*" | wc -l)+1))-screencast-%06d.mkv

