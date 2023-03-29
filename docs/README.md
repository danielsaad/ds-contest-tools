# Overview

This manual provides instructions for using various tools included in the software package. These tools are designed to help users initialize, build, convert, and manage problems for competitive programming contests.

## build.py

The build.py tool provides several options for building and managing problems.

### init

Initializes a problem with the necessary files and directories.

Usage: `python3 build.py init [-i] <problem_id>`

Options:
- **-i**: Initializes an interactive problem with interactive files for statement inputs/outputs.

### build

Builds the main solution of a problem.

Usage: `python3 build.py build [-a] <problem_id>`

Options: 
- **-a**: Builds all the solutions of a problem.

### pack2boca

Packs a problem to the BOCA format. Returns a ZIP file inside the problem folder with the problem converted.

Usage: `python3 build.py pack2boca <problem_id>` 

### genpdf

Generates a PDF file of the problem statement.

Usage: `python build.py genpdf <problem_id>`

### genio

enerates input and output files for the problem.

Usage: `python build.py genio <problem_id>`

### clean

Removes executables (bin/ folder) of the problem.

Usage: `python build.py clean <problem_id>`

## convert.py

The convert.py tool provides several options for converting problems to other formats.

### convert

Converts a problem to one of the following formats:

- *BOCA*: Not implemented. Use pack2boca from build.py.
- *SQTPM*: Convert problem to SQTPM in a new folder. 
- *Polygon*: Send problem to Polygon. Many requests are made in order to convert the problem. The requests to Polygon make these changes:
    - General information and statement text change.
    - Source, resource and auxiliar, testcases, script and solution files are replaced with files which have the same name as them. If not, the files remain in stored in Polygon 

Usage: `python3 convert.py convert <format> <problem_id> <output_folder_or_polygon_id>`

### convert_polygon

Converts problem from Polygon. Downloads the latest ready linux package from Polygon in the problem folder and use it to convert the problem. More requests are made to the API in order to find the name of the source files.

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