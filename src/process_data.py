"""
Read all data from input file, generate summaries, and write results.
"""
import os
import multiprocessing as mp
from . import input_format
from . import h1b_data


class Summary:
    """
    Read, store, and write data about job locations and SOC codes for
        certified H1B applications.
    """

    def __init__(self, inputfile):
        """Initialize an empty summary for the given file."""
        self.inputfile = inputfile
        with open(inputfile, 'r') as file:
            header = file.readline()
        self.header_info = input_format.InputFormat(header)
        self.data = None

    def _chunked_file(self, chunk_size):
        """
        Generator for positions of chunks of the input file, yielding
            chunk starting positions and exact sizes. Each chunk will contain
            only complete lines of input, and will skip the header.
            chunk_size -- approximate desired size of chunks in bytes
        """
        file_end = os.path.getsize(self.inputfile)
        with open(self.inputfile, 'r') as file:
            file.readline()     # skip the header
            chunk_end = file.tell()

            while chunk_end <= file_end:
                chunk_start = chunk_end
                current = file.tell()
                file.seek(current + chunk_size)   # move forward by chunk_size
                file.readline()     # move to the end of the current line
                chunk_end = file.tell()
                yield chunk_start, chunk_end - chunk_start

    def read_file(self, chunk_size, cores=None):
        """
        Process the entire input file, using multiple processes to consume it
            in chunks. Results are stored in self.data.
            chunk_size -- approximate desired size of chunks in bytes
            cores -- number of parallel data reading processes to use
        """

        pool = mp.Pool(cores)
        jobs = []

        for chunk_start, exact_size in self._chunked_file(chunk_size):
            jobs.append(pool.apply_async(process_chunk,
                                         (self.inputfile, self.header_info,
                                          chunk_start, exact_size)))

        # wait for all data and gather it
        all_data = [job.get() for job in jobs]

        # Combine results from all chunks
        data = h1b_data.Data(self.header_info)
        for sub_data in all_data:
            data += sub_data

        self.data = data


def process_chunk(filename, header_info, chunk_start, chunk_size):
    """Create a Data object, process the chunk, and return data."""
    data = h1b_data.Data(header_info)
    data.process_chunk(filename, chunk_start, chunk_size)
    return data
