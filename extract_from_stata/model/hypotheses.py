import re

import extract_from_stata.model.common


def is_beginning_of_table(line):
    pattern = re.compile(r"^-+$")

    return pattern.match(line)


def find_first_table_in(string):
    table_string = ""

    for line in string.splitlines(True):
        if is_beginning_of_table(line):
            table_string += line
        elif table_string:
            if not line.strip():
                break

            table_string += line

    return table_string


def extract_dependent_variable(table_string):
    pattern = re.compile(r"^ *([A-Za-z0-9_~]+) +\|")

    header_started = False
    for line in table_string.splitlines():
        if not header_started and line.startswith("----"):
            header_started = True
        elif header_started and line.startswith("----"):
            return None # This shouldn't happen.
        elif header_started:
            match = pattern.match(line)

            if match is None:
                continue

            return match.group(1)

    return None # This shouldn't be reached.


def extract_coefficient(table_string):
    pattern = re.compile(r"^ *\(1\) +\| +(-?[0-9.e-]+) +([0-9.e-]+) +-?[0-9.]+ +([0-9.]+)")

    for line in table_string.splitlines():
        match = pattern.match(line)

        if match is None:
            continue

        return dict(coefficient=match.group(1),
                    std_error=match.group(2),
                    p_value=match.group(3))

    return None


def label_from(parameters):
    for param, value in parameters:
        if param == "label" and len(value) >= 1:
            # FIXME Hack.  It should never've been split up by
            # the comma in the first place.
            #
            return ", ".join(value)

    return None


def parse_hypothesis(block):
    table_string = find_first_table_in(block)
    parameters = extract_from_stata.model.common.find_parameters_in(block)

    return dict(dependent_variable=extract_dependent_variable(
                                       table_string),
                coefficients={label_from(parameters):
                                  extract_coefficient(table_string)},
                parameters=parameters)
