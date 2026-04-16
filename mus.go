package jakaudiotools

import (
	"fmt"
)

type MUSFile struct {
	Version           uint32
	SubVersion        uint32
	MinorVersion      uint32
	a                 uint32
	SoundBankStart    uint32
	SoundBankSize     uint32
	SequenceDataStart uint32
	b                 uint32
}

func readUint32(data []byte, offset int) uint32 {
	return uint32(data[offset]) | uint32(data[offset+1])<<8 | uint32(data[offset+2])<<16 | uint32(data[offset+3])<<24
}

// MUS = namedtuple('MUS','version subversion minorversion something soundBankStart soundBankSize sequenceDataStart s3')
// MUSStructString= "8I"
func (mfe *MUSFile) Unmarshal(data []byte) error {
	if len(data) < 32 {
		return fmt.Errorf("data too short to unmarshal MUSFileEntry")
	}
	mfe.Version = readUint32(data, 0)
	mfe.SubVersion = readUint32(data, 4)
	mfe.MinorVersion = readUint32(data, 8)
	mfe.a = readUint32(data, 12)
	mfe.SoundBankStart = readUint32(data, 16)
	mfe.SoundBankSize = readUint32(data, 20)
	mfe.SequenceDataStart = readUint32(data, 24)
	mfe.b = readUint32(data, 28)
	return nil
}

type SBV2 struct {
	Signature        string
	Version          uint32
	HVersion         uint32
	Name             string
	a                uint32
	b                uint16
	InstrumentCount  uint16
	RegionCount      uint16
	NumSample        uint16
	f                uint32
	InstrumentOffset uint32
	RegionOffset     uint32
	i                uint32
	SoundBankSize    uint32
	k                uint32
	l                uint32
	ExtName          string
	m                uint16
	n                uint16
	o                uint16
	p                uint16
	q                uint32
}

// #struct type               4s        I       I        4s   I H H    H     H       I I                I            I I             I I 12s     H H H H I
// SBV2 = namedtuple('SBV2', 'signature version hversion name a b nMap nSMap nSample f instrumentOffset regionOffset i soundBankSize k l extname m n o p q')
// SBV2StructString = "4s2I4sI4H7I12s4HI"
func (sbv2 *SBV2) Unmarshal(data []byte) error {
	if len(data) < 158 {
		return fmt.Errorf("data too short to unmarshal SBV2")
	}
	sbv2.Signature = string(data[0:4])
	sbv2.Version = readUint32(data, 4)
	sbv2.HVersion = readUint32(data, 8)
	sbv2.Name = string(data[12:16])
	sbv2.a = readUint32(data, 16)
	sbv2.b = uint16(data[20]) | uint16(data[21])<<8
	sbv2.InstrumentCount = uint16(data[22]) | uint16(data[23])<<8
	sbv2.RegionCount = uint16(data[24]) | uint16(data[25])<<8
	sbv2.NumSample = uint16(data[26]) | uint16(data[27])<<8
	sbv2.f = readUint32(data, 28)
	sbv2.InstrumentOffset = readUint32(data, 32)
	sbv2.RegionOffset = readUint32(data, 36)
	sbv2.i = readUint32(data, 40)
	sbv2.SoundBankSize = readUint32(data, 44)
	sbv2.k = readUint32(data, 48)
	sbv2.l = readUint32(data, 52)
	sbv2.ExtName = string(data[56:68])
	sbv2.m = uint16(data[68]) | uint16(data[69])<<8
	sbv2.n = uint16(data[70]) | uint16(data[71])<<8
	sbv2.o = uint16(data[72]) | uint16(data[73])<<8
	sbv2.p = uint16(data[74]) | uint16(data[75])<<8
	sbv2.q = readUint32(data, 76)
	return nil
}

type Instrument struct {
	RegionCount  uint8
	Volume       uint8
	zero         uint16
	RegionOffset uint32
}

// #struct type                          B           B      H    I
// Instrument = namedtuple('Instrument','regionCount volume zero regionOffset')
func (inst *Instrument) Unmarshal(data []byte) error {
	if len(data) < 8 {
		return fmt.Errorf("data too short to unmarshal Instrument")
	}
	inst.RegionCount = data[0]
	inst.Volume = data[1]
	inst.zero = uint16(data[2]) | uint16(data[3])<<8
	inst.RegionOffset = readUint32(data, 4)
	return nil
}

// #struct type                  B    B       B B h   B B       H    B B B B H        I            I
// Region = namedtuple('Region','type volume1 a b pan c volume2 zero d e f g loopFlag sampleOffset sampleId')
// RegionStructString = "=BBBBhBBHBBBBHII"
type Region struct {
	Type         uint8
	Volume1      uint8
	a            uint8
	b            uint8
	Pan          int16
	c            uint8
	Volume2      uint8
	zero         uint16
	d            uint8
	e            uint8
	f            uint8
	g            uint8
	LoopFlag     uint16
	SampleOffset uint32
	SampleId     uint32
}

func (r *Region) Unmarshal(data []byte) error {
	if len(data) < 24 {
		return fmt.Errorf("data too short to unmarshal Region")
	}
	r.Type = data[0]
	r.Volume1 = data[1]
	r.a = data[2]
	r.b = data[3]
	r.Pan = int16(data[4]) | int16(data[5])<<8
	r.c = data[6]
	r.Volume2 = data[7]
	r.zero = uint16(data[8]) | uint16(data[9])<<8
	r.d = data[10]
	r.e = data[11]
	r.f = data[12]
	r.g = data[13]
	r.LoopFlag = uint16(data[14]) | uint16(data[15])<<8
	r.SampleOffset = readUint32(data, 16)
	r.SampleId = readUint32(data, 20)
	return nil
}

// #struct type            I       I          I            I
// SEQ = namedtuple('SEQ','version subversion minorversion sequenceDataSize')
// SEQStructString = "4I"

// #struct type            4s        H H I I 4s   I I              I I         I        H    B          B
// MID = namedtuple('MID','signature a b c d name e midiDataOffset g midiTempo division zero trackIndex trackCount')
// MIDStructString = "4s2H2I4s5IH2B"

// #struct type              4s        H    B B          4s   I
// MMID = namedtuple('MMID','signature type a trackCount name zero')
// MMIDStructString = "4sH2B4sI"

func ParseMUS(data []byte) (*MUSFile, error) {

	// nameLength := 20
	// soundsStart := 24
	// soundsLength := 20

	offset := 0
	musFile := &MUSFile{}
	err := musFile.Unmarshal(data)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal MUS file: %w", err)
	}
	offset += 32
	sbv2Start := offset
	sbv2Info := &SBV2{}
	err = sbv2Info.Unmarshal(data[offset:])
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal MUS file: %w", err)
	}

	fmt.Printf("SBV2 info: %+v\n", sbv2Info)

	instruments := []Instrument{}
	offset = sbv2Start + int(sbv2Info.InstrumentOffset)
	for i := 0; i < int(sbv2Info.InstrumentCount); i++ {
		instrument := &Instrument{}
		err := instrument.Unmarshal(data[offset:])
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal instrument at offset %d: %w", offset, err)
		}
		fmt.Printf("instrument %d: %+v\n", i, instrument)
		instruments = append(instruments, *instrument)
		offset += 8
	}
	fmt.Printf("found %d instruments\n", len(instruments))

	regions := []Region{}

	offset = sbv2Start + int(sbv2Info.RegionOffset)
	for i := 0; i < int(sbv2Info.RegionCount); i++ {
		region := &Region{}
		err := region.Unmarshal(data[offset:])
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal region at offset %d: %w", offset, err)
		}
		fmt.Printf("region %d: %+v\n", i, region)
		regions = append(regions, *region)
		offset += 24
	}

	// TODO(jwetzell): parse samples in regions

	sequenceOffset := int(musFile.SequenceDataStart)

	sequence := &Sequence{}
	err = sequence.Unmarshal(data[sequenceOffset:])
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal sequence at offset %d: %w", sequenceOffset, err)
	}
	fmt.Printf("sequence: %+v\n", sequence)

	offset = sequenceOffset + 16

	midBlockType := string(data[offset : offset+4])
	fmt.Printf("mid block type: %s\n", midBlockType)

	if midBlockType == "MID " {
		midBlock := &MID{}
		err = midBlock.Unmarshal(data[offset:])
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal MID block at offset %d: %w", offset, err)
		}
		fmt.Printf("MID block: %+v\n", midBlock)
		// midBlocks = append(midBlocks, *midBlock)
	} else if midBlockType == "MMID" {
		mmidBlockStart := offset
		mmidBlock := &MMID{
			MIDBlocks: []MID{},
		}
		err = mmidBlock.Unmarshal(data[offset:])
		if err != nil {
			return nil, fmt.Errorf("failed to unmarshal MMID block at offset %d: %w", offset, err)
		}
		fmt.Printf("MMID block: %+v\n", mmidBlock)

		offset += 16

		for i := 0; i < int(mmidBlock.TrackCount); i++ {
			blockOffset := int(readUint32(data[offset:], 0)) + mmidBlockStart
			fmt.Printf("Found MID block at offset %d\n", blockOffset)

			midBlock := &MID{
				BlockOffset: blockOffset,
			}
			err = midBlock.Unmarshal(data[blockOffset:])
			if err != nil {
				return nil, fmt.Errorf("failed to unmarshal MID block at offset %d: %w", blockOffset, err)
			}
			mmidBlock.MIDBlocks = append(mmidBlock.MIDBlocks, *midBlock)
			offset += 4
		}
		for i, midBlock := range mmidBlock.MIDBlocks {
			blockOffset := midBlock.BlockOffset
			if i != len(mmidBlock.MIDBlocks)-1 {
				nextBlockOffset := mmidBlock.MIDBlocks[i+1].BlockOffset
				midBlock.MidiData = data[blockOffset+int(midBlock.MidiDataOffset) : nextBlockOffset]
			} else {
				midBlock.MidiData = data[blockOffset+int(midBlock.MidiDataOffset):]
			}
		}
	} else {
		return nil, fmt.Errorf("unknown mid block type: %s", midBlockType)
	}

	return musFile, nil
}

// #struct type            I       I          I            I
// SEQ = namedtuple('SEQ','version subversion minorversion sequenceDataSize')
// SEQStructString = "4I"
type Sequence struct {
	Version          uint32
	SubVersion       uint32
	MinorVersion     uint32
	SequenceDataSize uint32
}

func (s *Sequence) Unmarshal(data []byte) error {
	if len(data) < 16 {
		return fmt.Errorf("data too short to unmarshal Sequence")
	}
	s.Version = readUint32(data, 0)
	s.SubVersion = readUint32(data, 4)
	s.MinorVersion = readUint32(data, 8)
	s.SequenceDataSize = readUint32(data, 12)
	return nil
}

// #struct type            4s        H H I I 4s   I I              I I         I        H    B          B
// MID = namedtuple('MID','signature a b c d name e midiDataOffset g midiTempo division zero trackIndex trackCount')
// MIDStructString = "4s2H2I4s5IH2B"
type MID struct {
	Signature      string
	a              uint16
	b              uint16
	c              uint32
	d              uint32
	Name           string
	e              uint32
	MidiDataOffset uint32
	g              uint32
	MidiTempo      uint32
	Division       uint32
	zero           uint16
	TrackIndex     uint8
	TrackCount     uint8

	BlockOffset int
	MidiData    []byte
}

func (m *MID) Unmarshal(data []byte) error {
	if len(data) < 44 {
		return fmt.Errorf("data too short to unmarshal MID")
	}
	m.Signature = string(data[0:4])
	m.a = uint16(data[4]) | uint16(data[5])<<8
	m.b = uint16(data[6]) | uint16(data[7])<<8
	m.c = readUint32(data, 8)
	m.d = readUint32(data, 12)
	m.Name = string(data[16:20])
	m.e = readUint32(data, 20)
	m.MidiDataOffset = readUint32(data, 24)
	m.g = readUint32(data, 28)
	m.MidiTempo = readUint32(data, 32)
	m.Division = readUint32(data, 36)
	m.zero = uint16(data[40]) | uint16(data[41])<<8
	m.TrackIndex = data[42]
	m.TrackCount = data[43]
	return nil
}

// #struct type              4s        H    B B          4s   I
// MMID = namedtuple('MMID','signature type a trackCount name zero')
// MMIDStructString = "4sH2B4sI"
type MMID struct {
	Signature  string
	Type       uint16
	a          uint8
	TrackCount uint8
	Name       string
	zero       uint32
	MIDBlocks  []MID
}

func (mmid *MMID) Unmarshal(data []byte) error {
	if len(data) < 16 {
		return fmt.Errorf("data too short to unmarshal MMID")
	}
	mmid.Signature = string(data[0:4])
	mmid.Type = uint16(data[4]) | uint16(data[5])<<8
	mmid.a = data[6]
	mmid.TrackCount = data[7]
	mmid.Name = string(data[8:12])
	mmid.zero = readUint32(data, 12)
	return nil
}
