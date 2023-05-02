# Overview

This manual provides instructions for using various tools included in the software package. These tools are designed to help users initialize, build, convert, and manage problems for competitive programming contests.

## How to create a problem

Creating a problem requires several steps, which can be done in any order. Follow these guidelines:

1. **Initialize the problem**: Start by initializing the problem.
2. **Write the statement**: Write the statement text inside each file in the `statement` folder.
3. **Configure the problem**: Use `problem.json` to configure the problem.
4. **Write the solution**: Write the solution files inside the `src` folder and add them in `problem.json`.
5. **Modify the problem**: Modify the generator, validator, checker, and interactor (if it's an interactive problem) of the problem, inside the `src` folder.
6. **Generate testcases**: Write the scripts to generate test cases inside the `script.sh` file in the `src` folder. Each line of the script must contain the name of the generator and the arguments used to generate the tests.
7. **Build the problem**: Build the problem with the tool!

# Commands
## build.py

The build.py tool provides several options for building and managing problems.

### init

Initializes a problem with the necessary files and directories.

Usage: `python3 build.py init [-i] <problem_id>`

Options:
- **-i**: Initializes an interactive problem. In interactive problems, the example tests are the input/output files ending with '.interactive'.
- **-c**: Number of threads to be used when running the checker to verify the solution files.

### build

Builds the problem with only the main solution.

Usage: `python3 build.py build [-a] <problem_id>`

Options: 
- **-a**: Builds problem with all solutions.
- **-s**: Builds problem with only the specific solution.

### pack2boca

Packs a problem to the BOCA format. Returns a ZIP file inside the problem folder with the problem converted.

Usage: `python3 build.py pack2boca <problem_id>` 

### genpdf

Generates a PDF of the problem statement.

Usage: `python build.py genpdf <problem_id>`

### genio

Generates input and output files of the problem.

Usage: `python build.py genio <problem_id>`

### clean

Removes executables created after building the problem.

Usage: `python build.py clean <problem_id>`

## convert.py

The convert.py tool provides several options for converting problems to other formats.

### convert_to

Converts a problem to one of the following formats:

- *BOCA*: Not implemented. Use pack2boca from build.py.
- *SQTPM*: Convert problem to SQTPM in a new folder. 
- *Polygon*: Send problem to Polygon. Inumerous requests are made in order to convert the problem. These changes are made during the conversion to Polygon:
    - General info and statement texts are changed.
    - Source, resource, auxiliar and solution files with the same name as the new ones will be overwritten.
    - Testcases with the same index as the new ones will be overwritten.
    - Script will be overwritten if a script request was made.

Usage: `python3 convert.py [-o] convert_to <format> <problem_id>`

Options:
- **-o**: Define a output directory for the problem. In case of a Polygon conversion, defines the ID of the problem in the file problem.json for future uses.

### convert_from

Converts a problem from one of the following formats to DS format:
- *Polygon*: Downloads the latest ready linux package from Polygon in the problem folder and use it to convert the problem. Aditional requests are made to the API in order to find the name of the source files and the type of the problem. It is also possible to convert local problems.

Usage: `python3 convert.py [-l] convert_from <format> <problem_dir> <package_dir_or_polygon_id>`

Options:
- **-l**: Converts local Polygon package to DS. It is possible to convert FULL and STANDARD packages. Requests are not made, so the user needs to specify if the problem is interactive or not, and change the name of the source files to DS standard.

### set_keys

Changes the Polygon API keys of the user and saves it locally in the tool directory.

Usage: `python3 convert.py set_keys`

## contest.py

The contest.py tool provides several options for creating contests with a list of problems.

### build

Generates folder with merged problems PDFs. 

Usage: `python3 contest.py build [-b, --boca] <problem_id [problem_id...]> <contest_folder>` 

Options:
- **-b, --boca**: Generates a folder with merged problems PDFs and BOCA zipped files of the problems.

### genpdf

Generates folder with merged problems PDFs. Does the same as build without the flag *-b*.

Usage: `python3 contest.py genpdf <problem_id [problem_id...]> <contest_folder>` 

## legacy_converter.py

Converts a legacy problem to the new version. Removes the testlib folder and CMake file, and saves statement.md.

Usage: `python3 legacy_converter.py <problem_id>`