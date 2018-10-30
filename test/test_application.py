import unittest
import src.input_format as input_format
import src.h1b_application as h1b_app


class ApplicationTestCase(unittest.TestCase):
    """Tests for entry reading and cleaning in `src/h1b_application.py`."""

    def setUp(self):
        """Generate a simple header to allow us to build simple test rows."""
        header = 'CASE_STATUS;WORKSITE_STATE;SOC_CODE;SOC_NAME'
        self.header_info = input_format.InputFormat(header)

    def test_status_clean(self):
        raw_data = 'Certified;AL;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertEqual(app.status, 'CERTIFIED')

    def test_soc_clean(self):
        raw_data = 'CERTIFIED;AL;1511-31;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertEqual(app.soc, '15-1131')

    def test_state_clean(self):
        raw_data = 'CERTIFIED;mi;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertEqual(app.work_state, 'MI')

    def test_puerto_rico(self):
        raw_data = 'CERTIFIED;pr;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertEqual(app.work_state, 'PR')

    def test_invalid_state(self):
        raw_data = 'CERTIFIED;Michigan;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertEqual(app.work_state, None)

    def test_certified(self):
        raw_data = 'CERTIFIED;AL;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertTrue(app.certified)

    def test_not_certified(self):
        raw_data = 'CERTIFIED-WITHDRAWN;AL;15-1131;SOME JOB'
        app = h1b_app.Application(raw_data, self.header_info)
        self.assertFalse(app.certified)


if __name__ == '__main__':
    unittest.main()
