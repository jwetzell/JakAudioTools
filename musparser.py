#UNFINISHED
# A LOT of data format info taken from https://forum.xentax.com/viewtopic.php?t=12966

import os
import argparse
import struct

#yes two midi libraries...
import music21
import mido

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

parser = argparse.ArgumentParser(description="Process JAK SBK files")


parser.add_argument("-i", dest="filepath", required=True, 
                    help="Input path to JAK SBK file", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

args = parser.parse_args()

filename = os.path.basename(args.filepath)

name_length = 20
sounds_start = 24
sounds_length = 20

with open(args.filepath, "rb") as f:

    '''
        struct MUS { // 2 * 16
            uint32_t version; // 1 version?
            uint32_t subversion; // 3 subversion?
            uint32_t minorversion; // 32 minor version?
            uint32_t oSomething; // points to start of soundbank data, -32? or is it SBv2 struct data size?
            uint32_t oBank; // this points to the start of the soundbank sample data
            uint32_t sBank; // size of sound bank
            uint32_t oMID; // pointer to sequenced music data
            uint32_t s3;
        }

        E.g.: Version 1.3.32, oSomething 704, Bank offset 736 B, Bank Size 534256 B, MID offset 534992, ? 22772
    '''
    MUSinfo = struct.unpack("IIIIIIII",f.read(32))
    soundbankStart = MUSinfo[4]
    print(f"SoundBank Start: {soundbankStart}")
    sequenceStart = MUSinfo[6]
    print(f"Sequence Start: {sequenceStart}")


    sbv2Start = f.tell()

    '''
        struct SBv2 { // 5x16 B
            char signature[4]; // "SBv2"
            uint32_t version;
            uint32_t hversion;
            char name[4]; //eg "V1RA" or "BOSS"
            uint32_t a; // 0xa
            uint16_t b; //1
            uint16_t nMap;
            uint16_t nSMap;
            uint16_t nSample; // same as nMap? no it can be different...
            uint32_t f; //0x34 another offset, to end of extname from start of SBv2?
            uint32_t oInstrument; // from start of SBv2
            uint32_t oRegions; // from start of SBv2
            uint32_t i; //0x5040
            uint32_t sizeofsamples; // same as in file header
            uint32_t k; //0
            uint32_t l; //4 or 5?
            char extname[12]; // e.g. "V1RAV1RAV1RA"
            uint16_t m;
            uint16_t n;
            uint16_t o;
            uint16_t p;
            uint32_t q;
        }
    '''
    sbv2 = struct.unpack("4sII4sIHHHHIIIIIII12sHHHHI",f.read(80))
    
    instrumentStart = sbv2[10] + sbv2Start
    regionStart = sbv2[11] + sbv2Start
    
    print(MUSinfo)
    print(sbv2)
    f.seek(instrumentStart)
    instruments = []
    while(f.tell() < regionStart):
        '''
            struct Instrument {
                uint8_t nRegion; // usually 1
                uint8_t volume; // ? maybe... like 7f is 1.0?
                uint16_t something; // always 0
                uint32_t oRegion; // relative to start of SBv2 block I think, points to the first region for instrument
            }
        '''
        instrument = struct.unpack("BBHI",f.read(8))
        instruments.append(instrument)

    print("INSTRUMENTS")
    for instrument in instruments:
        print(instrument)

    '''
        struct Region { // 0x18 B
            uint8_t type; //? always 0
            uint8_t marker1; // usually 7f, not always, maybe another volume?
            uint8_t a; // not same for same sample data
            uint8_t b; // not same for same sample data
            int16_t c; // signed in range +/- 64? Tuning? intruments with 2 regions seem to have these in a plus minus couple, maybe panorama?
            uint32_t keymap; //? LSB is only set for programs with multiple entries?
            uint16_t marker2; // 0x80ff, bt sometimes LSB is dX
            uint8_t type2; // in range c9 - d1? can be different for same sample data
            uint8_t marker3; // always 9f, or 0x80 | 0x1f?
            uint16_t version; //? 1 or 0, maybe looped flag? not same sample data
            uint32_t oSample; // offset to sample from start of sample bank
            uint32_t sampleID; // I think it's the index in the sample bank...
        }

    '''
    regions = []
    while(f.tell()<soundbankStart):
        region = struct.unpack("=BBBBhIHBBHII", f.read(24))
        regions.append(region)
    print("REGIONS")
    sampleOffsets = []
    for region in regions:
        print(region)
        sampleIndex = region[11]
        sampleOffset = soundbankStart + region[10]
        if sampleOffset not in sampleOffsets:
            sampleOffsets.append(sampleOffset)
        #print(f"Region Sample Audio  offset: {soundbankStart + region[10]}")
    # this should align the index of the sample offset with it's sample ID
    sampleOffsets.sort()
    # the sample data lies between here and the next processed section 22050 Hz sample rate mono adpcm

    '''
        struct seq {
            u32 version; // 2
            u32 subversion; // 1
            u32 number; // 16
            u32 size; // Size of sequence data following this struct
        }

    '''
    f.seek(sequenceStart)

    seq = struct.unpack("4I",f.read(16))
    
    
    midBlockType = f.read(4)
    f.seek(-4,1)
    mmidBlockStart = f.tell()

    midBlockOffsets = []
    midBlocks = []
    midBlockDataOffsets = []

    if(midBlockType == str.encode("MID ")):
        '''
            struct MID {
                char signature[4]; // "MID "
                u16 a;
                u16 b;
                u32 c;
                u32 d;
                char name[4]; // e.g. "V1RA"
                u32 e;
                u32 f; // offset from start of struct to midi data
                u32 g;
                u32 tempo; // microseconds per quarter note?
                u32 division; // or not...
                u16 unknown;
                u8 iTrack; // track index 0 - 2
                u8 nTrack; // number of tracks (3)
            }
        '''
        midBlock = struct.unpack("4sHHII4sIIIIIHBB", f.read(44))
        midBlocks.append(midBlock)
        midBlockDataOffsets.append(int(midBlock[7] + mmidBlockStart))
        midBlockOffsets.append(mmidBlockStart)
        print(midBlock)
    elif midBlockType == str.encode("MMID"):
        '''
            struct MMID {
                char signature[4]; // "MMID"
                u16 type; //?
                u8 a; //?
                u8 nTrack; // maybe... it's always 3 lol
                char name[4]; // e.g. "V1RA"
                u32 blank; //?
            }
        '''
        
        mmidBlock = struct.unpack("4sHBB4sI", f.read(16))
        print("MMIDBLOCK")
        print(mmidBlock)
        for i in range(mmidBlock[3]):
            blockOffset = struct.unpack("I",f.read(4))[0] + mmidBlockStart
            midBlockOffsets.append(blockOffset)

        for offset in midBlockOffsets:
            f.seek(offset)
            '''
                struct MID {
                    char signature[4]; // "MID "
                    u16 a;
                    u16 b;
                    u32 c;
                    u32 d;
                    char name[4]; // e.g. "V1RA"
                    u32 e;
                    u32 oMIDI; // offset from start of struct to midi data
                    u32 g;
                    u32 tempo; // microseconds per quarter note?
                    u32 division; // or not...
                    u16 unknown;
                    u8 iTrack; // track index 0 - 2
                    u8 nTrack; // number of tracks (3)
                }
            '''
            midBlock = struct.unpack("4sHHII4sIIIIIHBB", f.read(44))
            midBlocks.append(midBlock)
        for i in range(len(midBlockOffsets)):
            midBlockDataOffsets.append(int(midBlocks[i][7] + midBlockOffsets[i]))

    print("MIDBLOCKS")
    for block in midBlocks:
        print(block)

    midBlockData = []
    for offset in midBlockDataOffsets:
        f.seek(offset)
        midiData = music21.midi.MidiTrack.headerId #add midi track so music21 doesn't complain
        while int(f.tell()) not in midBlockOffsets:
            character = f.read(1)
            if not character:
                break
            midiData += character
        midBlockData.append(midiData)
    

    #I would stop reading now it doesn't get any better.....

    #The use of two midi libraries is ugly...but it works
    # the parser in music21 is able to pickup miditrack time delay events but doesn't output this all correctly to MIDI file
    # mido doesn't get this time delay events but DOES output to midi correctly if a time is added to messages appropriately

    # easily fixed if I just grow up and parse the MIDI myself...

    eventsToOutput = [  music21.midi.ChannelVoiceMessages.NOTE_ON,
                        music21.midi.ChannelVoiceMessages.CHANNEL_KEY_PRESSURE]

    mid = mido.MidiFile()
    
    trackEvents = []
    for block in midBlocks: 
        mt = music21.midi.MidiTrack(block[12])
        midiData = midBlockData[block[12]]
        mt.read(midiData)
        cleanTrack = music21.midi.MidiTrack(block[12])

        for event in mt.events:
            if(event.type in eventsToOutput or event.isDeltaTime()):
                cleanTrack.events.append(event)
                trackEvents.append(event)

        track = mido.MidiTrack()
        mid.tracks.append(track)

        track.append(mido.MetaMessage('set_tempo',tempo=block[9]))

        delayTime = 0
        for event in trackEvents:
            if event.isDeltaTime():
                delayTime += event.time
            elif event.type == music21.midi.ChannelVoiceMessages.NOTE_ON:
                if event.velocity > 127:
                    event.velocity = 127
                messageToAdd = mido.Message('note_on',channel=event.channel-1, note=event.pitch, velocity=event.velocity)
                if(delayTime > 0):
                    messageToAdd.time = delayTime
                    delayTime = 0
                track.append(messageToAdd)
            elif event.type == music21.midi.ChannelVoiceMessages.CHANNEL_KEY_PRESSURE:
                messageToAdd = mido.Message('note_off',channel=event.channel-1, note=event.data, velocity=0)
                if(delayTime > 0):
                    messageToAdd.time = delayTime
                    delayTime = 0
                track.append(messageToAdd)
            elif event.type == music21.midi.ChannelVoiceMessages.PROGRAM_CHANGE:
                messageToAdd = mido.Message('program_change',channel=event.channel-1, program=event.data)
                if(delayTime > 0):
                    messageToAdd.time = delayTime
                    delayTime = 0
                track.append(messageToAdd)
    
    mid.save(f"{sbv2[3].decode('utf-8')}.mid")
