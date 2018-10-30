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

    def __init__(self, input_file):
        """Initialize an empty summary for the given file."""
        self.input_file = input_file
        with open(input_file, 'r') as file:
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
        file_end = os.path.getsize(self.input_file)
        with open(self.input_file, 'r') as file:
            file.readline()     # skip the header
            chunk_end = file.tell()

            while chunk_end <= file_end:
                chunk_start = chunk_end
                current = file.tell()
                file.seek(current + chunk_size)   # move forward by chunk_size
                file.readline()     # move to the end of the current line
                chunk_end = file.tell()
                yield chunk_start, chunk_end - chunk_start

    def read_file(self, chunk_size=1024 * 1024, cores=None):
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
                                         (self.input_file, self.header_info,
                                          chunk_start, exact_size)))

        # wait for all data and gather it
        all_data = [job.get() for job in jobs]

        # Combine results from all chunks
        data = h1b_data.Data(self.header_info)
        for sub_data in all_data:
            data += sub_data

        self.data = data

    def get_results(self, result_type):
        """
        Get the top 10 states or occupations prepared for writing to the output
            file.
        """
        if result_type is input_format.Concept.WORK_STATE:
            full_counter = self.data.states
            first_header = 'TOP_STATES'
        elif result_type is input_format.Concept.SOC_NAME:
            full_counter = self.data.soc_codes
            first_header = 'TOP_OCCUPATIONS'
        else:
            raise ValueError('Unrecognized result type {}'.format(result_type))
        # Get total number of states
        total = sum(full_counter.values())

        # Get the top states (using a Counter method)
        top_ten = full_counter.most_common(10)

        # Check for ties
        last_count = top_ten[-1][1]
        tied = [k for k, v in full_counter.items() if v == last_count]

        if len(tied) > 1:
            # Only process further if there actually is a tie in the last
            #   position. Then start by taking those above the tie
            top = [(k, v) for (k, v) in top_ten if v != last_count]
            # Then add in everything from the tie
            top_ten = top + [(k, last_count) for k in tied]
            # This leaves us with possibly too many items, but we'll truncate
            #   after we sort fully

        if result_type is input_format.Concept.SOC_NAME:
            # Replace SOC codes with occupation names
            temp = []
            for (code, count) in top_ten:
                name = self.data.soc_names[code].most_common(1)[0][0]
                name = name.strip('"')
                temp.append((name, count))
            top_ten = temp

        # Sort by name then count, using python's stable sort order to get
        #   the desired multi_level count
        top_ten.sort(key=lambda x: x[0])
        top_ten.sort(key=lambda x: x[1], reverse=True)

        return Results(first_header, top_ten, total)


class Results:
    """
    Store the top ten with names, counts, and the total. Provides methods for
        writing to a file.
    """

    def __init__(self, first_header, top_ten, total):
        """
        Stores results of the given type to write to output file.
            top_ten -- a sorted list of (name, count) tuples
        """
        self._first_header = first_header
        self._top_ten = top_ten
        self._total = total

    def to_file(self, outfile):
        """Write to the given output file."""
        with open(outfile, 'w') as file:
            header = [self._first_header, 'NUMBER_CERTIFIED_APPLICATIONS',
                      'PERCENTAGE']
            file.write(';'.join(header) + '\n')

            for name, count in self._top_ten:
                percentage = (count / self._total) * 100
                line = [name, str(count), '{:.1f}%'.format(percentage)]
                file.write(';'.join(line) + '\n')


def process_chunk(filename, header_info, chunk_start, chunk_size):
    """Create a Data object, process the chunk, and return data."""
    data = h1b_data.Data(header_info)
    data.process_chunk(filename, chunk_start, chunk_size)
    return data
