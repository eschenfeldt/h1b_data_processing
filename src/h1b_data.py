"""
Parse and store intermediate data from part of an input file
"""
from . import h1b_application
from collections import Counter


class Data:
    """
    Store data about job locations and SOC codes for certified H1B
        applications.
    """

    def __init__(self, header_info):
        """
        An empty container for intermediate data.
        """
        self.header_info = header_info
        self.states = Counter()
        self.soc_codes = Counter()
        self.soc_names = {}

    def process_one(self, line):
        """
        Read one line of input data and update intermediate data.
        """
        app = h1b_application.Application(line, self.header_info)
        if not app.certified:
            return

        if app.work_state is not None:
            self.states[app.work_state] += 1

        if app.soc is not None:
            self.soc_codes[app.soc] += 1

            if app.soc in self.soc_names:
                self.soc_names[app.soc][app.soc_name] += 1
            else:
                self.soc_names[app.soc] = Counter({app.soc_name: 1})

    def process_chunk(self, filename, chunk_start, chunk_size):
        """
        Read and process a portion of the given file
        """
        with open(filename, 'r') as f:
            f.seek(chunk_start)
            lines = f.read(chunk_size).splitlines()
            for line in lines:
                self.process_one(line)

    def __add__(self, other):
        """
        Add counts from another Data object, returning a new Data object
        """
        states = self.states + other.states
        soc_codes = self.soc_codes + other.soc_codes
        soc_names = {}
        for code in (self.soc_names.keys() | other.soc_names.keys()):
            if code in self.soc_names and code in other.soc_names:
                soc_names[code] = self.soc_names[code] + other.soc_names[code]
            elif code in self.soc_names:
                soc_names[code] = self.soc_names[code]
            else:
                soc_names[code] = other.soc_names[code]

        out = Data(self.header_info)
        out.states = states
        out.soc_codes = soc_codes
        out.soc_names = soc_names

        return out
