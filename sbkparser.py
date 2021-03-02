#UNFINISHED
import os
import argparse
import struct
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
    sbkInfo = struct.unpack("20sI",f.read(24))
    print(sbkInfo)
    soundDatas = []
    for i in range(sbkInfo[1]):
        soundData = struct.unpack("16sHH",f.read(20))
        print(soundData)
    f.seek(2048)

    '''
        seq
        I version
        I subversion
        I minorversion
        I something?
        I soundbankStart
        I soundBankSize
    '''

    seqStart = f.tell()
    seq = struct.unpack("6I",f.read(24))
    print(seq)

    soundbankStart = seq[4] + seqStart
    print(f"SoundBank Offset: {soundbankStart}")

    '''
        sb1k

        4s signature 'SB1k'
        I
        I
        4s
        I
        H
        H
        H
        H
        I instrumentOffset from beingging of this struct
        I regionOffset from beginning of this struct
        I
        I
        I
        I
        I
        12s
        H
        H
        H
        H
        I
    '''
    

    soundBankHeaderStart = f.tell()
    sb1k = struct.unpack("4sII4sIHHHHIIIIIII12sHHHHI",f.read(80))

    instrumentStart = sb1k[8] + soundBankHeaderStart
    print(instrumentStart)
    f.seek(instrumentStart)
    regionStart = sb1k[10] + soundBankHeaderStart
    print(sb1k)

    instruments = []
    while(f.tell() < regionStart):
        '''
            struct Instrument {
                uint8_t nRegion; // usually 1
                uint8_t volume; // ? maybe... like 7f is 1.0?
                uint16_t something; // always 0
                uint32_t oRegion; // relative to start of SBv2 block I think, points to the first region for instrument
            } __attribute__((packed));
        '''
        instrument = struct.unpack("BBBBHI",f.read(12))
        instruments.append(instrument)

    print("INSTRUMENTS")
    offsets = []
    for instrument in instruments:
        if instrument[-1] not in offsets:
            offsets.append(instrument[-1])
        print(instrument)
    print(len(offsets))

    f.seek(regionStart)

    regions = []
    while(f.tell()<soundbankStart):
        #format defintely not right but 
        region = struct.unpack("10I", f.read(40))
        regions.append(region)
    print("REGIONS")
    sampleOffsets = []
    for region in regions:
        print(region)
        sampleOffset = soundbankStart + region[-4]
        if sampleOffset not in sampleOffsets:
            sampleOffsets.append(sampleOffset)
        #print(f"Region Sample Audio  offset: {soundbankStart + region[10]}")
    # this should align the index of the sample offset with it's sample ID
    sampleOffsets.sort()

    count = 0
    for offset in sampleOffsets:
        f.seek(offset)
        soundData = f.read(1)
        while(f.tell() not in sampleOffsets):
            character = f.read(1)
            if not character:
                break
            soundData += character

        #VAGp header data length and sample rate are packed in bytes 11-15 and 16-20 respectively
        header = b'\x56\x41\x47\x70\x00\x00\x00\x20\x00\x00\x00\x00'
        header += struct.pack(">II", len(soundData), 22050)
        header += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x61\x73\x73\x69\x73\x74\x61\x6E\x74\x2D\x76\x69\x6C\x6C\x61\x67\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        
        with open(f'./OUT/VAGp/{count}.VAGp','wb') as out:
            out.write(header)
            out.write(soundData)
            out.close()
        count += 1
        

