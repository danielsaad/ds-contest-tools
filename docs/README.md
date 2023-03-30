# Overview

This manual provides instructions for using various tools included in the software package. These tools are designed to help users initialize, build, convert, and manage problems for competitive programming contests.

## build.py

The build.py tool provides several options for building and managing problems.

### init

Initializes a problem with the necessary files and directories.

Usage: `python3 build.py init [-i] <problem_id>`

Options:
- **-i**: Initializes an interactive problem. In interactive problems, the example tests are the input/output files ending with '.interactive'.

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

### convert

Converts a problem to one of the following formats:

- *BOCA*: Not implemented. Use pack2boca from build.py.
- *SQTPM*: Convert problem to SQTPM in a new folder. 
- *Polygon*: Send problem to Polygon. Inumerous requests are made in order to convert the problem. These changes are made during the conversion to Polygon:
    - General info and statement texts are changed.
    - Source, resource, auxiliar and solution files with the same name as the new ones will be overwritten.
    - Testcases with the same index as the new ones will be overwritten.
    - Script will be overwritten if a script request was made.

Usage: `python3 convert.py convert <format> <problem_id> <output_folder_or_polygon_id>`

Options:
- **-o**: Define a output directory for the problem. In case of a Polygon conversion, defines the ID of the problem in the file problem.json.

### convert_polygon

Converts problem from Polygon. Downloads the latest ready linux package from Polygon in the problem folder and use it to convert the problem. Aditional requests are made to the API in order to find the name of the source files and the type of the problem.

Usage: `python3 convert.py convert_polygon [-l] <problem_id> <package_folder_or_polygon_id`

Options:
- **-l**: Converts problem from a local Polygon package. It is possible to convert FULL and STANDARD packages. Requests are not made, so the user needs to specify if the problem is interactive or not, and change the name of the source files.

### change_keys

Changes the Polygon API keys of the user and saves it locally in the tool directory.

Usage: `python3 convert.py change_keys`

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