package jakaudiotools

import (
	"bytes"
	"fmt"
)

type VAGEntry struct {
	Name string
	Data []byte
}

func ParseVAG(vagWAD []byte, vagDict []byte, game int8) ([]VAGEntry, error) {
	entries := []VAGEntry{}
	separator := "VAGp"
	dictionaryEntrySize := 12

	if game != 1 {
		separator = "pGAV"
		dictionaryEntrySize = 16
	}

	magic := []byte(separator)
	stereo := []byte("Stereo")
	mono := []byte("Mono")

	stereoInterleaveSize := 8192

	fileStart := 0
	firstTime := true
	previousFileStart := 0
	fileCount := 0
	skipInterleave := false

	vagDictLookup := processVAGDict(vagDict, dictionaryEntrySize)

	for fileStart != -1 {
		previousFileStart = fileStart
		if firstTime {
			location := bytes.Index(vagWAD[fileStart:], magic)
			if location != -1 {
				fileStart += location
			} else {
				fileStart = -1
			}
			firstTime = false
		} else {
			//if last time the start of a stereo file was found we can start looking for the next file starting after the interleave
			if skipInterleave {
				location := bytes.Index(vagWAD[fileStart+len(magic)+stereoInterleaveSize:], magic)
				if location != -1 {
					fileStart += len(magic) + stereoInterleaveSize + location
				} else {
					fileStart = -1
				}
				skipInterleave = false
			} else {
				location := bytes.Index(vagWAD[fileStart+len(magic):], magic)
				if location != -1 {
					fileStart += len(magic) + location
				} else {
					fileStart = -1
				}
			}
		}
		stereoLocation := bytes.Index(vagWAD, stereo)
		monoLocation := bytes.Index(vagWAD, mono)

		audioType := "mono"
		if stereoLocation != -1 && (monoLocation == -1 || stereoLocation < monoLocation) {
			audioType = "stereo"
		}

		if audioType == "stereo" && !skipInterleave {
			skipInterleave = true
		}

		if fileStart >= 0 && fileStart != previousFileStart {
			fileCount += 1
			outname := fmt.Sprintf("%d", fileCount)
			if vagDict != nil && game <= 2 {
				if fileCount-1 >= len(vagDictLookup) {
					return nil, fmt.Errorf("file count exceeds number of entries in VAG dict")
				}
				outname = vagDictLookup[fileCount-1]
			}
			fmt.Printf("%s file named %s found\n", audioType, outname)
			entry := VAGEntry{
				Name: outname,
				Data: vagWAD[previousFileStart:fileStart],
			}
			entries = append(entries, entry)
		}

	}
	return entries, nil
}

func processVAGDict(vagDict []byte, entrySize int) []string {
	names := []string{}
	for i := 0; i < len(vagDict); i += entrySize {
		if i+entrySize > len(vagDict) {
			break
		}
		name := string(vagDict[i+4 : i+entrySize])
		names = append(names, name)
	}
	return names
}
