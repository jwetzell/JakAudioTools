#UNFINISHED
import os
import argparse
import struct
from collections import namedtuple

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

#struct type            20s  I
SBK = namedtuple('SBK','name soundCount')
SBKStructString = "20sI"

#struct type                16s  I               I
Sound = namedtuple('Sound','name soundDataOffset soundDataSize')
SoundStructString = "16sHH"

#struct type            I       I          I            I         I               I
SEQ = namedtuple('SEQ','version subversion minorversion something soundBankOffset soundBankSize')
SEQStructString = "6I"

#struct type               4s       I       I          I            I    H H H H                I                I            I I I
SB1K = namedtuple('SB1K','signature version subversion minorversion zero e f g h instrumentOffset regionOffset k l m')
SB1kStructString = "4sIIIIHHHHIIIII"

#struct type                          I      h h h            h
Instrument = namedtuple('Instrument','volume a b regionOffset d')
InstrumentStructString = 'IHHHH'

Region = namedtuple('Region','version subversion a volume b c d e1 e2 f1 f2 g1 sampleId zeros1 zeros2 zero3')
RegionStructString = 'IIBBBBIHHHHHHIII'

with open(args.filepath, "rb") as f:
    sbkInstance = SBK._make(struct.unpack(SBKStructString,f.read(24)))
    print(sbkInstance)
    soundDatas = []

    for i in range(sbkInstance.soundCount):
        soundData = Sound._make(struct.unpack(SoundStructString,f.read(20)))
        print(soundData)
    
    # a ton of zeros
    while(struct.unpack("B",f.read(1))[0] == 0):
        continue
    # found something rewind a byte
    f.seek(-1,1)

    seqStart = f.tell()
    seqInstance = SEQ._make(struct.unpack(SEQStructString,f.read(24)))
    print(seqInstance)

    soundbankStart = seqInstance.soundBankOffset + seqStart
    print(f"SoundBank Offset: {soundbankStart}")

    soundBankHeaderStart = f.tell()
    SB1KInstance = SB1K._make(struct.unpack(SB1kStructString,f.read(48)))
    print(SB1KInstance)

    # there is some data here
    instrumentStart = SB1KInstance[8] + soundBankHeaderStart
    regionStart = SB1KInstance[10] + soundBankHeaderStart

    f.seek(instrumentStart)

    instruments = []
    while(f.tell() < regionStart):
        
        instrumentInstance = Instrument._make(struct.unpack(InstrumentStructString,f.read(12)))
        instruments.append(instrumentInstance)

    print("INSTRUMENTS")
    offsets = []
    for inst in instruments:
        if inst.regionOffset not in offsets:
            offsets.append(inst.regionOffset)
        print(inst)
    print(len(instruments))
    f.seek(regionStart)

    regions = []
    while(f.tell()<soundbankStart):
        #format defintely not right but 
        regionInstance = Region._make(struct.unpack(RegionStructString, f.read(40)))
        regions.append(regionInstance)
    print("REGIONS")
    sampleOffsets = []
    for reg in regions:
        print(reg)
        sampleOffset = soundbankStart + reg[-4]
        if sampleOffset not in sampleOffsets:
            sampleOffsets.append(sampleOffset)
        
        #print(f"Region Sample Audio  offset: {soundbankStart + region[10]}")
    # this should align the index of the sample offset with it's sample ID
    # sampleOffsets.sort()

    # count = 0
    # previousOffset = 0
    # for offset in sampleOffsets:
    #     previousOffset = offset
    #     f.seek(offset)
    #     soundData = f.read(1)
    #     count += 1
    #     while(f.tell() not in sampleOffsets):
    #         character = f.read(1)
    #         if not character:
    #             break
    #         soundData += character
    #     #VAGp header data length and sample rate are packed in bytes 11-15 and 16-20 respectively
    #     header = b'\x56\x41\x47\x70\x00\x00\x00\x20\x00\x00\x00\x00'
    #     header += struct.pack(">II", len(soundData), 22050)
    #     header += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x61\x73\x73\x69\x73\x74\x61\x6E\x74\x2D\x76\x69\x6C\x6C\x61\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
    #     with open(f'./OUT/VAGp/{count}.VAGp','wb') as out:
    #         out.write(header)
    #         out.write(soundData)
    #         out.close()
    #     count += 1
        

