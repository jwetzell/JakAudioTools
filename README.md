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
* **XXXXXX.SBK** - SBK files are like soundfonts, they contain short game sound effects as well as the sound name for each of these i.e zoomer-jump
* **XXXXXX.MUS** - MUS files contain sequence data (like MIDI) as well as sound bank information, this is the main format of game background music in Jak 1 & 2
 
