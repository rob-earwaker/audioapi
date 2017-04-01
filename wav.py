import struct


class Chunk:
    struct = struct.Struct('<4sI')

    def __init__(self, id, size, data):
        self.id = id
        self.size = size
        self.data = data

    @classmethod
    def read_from(cls, stream):
        id, size = cls.struct.unpack(stream.read(cls.struct.size))
        data = stream.read(size)
        return cls(id, size, data)

    def __repr__(self):
        return 'Chunk(id={0}, size={1}, data=<{2} bytes>)'.format(
            self.id, self.size, len(self.data)
        )


def read_wav(stream):
    chunk = Chunk.read_from(stream)
    print(chunk)
    print('Remaining bytes = {0}'.format(len(stream.read())))


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as file:
        read_wav(file)
