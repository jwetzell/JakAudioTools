:: This works if all the files in the VAGp folder are mono compressed ADPCM
mkdir "./OUT/WAV"
for %%f in (./OUT/VAGp/*) do (
  ffmpeg -i "./OUT/VAGp/%%f" "./OUT/WAV/%%~nf.wav"
)