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

    def bytes(self):
        return (
            struct.pack('<4sI', self.id.encode('ascii'), self.size) + self.data
        )

    def stream(self):
        return io.BytesIO(self.bytes())

    def __repr__(self):
        return 'Chunk(id={0}, size={1}, data=<{2} bytes>)'.format(
            repr(self.id), repr(self.size), len(self.data)
        )


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

    def chunk(self):
        data = (
            struct.pack('4s', self.format.encode('ascii')) +
            ''.join(subchunk.bytes() for subchunk in self.subchunks)
        )
        return Chunk(self.id, self.size, data)

    def bytes(self):
        return self.chunk().bytes()

    def stream(self):
        return self.chunk().stream()

    def __repr__(self):
        return 'RiffChunk(size={0}, format={1}, subchunks={2}'.format(
            repr(self.size), repr(self.format), repr(self.subchunks)
        )


class RiffWaveChunk:
    id = RiffChunk.id
    format = 'WAVE'

    def __init__(self, size, subchunks):
        self.size = size
        self.subchunks = subchunks

    @classmethod
    def create(cls, chunk):
        return cls(chunk.size, RiffWaveSubchunks.create(chunk.subchunks))

    def __repr__(self):
        return 'RiffWaveChunk(size={0}, subchunks={1})'.format(
            repr(self.size), repr(self.subchunks)
        )


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

    def __repr__(self):
        return (
            'RiffWaveSubchunks(subchunks={0}, format_chunk_index={1}, '
            'data_chunk_index={2})'
        ).format(
            repr(list(self)),
            repr(self.format_chunk_index),
            repr(self.data_chunk_index)
        )


class WaveFormat(int):
    PCM = 0x0001

    def __repr__(self):
        return (
            'WaveFormat.PCM' if self == WaveFormat.PCM
            else 'WaveFormat({0})'.format(repr(self))
        )


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
            format=WaveFormat(format.format),
            channels=format.channels,
            samplerate=format.samplerate,
            byterate=format.byterate,
            blockalign=format.blockalign,
            specific=stream.read()
        )

    def __repr__(self):
        return (
            'WaveFormatChunk(size={0}, format={1}, channels={2}, '
            'samplerate={3}, byterate={4}, blockalign={5}, '
            'specific=<{6} bytes>)'
        ).format(
            repr(self.size),
            repr(self.format),
            repr(self.channels),
            repr(self.samplerate),
            repr(self.byterate),
            repr(self.blockalign),
            len(self.specific)
        )


class PcmWaveFormatChunk:
    id = WaveFormatChunk.id
    format = WaveFormat.PCM

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

    def __repr__(self):
        return (
            'PcmWaveFormatChunk(size={0}, channels={1}, samplerate={2}, '
            'byterate={3}, blockalign={4}, bitspersample={5})'
        ).format(
            repr(self.size),
            repr(self.channels),
            repr(self.samplerate),
            repr(self.byterate),
            repr(self.blockalign),
            repr(self.bitspersample)
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
