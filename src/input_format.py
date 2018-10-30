"""
Generate and store information about the structure of an input file, primarily
    the locations of columns of interest.
"""
import re


class InputError(Exception):
    pass


class Concept:
    """Constants representing the types of data we need for this problem."""
    STATUS = 'status'
    WORK_STATE = 'state'
    SOC_CODE = 'soc_code'
    SOC_NAME = 'soc_name'


class ColumnInfo:
    """Store information about a data column of interest, to aid in finding it
        in a particular input file.
    """

    @property
    def index(self):
        """Index of the column for this data."""
        return self._indices[0]

    @property
    def fallbacks(self):
        """Index of other columns that might contain this data."""
        return self._indices[1:]

    def __init__(self, name, known_names, pattern):
        """Column or columns representing a particular piece of data.
        Arguments:
        name -- name of this piece of data
        known_names -- names known to correspond to the desired data; the
                        first of these to match will be used
        pattern -- fallback regex pattern to match if no known names are
                    found
        """
        self.name = name
        self._known_names = known_names
        self._pattern = pattern
        self._indices = None

    def find_indices(self, columns):
        """Find the indices for this piece of data in the given columns."""
        indices = []
        for name in self._known_names:
            if name in columns:
                indices.append(columns.index(name))

        # If these don't match, search using a case-insensitive regex
        for j, col in enumerate(columns):
            if re.search(self._pattern, col, flags=re.IGNORECASE):
                indices.append(j)

        if not indices:
            mes = f'No columns match for {known_names} or "{pattern}"'
            raise InputError(mes)

        self._indices = indices


class InputFormat:
    """
    Store the locations of columns of interest in a particular input file.
    """

    def __init__(self, header):
        """Given the header row of an input file, parse format."""
        columns = header.split(';')
        info = {}
        info[Concept.STATUS] = ColumnInfo(
            Concept.STATUS,
            ['CASE_STATUS', 'STATUS'],
            r'status'
        )
        info[Concept.WORK_STATE] = ColumnInfo(
            Concept.WORK_STATE,
            ['WORKSITE_STATE', 'LCA_CASE_WORKLOC1_STATE'],
            r'work.*state'
        )
        info[Concept.SOC_CODE] = ColumnInfo(
            Concept.SOC_CODE,
            ['SOC_CODE', 'LCA_CASE_SOC_CODE'],
            r'soc.*code'
        )
        info[Concept.SOC_NAME] = ColumnInfo(
            Concept.SOC_NAME,
            ['SOC_NAME', 'LCA_CASE_SOC_NAME'],
            r'soc.*name'
        )
        for col_info in info.values():
            col_info.find_indices(columns)

        self._info = info

    def index(self, concept):
        """Get the primary index for the desired concept."""
        return self._info[concept].index

    def fallbacks(self, concept):
        """Get the fallback indices for the desired concept."""
        return self._info[concept].fallbacks
