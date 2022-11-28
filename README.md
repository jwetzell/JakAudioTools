# JakAudioTools
Tools for parsing and dealing with the various audio files found in Jak and Daxter games


## Types of audio files
* **VAGWAD.XXX** - found in the VAG folder on disc and generally contain speech audio in their respecitive languages i.e VAGWAD.ENG = English Speech Audio
  * VAGWAD.INT typically contains language agnostic audio like background music Jak 1 & 2 do not have a .INT as their music is sequenced using .MUS files
  * the file is just made up of all the audio files sequentially stuffed into one binary Jak 1 uses a file signature of `VAGp` while later games use `pGAV`
  * audio can either be mono or interleaved stereo with an interleave of 2000 bytes
  * Other audio info: Sample rate: 48000, Format: Raw **Compressed** ADPCM
* **VAGDIR.ABY** - this file does not contain any audio data but can be used as a lookup table for the 8 character names of audio files found inside the VAGWAD.XXX files
  * Jak 1 - this file consists of a list of 12 byte entries that match 1-1 with the audio files from the VAGWAD
  * Jak 2 - identical to Jak 1 except entries are 16 bytes long
  * Jak 3 and beyond? - this file is obfuscated so isn't of use yet....
* **XXXXXX.SBK** 
  * SBK files are like soundfonts, they contain short game sound effects as well as the sound name for each of these i.e zoomer-jump
  * I've only tested the sbkparser with Jak 1 SBK files. The format seems to have changed after that, so some work will need to be done to reverse those formats.
* **XXXXXX.MUS** - MUS files contain sequence data (like MIDI) as well as sound bank information, this is the main format of game background music in Jak 1 & 2
  * A very good start for how the data is packed in these can be found [here](https://forum.xentax.com/viewtopic.php?t=12966) but seems like the poster's bitbucket is no longer available :(
  * One big thing I found that wasn't outline was the MID blocks that contain the actual sequence data is actually formatted like [MTrk's](http://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html#BM2_3) and the midi library I originally was using mido just ignored the delay events
  * Currently program change events and sysex messages aren't output to the midi file but can easily be added by modifying the `eventsToOutput` array at the beginning of the MIDI conversion
  * I also haven't done anything with the soundbank data (although the program does parse out the data for these sections) it's fairly easy to get these sounds out separately using something like [PSound](http://snailrush.online.fr/)
 
