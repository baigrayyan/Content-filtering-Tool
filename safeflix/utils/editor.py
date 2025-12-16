import moviepy.editor as mp
import os

def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            merged[-1] = (last[0], max(last[1], current[1]))
        else:
            merged.append(current)
    return merged

def create_clean_video(input_path, bad_intervals, output_path):
    clip = mp.VideoFileClip(input_path)
    duration = clip.duration
    bad_intervals = merge_intervals(bad_intervals)

    good_clips = []
    start = 0
    for bad_start, bad_end in bad_intervals:
        bad_end = min(bad_end, duration)
        if start < bad_start:
            good_clips.append(clip.subclip(start, bad_start))
        start = bad_end
    if start < duration:
        good_clips.append(clip.subclip(start, duration))

    if not good_clips:
        clip.close()
        return False

    final = mp.concatenate_videoclips(good_clips)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    final.close()
    clip.close()
    return True