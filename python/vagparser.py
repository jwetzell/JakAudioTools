import os
import argparse

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def load_name_from_dict(filepath, index, entrySize):
    with open(filepath,'rb') as dictFile:
        dictFile.seek(index*entrySize)
        dictFile.seek(4,1)
        return dictFile.read(8).decode('utf-8')

def check_game(parser,arg):
    valid_games = [1,2,3]
    if int(arg) not in valid_games:
        parser.error(f"Invalid game! Valid game numbers: {valid_games}")
    else:
        return int(arg)

    

parser = argparse.ArgumentParser(description="Process JAK VAGWAD files")


parser.add_argument("-i", dest="filepath", required=True, 
                    help="Input path to JAK VAGWAD file", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

parser.add_argument("-dict", dest="dictpath", required=False, 
                    help="Input path to JAK VAGDIR file to lookup names", metavar="FILE",
                    type=lambda x: is_valid_file(parser, x))

parser.add_argument("-game", dest="game", required=True, default="VAGp",
                    help="Some VAGWAD things are game specific please enter the game 1,2,3 so I can set these up", 
                    type=lambda x: check_game(parser,x))

args = parser.parse_args()

separator = 'VAGp'
dictionaryEntrySize = 12

# file "separator" and dictionary entry size change after Jak 1
if(args.game != 1):
    separator = 'pGAV'
    dictionaryEntrySize = 16

#setup some byte versions of strings for finding
magic = str.encode(separator)
stereo = str.encode('Stereo')
mono = str.encode('Mono')

#is this always 2000 bytes?
stereoInterleaveSize = 8192

with open(args.filepath, "rb") as f:
    #setup directory for file output
    if not os.path.exists("./OUT/VAGp"):
        os.makedirs("./OUT/VAGp")

    contents = f.read()
    fileStart = 0
    firstTime = True
    previousFileStart = 0
    fileCount = 0
    skipInterleave = False

    while fileStart != -1:
        previousFileStart = fileStart
        if firstTime:
            fileStart = contents.find(magic,fileStart)
            firstTime = False
        else:
            #if last time the start of a stereo file was found we can start looking for the next file starting after the interleave
            if skipInterleave:
                fileStart = contents.find(magic,fileStart+len(magic)+stereoInterleaveSize)
                skipInterleave = False
            else:
                fileStart = contents.find(magic,fileStart+len(magic))            
        
        # I don't think there is a "mono" tag to be found but this will default to mono if none of this is found
        stereoLocation = contents.find(stereo)
        monoLocation = contents.find(mono)
        audioType = ('stereo','mono')[monoLocation<stereoLocation or (monoLocation==-1 and stereoLocation ==-1)]
        
        if(audioType== 'stereo' and  not skipInterleave):
            #this is the first start of a stereo file so skip interleave on the next go around
            skipInterleave = True
        
        #FILE FOUND!!
        if(fileStart >= 0 and fileStart != previousFileStart):
            fileCount += 1
            outfilename = str(fileCount)
            # load name from dictionary for Jak 1 and 2, Jak 3 dictionary is obfuscated so skip it for now
            if(args.dictpath and args.game <= 2):
                outfilename = load_name_from_dict(args.dictpath,fileCount -1, dictionaryEntrySize)
                print(f'{audioType} file named {outfilename} found from {previousFileStart} : {fileStart - 1}')
            else:
                print(f'{audioType} file #{fileCount} found from {previousFileStart} : {fileStart - 1}')

            with open(f'./OUT/VAGp/{outfilename.strip()}.VAGp','wb+') as out:
                f.seek(previousFileStart)
                out.write(f.read(fileStart-previousFileStart))
                out.close()

    print(f'Found {fileCount} files')




        

        
        

