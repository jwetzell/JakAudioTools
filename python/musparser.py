#UNFINISHED
# A LOT of data format info taken from https://forum.xentax.com/viewtopic.php?t=12966

import os
import argparse
import struct

#yes two midi libraries...
import music21
import mido
from collections import namedtuple


#named tuple definitions

#struct type            I       I          I            I         I              I             I                 I
MUS = namedtuple('MUS','version subversion minorversion something soundBankStart soundBankSize sequenceDataStart s3')
MUSStructString= "8I"

#struct type               4s        I       I        4s   I H H    H     H       I I                I            I I             I I 12s     H H H H I
SBV2 = namedtuple('SBV2', 'signature version hversion name a b nMap nSMap nSample f instrumentOffset regionOffset i soundBankSize k l extname m n o p q')
SBV2StructString = "4s2I4sI4H7I12s4HI"

#struct type                          B           B      H    I
Instrument = namedtuple('Instrument','regionCount volume zero regionOffset')
InstrumentStructString = "2BHI"

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
#struct type                  B    B       B B h   B B       H    B B B B H        I            I
Region = namedtuple('Region','type volume1 a b pan c volume2 zero d e f g loopFlag sampleOffset sampleId')
RegionStructString = "=BBBBhBBHBBBBHII"

#struct type            I       I          I            I
SEQ = namedtuple('SEQ','version subversion minorversion sequenceDataSize')
SEQStructString = "4I"

#struct type            4s        H H I I 4s   I I              I I         I        H    B          B
MID = namedtuple('MID','signature a b c d name e midiDataOffset g midiTempo division zero trackIndex trackCount')
MIDStructString = "4s2H2I4s5IH2B"

#struct type              4s        H    B B          4s   I
MMID = namedtuple('MMID','signature type a trackCount name zero')
MMIDStructString = "4sH2B4sI"

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

parser = argparse.ArgumentParser(description="Process JAK MUS files")


parser.add_argument("-i", dest="filepath", required=True, 
                    help="Input path to JAK MUS file", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

args = parser.parse_args()

filename = os.path.basename(args.filepath)

name_length = 20
sounds_start = 24
sounds_length = 20

with open(args.filepath, "rb") as f:

    
    MUSInfo = MUS._make(struct.unpack(MUSStructString,f.read(32)))
    
    print(f"SoundBank Start: {MUSInfo.soundBankStart}")
    print(f"Sequence Start: {MUSInfo.sequenceDataStart}")


    sbv2Start = f.tell()

    sbv2Info = SBV2._make(struct.unpack(SBV2StructString,f.read(80)))
    
    instrumentStart = sbv2Info.instrumentOffset + sbv2Start
    regionStart = sbv2Info.regionOffset + sbv2Start
    
    print(MUSInfo)
    print(sbv2Info)
    f.seek(instrumentStart)
    instruments = []

    
    while(f.tell() < regionStart):
        instrument = Instrument._make(struct.unpack(InstrumentStructString,f.read(8)))
        instruments.append(instrument)

    print("INSTRUMENTS")
    for instrument in instruments:
        print(instrument)

    
    regions = []
    while(f.tell()<MUSInfo.soundBankStart):
        regionInstance = Region._make(struct.unpack(RegionStructString, f.read(24)))
        regions.append(regionInstance)

    print("REGIONS")
    sampleOffsets = []
    for region in regions:
        print(region)
        sampleIndex = region.sampleId
        sampleOffset = MUSInfo.soundBankStart + region.sampleOffset
        if sampleOffset not in sampleOffsets:
            sampleOffsets.append(sampleOffset)
        #print(f"Region Sample Audio  offset: {MUSInfo.soundBankStart + region[10]}")
    # this should align the index of the sample offset with it's sample ID
    sampleOffsets.sort()
    # the sample data lies between here and the next processed section 22050 Hz sample rate mono adpcm

    
    f.seek(MUSInfo.sequenceDataStart)

    seqInstance = SEQ._make(struct.unpack(SEQStructString,f.read(16)))
    
    
    midBlockType = f.read(4)
    f.seek(-4,1)
    mmidBlockStart = f.tell()

    midBlockOffsets = []
    midBlocks = []
    midBlockDataOffsets = []

    if(midBlockType == str.encode("MID ")):
        
        midBlock = MID._make(struct.unpack(MIDStructString, f.read(44)))
        midBlocks.append(midBlock)
        midBlockDataOffsets.append(int(midBlock.midiDataOffset + mmidBlockStart))
        midBlockOffsets.append(mmidBlockStart)
        print(midBlock)
    elif midBlockType == str.encode("MMID"):
        mmidBlock = MMID._make(struct.unpack(MMIDStructString, f.read(16)))
        print("MMIDBLOCK")
        print(mmidBlock)
        for i in range(mmidBlock.trackCount):
            blockOffset = struct.unpack("I",f.read(4))[0] + mmidBlockStart
            midBlockOffsets.append(blockOffset)

        for offset in midBlockOffsets:
            f.seek(offset)
            
            midBlock = MID._make(struct.unpack(MIDStructString, f.read(44)))
            midBlocks.append(midBlock)
        for i in range(len(midBlockOffsets)):
            midBlockDataOffsets.append(int(midBlocks[i].midiDataOffset + midBlockOffsets[i]))

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
        mt = music21.midi.MidiTrack(block.trackIndex)
        midiData = midBlockData[block.trackIndex]
        mt.read(midiData)
        cleanTrack = music21.midi.MidiTrack(block.trackIndex)

        for event in mt.events:
            if(event.type in eventsToOutput or event.isDeltaTime()):
                cleanTrack.events.append(event)
                trackEvents.append(event)

        track = mido.MidiTrack()
        mid.tracks.append(track)

        track.append(mido.MetaMessage('set_tempo',tempo=block.midiTempo))

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
    
    mid.save(f"{sbv2Info.name.decode('utf-8')}.mid")
