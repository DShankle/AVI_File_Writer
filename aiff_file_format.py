import sys, struct

def pLL(x): return struct.pack("<L", x)
def pLS(x): return struct.pack("<H", x)
def pBL(x): return struct.pack(">L", x)
def pBS(x): return struct.pack(">H", x)

class formChunk:
    ckID = b'FORM' 
    ckSize = pBL(0x011CB45A)#long #length of file starting at A in AIFF aka len(file) - 9
    formType = b'AIFF' 
    def __init__(self, l):
        self.ckSize = pBL(l-9)

    def build(self):
        return self.ckID + self.ckSize + self.formType

class commonChunk:
    ckID = b'COMM'
    ckSize = pBL(0x00000012) #long always 18 for comm
    numChannels = pBS(0x0002) #short
    numSampleFrames =  pBL(0x00472D0B)#long (supposedly unsigned?)  #determines number of sample frames in soundDataChunk.soundData
    sampleSize = pBS(0x0010) #short #determines the size of each sample point from 1 - 32 bits 
    sampleRate = pBL(0x400EAC44) + pBL(00000000) + pBS(0000) #80 bit IEEE Standard 754 floating point number (Standard Apple Numeric Environment [SANE] data type Extended).
    
    def __init__(self, l):
        self.numSampleFrames = pBL(int(l/4))
    
    def build(self):
        return self.ckID + self.ckSize + self.numChannels + self.numSampleFrames + self.sampleSize + self.sampleRate

class textChunk:
    #optional
    possibleID = [b'NAME',b'AUTH',b'(c) ',b'ANNO']
    ckID = b'' 
    ckSize = 0
    text = b''
    
    def __init__(self, c, t):
        self.ckID = c    
        self.text = t
        self.ckSize = pBL(len(self.text))

    def build(self):
        return self.ckID + self.ckSize + self.text
    
    def len(self):
        return len(self.ckID) + len(self.ckSize) + len(self.text)

class markerChunk:
    #optional
    ckID =  b'MARK'
    ckSize = pBL(0)
    numMarkers = pBL(2)
    id = pBL(1)
    position = pBL(0x4100)
    markerName = pBS(0x08) + b'beginLoop' +  pBS(0x00)
    id2 = pBL(2)
    position2 = pBL(0xffffffff)
    markerName2 = pBS(0x08) + b'endLoop' + pBS(0x00)

    def __init__(self):
        pass

    def build(self):
        r = self.numMarkers + self.id + self.position + self.markerName + self.id2 + self.position2 + self.markerName2
        self.ckSize = pBL(len(r))
        r = self.ckID + self.ckSize + r
        return r



class instrumentChunk:
    #optional
    ckID = b'INST'
    ckSize = pBL(0)
    baseNote = b'60' # 0 - 127 MIDI note #s
    detune = b'-50' #-50 - +50
    # 0 - 127 MIDI note #s
    lowNote = b'40'
    highNote = b'70'
    lowVelocity = b'1'
    highVelocity = b'127'
    
    gain = b'6' #dbs
    sustainLoopPlayMode = b'1' 
    sustainLoopBeginLoop = b'1'
    sustainLoopEndLoop = b'1'
    releaseLoopPlayMode = b'2'
    releaseLoopBeginLoop = b''
    releaseLoopEndLoop = b''
    
    def __init__(self):
        self.ckSize = pBL(len(self.baseNote + self.detune + self.lowNote + self.highNote + self.lowVelocity + self.highVelocity + self.gain + self.sustainLoopPlayMode + self.sustainLoopBeginLoop + self.sustainLoopEndLoop + self.releaseLoopPlayMode + self.releaseLoopBeginLoop + self.releaseLoopEndLoop))

    def build(self):
        return self.ckID + self.ckSize + self.baseNote + self.detune + self.lowNote + self.highNote + self.lowVelocity + self.highVelocity + self.gain + self.sustainLoopPlayMode + self.sustainLoopBeginLoop + self.sustainLoopEndLoop + self.releaseLoopPlayMode + self.releaseLoopBeginLoop + self.releaseLoopEndLoop

class soundDataChunk:
    ckID = b'SSND'
    ckSize = pBL(0x011CB434)#long len(file) - (len(packet)+6) 
    offset = pBL(0x00000000) #long
    blockSize = pBL(0x00000000) #long
    soundData = ((0x011CB434-0x7)*b"B")  #ch1 ch2 (1st sample frame) ... ch1 ch2 (commonChunk.numSampleFrames sample frame)
                    # example 12 bit sample point 101000010111 is stored  left justified with the remaning bits as zero padding 1 0 1 0 0 0 0 1 0 1 1 1 0 0 0 0 

    def __init__(self, l, h, s):
        self.size = pBL(l - (h+6))
        self.soundData = s
    
    def build(self):
        return self.ckID + self.ckSize + self.offset + self.blockSize + self.soundData

def buildAiff(soundData, tLen, hLen, op):
   
    fc = formChunk(tLen)
    cc = commonChunk(tLen)
    sd = soundDataChunk(tLen, hLen, soundData)
    
    form = fc.build()
    common = cc.build()
    sound = sd.build()
    if op:
        ret = form
        for c in op:
            ret += c 
        ret += common + sound
    else:
        ret = form + common + sound

    return ret

ohLen = 0x00 #additional length of optional headers
rhLen = 0x36 #required headers length before sound data

ops = []
soundData = ((0x011CB443-0x7)*b"A")
textData = ((0x10)*b"A")
textName = b'ANNO'
optional = textChunk(textName, textData)
#ops.append(optional.build())
textName = b'(c) '
optional = textChunk(textName, textData)
#ops.append(optional.build())
textName = b'NAME'
optional = textChunk(textName, textData)
ops.append(optional.build())
textName = b'AUTH'
optional = textChunk(textName, textData)
ops.append(optional.build())
optional = markerChunk()
ops.append(optional.build())
optional = instrumentChunk()
ops.append(optional.build())


ohLen = len(ops)

hLen = rhLen + ohLen  #total header length
tLen = len(soundData) + hLen #total file length after sound data
content = buildAiff(soundData, tLen, hLen, ops)

file = open("test.aiff", "wb")
file.write(content)
file.close()

