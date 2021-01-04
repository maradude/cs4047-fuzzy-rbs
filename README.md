# README

## run instruction

The following insturction assume you have python 3.9 or higher available and
are using a unix-like shell. For plots to work you will also need matplotlib
to be configured to work on your system. For most systems this should be fine, but
MacOS Big Sur seems to show issues with the GUI. Importing and running functions from
main.py from a jupyter notebook seemed to be an potential workaround.

1. Create a virtualenvironment using Python 3.9 or higher
  - `python -m venv venv && source venv/bin/activate`
2. Install the packages listed in requirements.txt
  - `pip install -r requirements.txt`
3. Run the main.py with appropriate command line arguments
  - `python main.py -e tipping` to run the first premade experiment
  - `python main.py -e 3d` to run the second premade experiment
  - e.g. `python main.py -f ./example.txt` to use the rules, variables, values and measurements inside to run a quick defuzz with additional information and plots. Substitute `./example.txt` with any path to a valid fuzzy rulebase system config file.