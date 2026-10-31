

This is the new Lab6 folder for the SE-PES1UG24CS637 repository.
It contains the branch coverage test, the module under test, and the terminal screenshot.

PowerShell test command from inside Lab6:
coverage erase
coverage run --branch --source=vending_machine -m pytest -v BranchCoverageTest_PES1UG24CS637_application.py
coverage report -m

Expected result: 7 passed; 100% branch coverage.
