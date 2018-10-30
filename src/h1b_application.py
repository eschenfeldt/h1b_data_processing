"""
Read and process information about a single H1B visa application
"""
import re
from .input_format import Concept


class Application:
    """Relevant information for a single visa application"""

    @property
    def certified(self):
        """This application was certified"""
        return self.status == 'CERTIFIED'

    def __init__(self, raw_data, header_info):
        """Parse a row of the input CSV and store relevant information."""
        entries = raw_data.split(';')
        self.status = self._read_data(Concept.STATUS, entries, header_info)
        self.work_state = self._read_data(Concept.WORK_STATE, entries,
                                          header_info)
        self.soc = self._read_data(Concept.SOC_CODE, entries, header_info)
        self.soc_name = self._read_data(Concept.SOC_NAME, entries,
                                        header_info)

    def _read_data(self, concept, entries, header_info):
        """
        Get data for the given concept from entries, using the column
            indicated by header_info, or its fallback options if data is
            missing.
        """
        try:
            value = entries[header_info.index(concept)]
            value = self._clean(concept, value)
        except IndexError:
            value = None
        if not value:
            for index in header_info.fallbacks(concept):
                try:
                    value = self._clean(concept, entries[index])
                except IndexError:
                    value = None
                if value:
                    break

        return value

    def _clean(self, concept, value):
        """
        Take a raw value for the given concept and ensure it is in the
            expected format, or convert it to that format if possible.
        """
        if concept is Concept.STATUS or concept is Concept.SOC_NAME:
            return self._ensure_upper(value)
        elif concept is Concept.SOC_CODE:
            return self._clean_soc_code(value)
        elif concept is Concept.WORK_STATE:
            return self._clean_state(value)

    def _ensure_upper(self, value):
        """
        Clean a raw short text entry, ensuring it is an upper-case string.
            Currently used for status and job name.
        """
        try:
            return value.upper()
        except AttributeError:
            return None

    def _clean_soc_code(self, value):
        """
        Clean a raw SOC code, ensuring it uses the expected XX-XXXX format.
            Values that contain at least 6 digits will use the first 6 digits
            to define the code, regardless of separators or trailing
            characters. Values without enough digits will be treated as
            invalid.
        """
        digits = re.sub(r'[^\d]', '', value)
        if len(digits) < 6:
            return None
        else:
            return '{}-{}'.format(digits[:2], digits[2:6])

    def _clean_state(self, value):
        """
        Clean a raw state abbreviation, ensuring it represents a valid ANSI
            abbreviation for a state or US Territory.
            Standardization is limited to accepting lowercase entries; no
            attempt is made to convert full names to abbreviations.
        """
        try:
            value = value.upper()
        except AttributeError:
            return None

        if value in _STATES:
            return value
        else:
            return None


_STATES = [
    'AK', 'AL', 'AR', 'AS', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'FM',
    'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD',
    'ME', 'MH', 'MI', 'MN', 'MO', 'MP', 'MS', 'MT', 'NA', 'NC', 'ND', 'NE',
    'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'PW', 'RI',
    'SC', 'SD', 'TN', 'TX', 'UM', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV',
    'WY',
]
