import ffmpeg
import librosa
import librosa.display
import numpy as np
import os
import sys
from pydub import AudioSegment
import subprocess
import argparse
import tempfile


# Description: Computes a chromagram
# Input: numpy.ndarray (audio), sampling rate
# Return: numpy.ndarray (Normalized energy for each chroma bin at each frame)
# Uses: Librosa
def defineChromagram(audio, sr):
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)
    return chroma


# Description: Runs .bat file to combine video and audio
# Input: Location of audio file, Location of Video File, Save Location
# Return: None
# Uses: ffmpeg
def combine(audio_file, video_file, save_location):
    cmd = ['ffmpeg', '-y', '-i', video_file, '-i', audio_file, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a',
           'aac', '-b:a', '160k', save_location]
    subprocess.run(cmd)


# Description: Runs .bat file to extract audio file from video
# Input: Location of Video File, Save Location
def extract(video_file, save_location):
    cmd = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', video_file, save_location]
    subprocess.run(cmd)


# Vars
n_fft = 4410
hop_size = 2205
sampling_rate = 22050
duration_limit = 60 # maximum duration of audio-video clips used to synchronize in seconds


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replaces the audio in a video file with '
                                                 'an external audio and maintains AV sync.')
    parser.add_argument('-v', '--video', help='import video file', required=True, type=str)
    parser.add_argument('-a', '--audio', help='import audio file', required=True, type=str)
    parser.add_argument('-o', '--output', help='export video file', required=True, type=str)

    args = parser.parse_args()
    if not os.path.exists(args.video):
        print('Video file does not exist.')
        sys.exit(-1)
    if not os.path.exists(args.audio):
        print('Audio file does not exist.')
        sys.exit(-1)

##############---------LOAD FILES---------##############

# Load audio file
audio_file = args.audio
audio, _ = librosa.load(audio_file, sr=sampling_rate, mono=True, duration=duration_limit)

# Load video file, creates .wav file of the video audio
video_file = args.video
handle, video_audio_file = tempfile.mkstemp(suffix='.wav')
os.close(handle)
extract(video_file, video_audio_file)
video, _ = librosa.load(video_audio_file, sr=sampling_rate, mono=True, duration=duration_limit)
os.unlink(video_audio_file)

##############---------DISPLAY WARPING PATH---------##############

# Chromagram
audio_chroma = defineChromagram(audio, sampling_rate)

# Chromagram
video_chroma = defineChromagram(video, sampling_rate)

# Performs RQA
xsim = librosa.segment.cross_similarity(audio_chroma, video_chroma, mode='affinity')
L_score, L_path = librosa.sequence.rqa(xsim, np.inf, np.inf, backtrack=True)

audio_times = []
video_times = []
diff_times = []
for v, a in L_path * hop_size / sampling_rate:
    A = float(a)
    V = float(v)
    audio_times.append(A)
    video_times.append(V)
    diff_times.append((A - V))

##############---------SYNC PROCESS---------##############

# Find mean of time differences
diff_times = np.array(diff_times)
mean = np.average(diff_times)
std = np.std(diff_times)
diff_times = [d for d in diff_times if np.abs(d-mean) < (0.5*std)]
diff = np.average(diff_times)

# Setting move option
move = True if (diff > 0) else False

# Sync using PyDub
audio = AudioSegment.from_wav(audio_file)

if move:
    # Trim diff seconds from beginning
    final = audio[diff * 1000:]
else:
    # Add diff seconds of silence to beginning
    silence = AudioSegment.silent(duration=-diff * 1000)
    final = silence + audio

# Export synced audio
handle, synced_audio = tempfile.mkstemp(suffix='.wav')
os.close(handle)
final.export(synced_audio, format='wav')

##############---------COMBINE PROCESS---------##############
save_file = args.output
combine(synced_audio, video_file, save_file)
os.unlink(synced_audio)
print('Synced and combined successfully to {}'.format(save_file))
