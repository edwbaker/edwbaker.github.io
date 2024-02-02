# Linux audio recipes

## Tools

### sox: Sound Exchange

### ffmpeg

## Mix stero to mono

````bash
ffmpeg -i stero.wav -ac 1 mono.wav
````

## Change sample rate of wav file

````bash
ffmpeg -i high.wav -ar 44100 low.wav
````

## Change bit depth of wav file

````bash
ffmpeg -i high.wav -c:a pcm_s16le low.wav
````

## Converting an entire folder

Source files in `raw`, output files in `wav`, convert to 16 bit 44.1kHz Wave file.

````bash
for f in raw/*;
do
	ffmpeg -i "${f}" -vn -c:a pcm_s16le -ar 44100 "wav/${f#raw/}.wav";
done
```

## Concatenating files

### Concatenating large numbers of files

This uses sox to concatenate any matching wave files in a directory.

*Note that the wav file format is limited to 4GB due to a 32-bit header.*

````bash
if test -f temp.wav; then
  rm temp.wav
fi

if test -f out.wav; then
  rm out.wav
fi
                                                                                                                         
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
