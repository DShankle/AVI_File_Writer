from json.tool import main
import sys, struct

def pLL(x): return struct.pack("<L", x)
def pLS(x): return struct.pack("<H", x)
def pBL(x): return struct.pack(">L", x)
def pBS(x): return struct.pack(">H", x)

class riffChunk:
    ckID = b'RIFF' 
    ckSize = pLL(0x00000000)#long #length of file starting after 'RIFF'
    formType = b'AVI ' 
    
    def __init__(self):
        pass

    def build(self):
        return self.ckID + self.ckSize + self.formType
    
    def reSize(self, l):
        self.ckSize = pLL(l-9)

class listChunk:
    list = b'LIST'
    ckSize = pLL(0x00000000) #size till closing LIST

    def __init__(self, l):
        self.ckSize = pLL(l)
    def build(self):
        return self.list+self.ckSize

class mainHeaderChunk:
    '''
        typedef struct
    {
    DWORD dwMicroSecPerFrame; // frame display rate (or 0)
    DWORD dwMaxBytesPerSec; // max. transfer rate
    DWORD dwPaddingGranularity; // pad to multiples of this
    // size;
    DWORD dwFlags; // the ever-present flags
    DWORD dwTotalFrames; // # frames in file
    DWORD dwInitialFrames;
    DWORD dwStreams;
    DWORD dwSuggestedBufferSize;
    DWORD dwWidth;
    DWORD dwHeight;
    DWORD dwReserved[4];
    } MainAVIHeader;
    '''

    ckID = b'hdrl'
    ckHd = b'avih'
    structSize = pBL(0x38000000)
    dwMicroSecPerFrame = pBL(0x56820000) #409C0000
    dwMaxBytesPerSec = pBL(0xA8610000) #018D0500
    dwPaddingGranularity = pBL(0x00000000)#01000000
    dwFlags = pBL(0x10090000) #00080000
    dwTotalFrames = pBL(0x90010000) #ee020000
    dwInitialFrames = pBL(0x00000000) 
    dwStreams = pBL(0x01000000) #02000000
    dwSuggestedBufferSize = pBL(0x00001000) #981c0300
    dwWidth = pBL(0x80020000) #640x360 #00050000
    dwHeight =  pBL(0x68010000)
    dwReserved = [pBL(0x00000000),pBL(0x00000000),pBL(0x00000000),pBL(0x00000000)] 
   
    def __init__(self):
        #chunkLen = len(self.build())
        #self.ckSize = pLL(chunkLen - 4)
        pass

    def build(self): 
        return self.ckID + self.ckHd + self.structSize + self.dwMicroSecPerFrame + self.dwMaxBytesPerSec + self.dwPaddingGranularity + self.dwFlags + self.dwTotalFrames + self.dwInitialFrames + self.dwStreams + self.dwSuggestedBufferSize + self.dwWidth + self.dwHeight + self.dwReserved[0] + self.dwReserved[1] + self.dwReserved[2] + self.dwReserved[3]

    def reSize(self, l, c):
        self.ckSize = pLL(l-c-4) #len from start to next LIST occurance - current offset of size indicator

class streamHeaderChunk:
    ckID = b'strl'
    ckHd = b'strh'
    structSize = pBL(0x38000000)
    fccTypes = [b'vids',b'auds', b'txts']
    #FOURCC 
    fccType = fccTypes[0]
    #FOURCC 
    fccHandler = b'FMP4'#codec 
    #DWORD AVISF_VIDEO_PALCHANGES or AVISF_DISABLED
    dwFlags =  pBL(0x00000000)
    #WORD 
    wPriority = pBS(0x0000) #idk
    #WORD 
    wLanguage = pBS(0x0000) #idk
    #DWORD Number of the first block of the stream that is present in the file. will need to initilize dynamically
    dwInitialFrames = pBL(0x00000000)
    #DWORD samples per second or frames per second 25/1 or 10,000,000/400,000
    dwScale = pBL(0x00000001) #0xe9030000
    #DWORD 
    dwRate = pBL(0x000000019) #30750000
    #DWORD Start time of stream
    dwStart = pBL(0x00000000)
    #DWORD size of stream in units as defined in dwRate and dwScale
    dwLength = pBL(0x90010000) #stream length / dwRate maybe?
    #DWORD Size of buffer necessary to store blocks of that stream. Can be 0 (in that case the application has to guess)
    dwSuggestedBufferSize = pBL(0xE56A0000)
    #DWORD "should indicate the quality of the stream. Not important"
    dwQuality = pBL(0x00000000) #ffffffff
    #DWORD "number of bytes of one stream atom (that should not be split any further)"
    dwSampleSize = pBL(0x00000000)
    #RECT 
    '''
        typedef struct tagRECT {
        LONG left;
        LONG top;
        LONG right;
        LONG bottom;
        } RECT, *PRECT, *NPRECT, *LPRECT;
    '''
    #idk man
    rcFrame = pBL(0x00000000) + pBL(0x00000000) +  pBL(0x80026801) #00000000 80026801

    def __init__(self):
        #chunkLen = len(self.build())
        #self.ckSize = pLL(chunkLen - 4)
        pass

    def build(self):
        return self.ckID + self.ckHd + self.structSize + self.fccType + self.fccHandler + self.dwFlags + self.wPriority + self.wLanguage + self.dwInitialFrames + self.dwScale + self.dwRate + self.dwLength + self.dwSuggestedBufferSize + self.dwQuality + self.dwSampleSize + self.rcFrame
    
    def reSize(self, l, c):
        self.ckSize = pLL(l-c) #len to next LIST - current offset

class strfChunk:
    '''
    ckID = b'strf'
#tagBITMAPINFOHEADER
  #DWORD 4
  biSize
  #LONG  8
  biWidth
  #LONG  8
  biHeight
  #WORD  2
  biPlanes
  #WORD  2
  biBitCount
  #DWORD 4
  biCompression
  #DWORD 4 
  biSizeImage
  #LONG  8
  biXPelsPerMeter
  #LONG  8
  biYPelsPerMeter
  #DWORD 4
  biClrUsed
  #DWORD 4  = 56 bytes total
  biClrImportant
} BITMAPINFOHEADER, *LPBITMAPINFOHEADER, *PBITMAPINFOHEADER;
    '''
    ckID = b'strf'
    #tagBITMAPINFOHEADER
    ckSize = pBL(0x2C000000)
    #DWORD 4
    biSize = pBL(0x28000000)
    #LONG  8
    biWidth = pBL(0x80020000)
    #LONG  8
    biHeight = pBL(0x68010000)
    #WORD  2
    biPlanes = pBL(0x68010000)
    #WORD  2
    biBitCount = pBL(0x01001800)
    #DWORD 4
    biCompression = b'FMP4' #??
    #DWORD 4 
    biSizeImage = pBL(0x008C0A00)
    #LONG  8
    biXPelsPerMeter = pBL(0x00000000)
    #LONG  8
    biYPelsPerMeter = pBL(0x00000000)
    #DWORD 4
    biClrUsed = pBL(0x00000000)
    #DWORD 4  = 56 bytes total
    biClrImportant = pBL(0x00000000)

    def __init__(self):
        chunkLen = len(self.build())
        self.ckSize = pLL(chunkLen - 8)

    def build(self):
        return self.ckID + self.ckSize + self.biSize + self.biWidth + self.biHeight + self.biPlanes + self.biBitCount + self.biCompression + self.biSizeImage + self.biXPelsPerMeter + self.biYPelsPerMeter + self.biClrUsed + self.biClrImportant 



class moviChunk:
    '''
    Two-character code 	Description
                    db 	Uncompressed video frame
                    dc 	Compressed video frame
                    pc 	Palette change
                    wb 	Audio data
    '''

    ckID = b'movi'
    #tagBITMAPINFOHEADER
    compVid = pBL(0x30306463) # 00dc

    def __init__(self):
        #chunkLen = len(self.build())
        #self.ckSize = pLL(chunkLen - 4)
        pass

    def build(self):
        return self.ckID + self.compVid

    def reSize(self, l, c):
        #self.ckSize = pLL(l-c)
        pass

class indxChunk:

#struct _aviindex_chunk {
    #FOURCC fcc;
    ckID = b'indx'
    #DWORD cb;
    ckSize = pBL()
    #WORD wLongsPerEntry; // size of each entry in aIndex array
    wLongsPerEntry = pBL() #04000000
    #BYTE bIndexSubType; // future use. must be 0
    bIndexSubType = pBL() #01000000
    #BYTE bIndexType; // one of AVI_INDEX_* codes
    bIndexType = pBL() # 30306462
    #DWORD nEntriesInUse; // index of first unused member in aIndex array
    nEntriesInuse = pBL() #00000000
    #DWORD dwChunkId; // fcc of what is indexed
    dwChunkId = pBL() #00000000
    #DWORD dwReserved[3]; // meaning differs for each index type/subtype. 0 if unused
    dwReserved = [pBL(0x00000000),pBL(0x00000000),pBL(0x00000000)]
    #struct _aviindex_entry {
    #DWORD adw[wLongsPerEntry];
    #} aIndex[ ];
#};

    def __init__(self, l, h, s):
        self.size = pLL(l - (h+6))
        self.soundData = s
    
    def build(self):
        return self.ckID + self.ckSize + self.offset + self.blockSize + self.soundData

def buildAvi(vidData):
    rc = riffChunk()
    mhc = mainHeaderChunk()
    shc = streamHeaderChunk()
    strf = strfChunk()
    mov = moviChunk()
    #id = indxChunk()
    riff = rc.build()
    mainHead = mhc.build()
    streamHead = shc.build()
    strfC = strf.build()
    movi = mov.build()
    lenList = len(listChunk(0).build())
    #idx = id.build()
    tl = len(riff + mainHead + streamHead + strfC + movi)
    l = (tl - len(riff)) + lenList*2 
    list1 = listChunk(l).build() 
    l = tl - len(riff + mainHead) + lenList
    list2 = listChunk(l).build()
    l = len(movi + vidData)
    list3 = listChunk(l).build()
    ret = riff + list1 + mainHead + list2 + streamHead + strfC +  list3 + movi + vidData
    rc.reSize(len(ret)+1)
    riff = rc.build()
    ret = riff + list1 + mainHead + list2 + streamHead + strfC + list3 + movi + vidData

    return ret

 

vidData = ((0x1000-0x7)*b"A")
content = buildAvi(vidData)


file = open("test2.avi", "wb")
file.write(content)
file.close()

