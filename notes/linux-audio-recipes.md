# Linux audio recipes

## Tools

### sox: Sound Exchange

### ffmpeg

## Concatenating files

### Concatenating large numbers of files
This uses sox to concatenate any matching wave files in a directory.

*Note that the wav file format is limited to 4GB due to a 32-bit header.*
````
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
