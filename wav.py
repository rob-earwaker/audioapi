import struct


class WavReadError(Exception):
    pass


def read_fourcc(stream):
    return struct.unpack('4s', stream.read(4))[0].decode('ascii')


def read_ushort(stream):
    return struct.unpack('<H', stream.read(2))[0]


def read_uint(stream):
    return struct.unpack('<I', stream.read(4))[0]


class WavFile:
    def __init__(self, *args):
        self.channel_count = args[0]
        self.sample_rate = args[1]
        self.byte_rate = args[2]
        self.block_align = args[3]
        self.bits_per_sample = args[4]
        self.data = args[5]


def read(stream):
    chunk_id = read_fourcc(stream)
    if chunk_id != 'RIFF':
        raise WavReadError
    chunk_size = read_uint(stream)
    riff_end_pos = stream.tell() + chunk_size
    riff_format = read_fourcc(stream)
    if riff_format != 'WAVE':
        raise WavReadError
    while stream.tell() < riff_end_pos:
        chunk_id = read_fourcc(stream)
        if chunk_id == 'fmt ':
            chunk_size = read_uint(stream)
            wave_format_end_pos = stream.tell() + chunk_size
            wave_format = read_ushort(stream)
            if wave_format != 0x0001:
                raise WavReadError
            channel_count = read_ushort(stream)
            sample_rate = read_uint(stream)
            byte_rate = read_uint(stream)
            block_align = read_ushort(stream)
            bits_per_sample = read_ushort(stream)
            stream.read(wave_format_end_pos - stream.tell())
        elif chunk_id == 'data':
            chunk_size = read_uint(stream)
            wave_data_end_pos = stream.tell() + chunk_size
            bytes_per_sample = bits_per_sample // 8
            sample_formats = {1: 'B', 2: 'h', 4: 'i', 8: 'q'}
            sample_format = '<{0}'.format(
                sample_formats[bytes_per_sample] * channel_count
            )
            data = []
            while stream.tell() < wave_data_end_pos:
                data.append(
                    struct.unpack(
                        sample_format,
                        stream.read(bytes_per_sample * channel_count)
                    )
                )
        else:
            chunk_size = read_uint(stream)
            stream.read(chunk_size)
    return WavFile(
        channel_count,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        data
    )


if __name__ == '__main__':
    import sys
    with open(sys.argv[1], 'rb') as file:
        read(file)
