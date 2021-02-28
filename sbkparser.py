import os
import argparse

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
    soundbank_name = f.read(20).decode('utf-8').strip()
    f.seek(24)
    soundsFound = 0
    while 1:
        empty = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        sounds_chunk = f.read(sounds_length)
        if sounds_chunk == empty:
            break
        else:
            sound_name = sounds_chunk[:-4].decode('utf-8').strip()
            sound_data = sounds_chunk[-4:]
            soundsFound += 1
            print(f'Found {sound_name} with some data {sound_data[0:2].hex()} {sound_data[2:].hex()}')
        




        

        
        

