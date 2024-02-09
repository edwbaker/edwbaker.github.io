# Linux audio recipes

Most of these should work on other Unix-like systems such as macOS.

Unless you are unusually curious, the best way to use this guide is by seaching (`Ctrl+F`) in your web browser for what you are trying to achieve.

## Tools

The two most common command line tools are Sound eXchange (sox) and FFmpeg, which share a great deal of basic functionality. These are widely availabe on Unix-like operating systems (and even Windows).

### Getting help

Both sox and ffmpeg come with extensive documentation.

````bash
man sox

man ffmpeg
````

### sox: Sound eXchange

#### sox Installation

##### sox installation on Ubunu and other Debian derivatives

````bash
sudo apt install sox
````

##### sox installation on macOS

First [install homebrew](https://docs.brew.sh/Installation).

````bash
brew install sox
````

### ffmpeg

#### ffmpeg installation

##### ffmpeg installation on Ubunu and other Debian derivatives

````bash
sudo apt install ffmpeg
````

##### ffmpeg installation on macOS

First [install homebrew](https://docs.brew.sh/Installation).

````bash
brew install ffmpeg
````

## Getting audio file information

````bash
sox file.mp3 -n stat
````

## Manipulating channels

### Mix stero to mono

````bash
ffmpeg -i stero.wav -ac 1 mono.wav
````

### Split stereo to seprate mono

````bash
sox in_file.wav out_left.wav remix 1
sox in_file.wav out_right.wav remix 2
````

## Manipulating sample rate

### Change sample rate of wav file

````bash
ffmpeg -i high.wav -ar 44100 low.wav
````

````bash
sox high.wav -r 44100 low.wav
sox high.wav low.wav rate 44100

sox high.wav -r 48k low.wav
sox high.wav low.wav rate 48k
````

## Manipulating bit depth

### Change bit depth of wav file

````bash
ffmpeg -i high.wav -c:a pcm_s16le low.wav
````

### Change bit depth of an entire folder

Source files in `raw`, output files in `wav`, convert to 16 bit 44.1kHz Wave file.

````bash
for f in raw/*;
do
  ffmpeg -i "${f}" -vn -c:a pcm_s16le -ar 44100 "wav/${f#raw/}.wav";
done
````

## Manipulating file types

### Convert file type

````bash
ffmpeg in_file.wav out_file.mp3
````

````bash
sox in_file.wav out_file.mp3
````

## Normalisation

### Normalisation of amplitude to -0.1dB

````bash
sox in_file out_file norm -0.1
````

## Mapiluting amplitude/volume

### Increase volume

````bash
sox -v 2.0 quiet.wav loud.wav
````

### Decrease volume

````bash
sox -v 0.5 loud.wav quiet.wav
````

## Getting sections of a file

### Splitting a file

Split a file into n second chunks

````bash
sox in_file out_file trim 0 n : newfile : restart
````

### Get first n seconds of a file

````bash
sox in_file out_file trim 0 n
````

### Trim n seconds from end of file

````bash
sox in_file out_file trim 0 -n
````

## Concatenating files

### Concatenating large numbers of files

This uses sox to concatenate any matching wave files in a directory.

*Note that the wav file format is limited to 4GB due to a 32-bit header.*

````bash
# Delete temp.wav if it exists
if test -f temp.wav; then
  rm temp.wav
fi

# Delete out.wav if it exists
if test -f out.wav; then
  rm out.wav
fi

# List Wave files and sort by name                                                                                     
ls *.wav | sort -n | while read l;
do     
   echo "$l"                                                                                                                                                          
   if [ ! -f temp.wav ]                                                                                                                                         
   then                                                                                                                                                       
      cp $l temp.wav                                                                                                                                            
   else                                                                                                                                                       
      sox temp.wav $l out.wav
      rm temp.wav                                                                                                                                
      cp out.wav temp.wav                                                                                                                                       
   fi
done
````

## Manipulating playback speed

### Increase/decrease playback speed by factor of n

````bash
#n can be a decimal value
sox in.wav out.wav speed n
````
