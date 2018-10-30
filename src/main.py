"""
Run the entire data reading, processing, and writing process.
"""
import sys
from . import process_data
from . import input_format


def main(args):
    """
    Read in data, create summaries, and write to output.
        Arguments are source file, occupation output, and state output.
    """
    input_file = args[1]
    output_occupations = args[2]
    output_states = args[3]

    print("Analyzing input_file file:")
    summary = process_data.Summary(input_file)
    print("Reading input data")
    summary.read_file()

    print("Computing summaries")
    occupations = summary.get_results(input_format.Concept.SOC_NAME)
    states = summary.get_results(input_format.Concept.WORK_STATE)

    print("Writing results")
    occupations.to_file(output_occupations)
    states.to_file(output_states)


if __name__ == '__main__':
    main(sys.argv)
