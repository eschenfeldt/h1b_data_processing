## Problem

Given a semicolon separated file of data on H1B visa applications, generate lists of the top ten occupations and top ten states for certified visa applications. This needs to be done in a way that scales to accomodate large amounts of data and can adapt to minor differences in input format so it can be easily used with future data. 

## Approach

I elected to use Python 3.6 for my solution to this problem. Several main pieces of the solution address different parts of the problem:

### Input format

Because the input file may contain different columns, and specifically data from different years may use different column names, I introduced the module `src.input_format` to automatically process the header of the input file and determine what data to use. This module defines the classes `ColumnInfo`, which defines the location of a particular column of interest and `InputFormat`, which creates and stores `ColumnInfo` objects for the specific columns we need for this problem, namely the application status, the occupation state, and the code and name for the occupation.

To identify these columns, I use a two tiered search through the column names, first looking for an exact match using the names from sample files, then using simple regular expressions that mimic the patterns in those names. If multiple columns match, the secondary matches (with regex matches behind known names) are preserved to be used in case the primary column has missing or malformed data. The regex searches are crude, and when applying this code to future data it would definitely be safest to manually identify the columns of interest and rename them in the input file, but this approach should provide some level of flexibility if the source has minor changes.

### Validating and cleaning data

As we read in the data, we want to ensure that it is in a consistent format so we can safely process it later. Using the column information from `src.input_format`, the module `src.h1b_application` parses a single line of input data into an `Application` object that stores our relevant data. The primary cleaning steps here are to strip non-digit characters from SOC codes and format them consistently as XX-XXXX. If there are fewer than 6 digits the code is treated as missing, but if there are more the extra digits are discarded, as they appeared to simply be extraneous in the sample data (i.e. they do not provide information because the SOC standard doesn't use them but they didn't seem to indicate that the initial digits should be discarded). States are expected to be a two character code and validated as corresponding to a US state or territory, and application status and SOC name are standardized to upper case.

### Aggregating the data

While `src.h1b_application.Application` handles the reading of a single line, the aggregation of lines together is handled by the modules `src.h1b_data` and `src.process_data`. These two modules together implement a parallel reading scheme using a `multiprocessing.Pool` to get somewhat better performance reading large files than reading each line serially. The `Summary` class in `process_data` handles splitting the source file into chunks and coordinating the processes, while `Data` in `h1b_data` defines how data is aggregated. The chunking and multiprocessing code follows the general approach of[this blog post](https://www.blopig.com/blog/2016/08/processing-large-files-using-python/).

In more detail, `Data` stores `collection.Counter` objects for states and SOC codes, which are incremented for every certified application with a particular state/code. Since each code needs to be associated with a name and any given line of the input file may be missing the SOC name `Data` also stores counters of names for each SOC code. Finally, `Data.__add__` is implemented to add counts together, allowing for simple aggregation of data generated from different chunks of the input file.

### Summarizing the data

The `Summary` class in `src.process_data` also defines a `get_results` method that identifies the top ten in each category and sorts them, returning a `Results` object which defines the actual writing to output files. Because `collection.Counter` defines a `most_common` method that can be used to choose the top 10, most of the work in `get_results` is checking for possible ties with 10th place and sorting by name. SOC codes are converted to names by taking the most common name for a given code. Rounding and formatting of percentages is handled by f-string float formatting.

## Run instructions

The module `src.main` can be run with command line arguments for the input file, occupations output file, and states output file, in that order. The script `run.sh` demonstrates this with default input and output names, specifically as
```python3 -m src.main ./input/h1b_input.csv ./output/top_10_occupations.txt ./output/top_10_states.txt
```
The `src` folder is a package to facilitate some unit tests, which can be run from the root directory via
```python3 -m unittest discover```
