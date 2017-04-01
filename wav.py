import collections
import io
import struct


class ChunkIncompleteError(Exception):
    pass


class WavReadError(Exception):
    pass


def read(size, stream):
    bytes = stream.read(size)
    if len(bytes) < size:
        raise ChunkIncompleteError
    return bytes


def unpack(format, stream):
    format = struct.Struct(format)
    bytes = read(format.size, stream)
    return format.unpack(bytes)


class Chunk:
    def __init__(self, id, size, data):
        self.id = id
        self.size = size
        self.data = data

    @classmethod
    def decode(cls, stream):
        id, size = unpack('<4sI', stream)
        data = read(size, stream)
        return cls(id.decode('ascii'), size, data)


class RiffChunk:
    id = 'RIFF'

    def __init__(self, size, format, subchunks):
        self.size = size
        self.format = format
        self.subchunks = subchunks

    @classmethod
    def decode(cls, stream):
        chunk = Chunk.decode(stream)
        stream = io.BytesIO(chunk.data)
        format = unpack('4s', stream)[0].decode('ascii')
        subchunks = []
        while True:
            try:
                subchunks.append(Chunk.decode(stream))
            except ChunkIncompleteError:
                break
        return cls(chunk.size, format, subchunks)


class RiffWaveChunk:
    id = RiffChunk.id
    format = 'WAVE'

    def __init__(self, size, subchunks):
        self.size = size
        self.subchunks = subchunks

    @classmethod
    def create(cls, chunk):
        return cls(chunk.size, RiffWaveSubchunks.create(chunk.subchunks))


class RiffWaveSubchunks(list):
    def __init__(self, subchunks, format_chunk_index, data_chunk_index):
        super().__init__(subchunks)
        self.format_chunk_index = format_chunk_index
        self.data_chunk_index = data_chunk_index

    @classmethod
    def create(cls, chunks):
        format_chunk_index = next(
            index for index, chunk in enumerate(chunks)
            if chunk.id == WaveFormatChunk.id
        )
        chunks[format_chunk_index] = WaveFormatChunk.create(
            chunks[format_chunk_index]
        )
        if chunks[format_chunk_index].format == PcmWaveFormatChunk.format:
            chunks[format_chunk_index] = PcmWaveFormatChunk.create(
                chunks[format_chunk_index]
            )
        data_chunk_index = next(
            index for index, chunk in enumerate(chunks)
            if chunk.id == WaveDataChunk.id
        )
        return cls(chunks, format_chunk_index, data_chunk_index)

    @property
    def format(self):
        return self[self.format_chunk_index]

    @property
    def data(self):
        return self[self.data_chunk_index]


class WaveFormatChunk:
    id = 'fmt '

    def __init__(self, **kwargs):
        self.size = kwargs['size']
        self.format = kwargs['format']
        self.channels = kwargs['channels']
        self.samplerate = kwargs['samplerate']
        self.byterate = kwargs['byterate']
        self.blockalign = kwargs['blockalign']
        self.specific = kwargs['specific']

    @classmethod
    def create(cls, chunk):
        stream = io.BytesIO(chunk.data)
        Format = collections.namedtuple(
            'Format',
            ['format', 'channels', 'samplerate', 'byterate', 'blockalign']
        )
        format = Format(*unpack('<HHIIH', stream))
        return cls(
            size=chunk.size,
            format=format.format,
            channels=format.channels,
            samplerate=format.samplerate,
            byterate=format.byterate,
            blockalign=format.blockalign,
            specific=stream.read()
        )


class PcmWaveFormatChunk:
    id = WaveFormatChunk.id
    format = 0x0001

    def __init__(self, **kwargs):
        self.size = kwargs['size']
        self.channels = kwargs['channels']
        self.samplerate = kwargs['samplerate']
        self.byterate = kwargs['byterate']
        self.blockalign = kwargs['blockalign']
        self.bitspersample = kwargs['bitspersample']

    @classmethod
    def create(cls, chunk):
        stream = io.BytesIO(chunk.specific)
        return cls(
            size=chunk.size,
            channels=chunk.channels,
            samplerate=chunk.samplerate,
            byterate=chunk.byterate,
            blockalign=chunk.blockalign,
            bitspersample=unpack('<H', stream)[0]
        )


class WaveDataChunk:
    id = 'data'


def decode(stream):
    chunk = RiffChunk.decode(stream)
    if not chunk.format == RiffWaveChunk.format:
        raise ValueError('invalid RIFF format {0}'.format(chunk.format))
    return RiffWaveChunk.create(chunk)


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as file:
        decode(file)
