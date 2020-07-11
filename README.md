# audiosync-cmd

#### This tool automatically syncs matching video and audio files using recurrence quantification analysis (RQA). The tool allows you to adjust the sampling rate, hop length, and ftt window size so you can achieve near-perfect synchronization.

#### At the start of this project, I used dynamic time warping (DTW) instead of recurrence quantification analysis (RQA) to synchronize the two audio tracks. This method seemed efficient for my purposes, but didn't achieve near-perfect synchronization on some tests. This led me to implement RQA, which maximizes alignment paths and relies on similarity rather than distance.

#### More information on RQA can be discovered [here](https://en.wikipedia.org/wiki/Recurrence_quantification_analysis) on Wikipedia, and a similar project has been documented on this [pdf](http://www.mtg.upf.edu/system/files/publications/Roma-Waspaa-2014.pdf)

## setup
#### Python 2
`pip install -r requirements.txt`
#### Python 3
`pip3 install -r requirements.txt`

## usage

#### use the help command
`python audiosync.py --help`

#### arguments

##### required
`-v, --video | path to video file`

`-a, --audio | path to audio file`

`-o, --output | path to output file`

##### optional

`-f, --fft | fft window size | recommended to be a power of 2 | default: 1024`

`-hl, --hoplength | hop length | the number of samples between successive frames | default: 512`

`-sr, --samplingrate | sampling rate in Hz | Most applications use 44.1kHz | default: 44100Hz`

`-d, --duration | duration to process | default: 120 seconds`
