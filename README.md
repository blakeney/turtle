# turtle
Build and execute shell commands in a console-based GUI

## Usage
turtle.py config_file

Where config_file is the name of a YAML configuration file with information about the command to build and run.  See the examples directory.

## Working State
Unstable

## Security Notes
This program, by design, allows execution of arbitrary shell code as the calling user.  Use with caution.

## Dependencies
- Python 2.7
- PyYAML 3+
- urwid 1.2+

