#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
from ds_contest_tools import main
from multiprocessing import set_start_method
if __name__ == '__main__':
    set_start_method("fork") # TODO: Fix this issue. Now modern python does not use fork semantics anymore.
    main()
