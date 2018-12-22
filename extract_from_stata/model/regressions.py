import re
import collections

import extract_from_stata.model.common


def is_beginning_of_table(line):
    return (line.startswith("Linear regression")
            or re.match(r"^ +Source \| +SS +df +MS", line) is not None
            or line.startswith("Negative binomial regression")
            or line.startswith("HDFE Linear regression")
            # reghdfe IV estimation:
            or line.startswith("Estimates efficient for homoskedasticity only")
            # margins:
            or line.startswith("Average marginal effects")) # XXX


def find_first_table_in(string):
    table_string = ""

    for line in string.splitlines(True):
        if is_beginning_of_table(line):
            table_string += line
        elif table_string and not line.strip():
            if re.search(r"^----+$", table_string, flags=re.M):
                break
            else:
                table_string += line
        elif table_string:
            table_string += line

    return table_string


assert (find_first_table_in(
            "foo\nbar\nLinear regression\n\n----\nfoo\nbar\n\nlipsum\n")
        == "Linear regression\n\n----\nfoo\nbar\n")


def param_to_show_categoricals(parameters):
    return ("show_categoricals"
            in set(param for param, value in parameters))


def param_to_show_constant(parameters):
    return ("show_constant"
            in set(param for param, value in parameters))


def extract_sample_size(table_string):
    pattern = re.compile(r"Number of obs += +([\d,]+)")

    match = pattern.search(table_string)

    if match is None:
        return None

    return match.group(1).replace(",", "")


def extract_number_of_clusters(table_string):
    pattern = re.compile(r"adjusted for (\d+) clusters in")

    match = pattern.search(table_string)

    if match is None:
        return None

    return match.group(1)


def _extract_depvar_from_table_header(table_string):
    pattern = re.compile(r"^ *([A-Za-z0-9_~]+) +\| +Coef[.] ")

    for line in table_string.splitlines():
        match = pattern.match(line)

        if match is None:
            continue

        return match.group(1)

    return None # This shouldn't be reached.


def _extract_depvar_from_table_preamble(table_string):
    pattern = re.compile(r"^Expression *: +Pr\(([^)]+)\)")

    for line in table_string.splitlines():
        match = pattern.match(line)

        if match is not None:
            return match.group(1)

    return None


def extract_dependent_variable(table_string):
    varname = _extract_depvar_from_table_preamble(table_string)

    if varname is None:
        varname = _extract_depvar_from_table_header(table_string)

    return varname


def extract_categorical_variable(line):
    pattern = re.compile(r"^ *([A-Za-z0-9_~#.]+) +\| *$")
    match = pattern.match(line)

    if match is None:
        return None

    return match.group(1)


def is_start_of_new_block(line):
    return extract_categorical_variable(line) is not None


assert is_start_of_new_block("  birth_year |")
assert not is_start_of_new_block(
               " saw_protest |   .0500882   .0193186")


def is_end_of_block(line):
    pattern = re.compile(r"^ +\| *$")

    return line.startswith("----") or pattern.match(line) is not None


def extract_coefficients(table_string, parameters):
    pattern = re.compile(r"^ *([A-Za-z0-9_~#. ]+) +\| +(-?[0-9.e-]+) +([0-9.e-]+) +-?[0-9.]+ +([0-9.]+)")

    coefficients = collections.OrderedDict()

    segment = "pre-header"
    categorical_block = False
    categorical_variable = None

    for line in table_string.splitlines():
        if segment == "pre-header" and re.match(r"^----+$", line):
            segment = "header"
        elif segment == "header" and re.match(r"^----+[+]-+$", line):
            segment = "post-header"
        elif segment == "post-header":
            if categorical_block and is_end_of_block(line):
                categorical_block = False
            elif is_start_of_new_block(line):
                categorical_block = True
                categorical_variable = extract_categorical_variable(
                                           line)
            elif (categorical_block
                  and not param_to_show_categoricals(parameters)):
                continue
            else:
                match = pattern.match(line)

                if match is None:
                    continue
                elif (match.group(1) == "_cons"
                      and not param_to_show_constant(parameters)):
                    continue

                if categorical_block:
                    variable_name = "%s.%s" % (match.group(1).strip(),
                                               categorical_variable)
                else:
                    variable_name = match.group(1)

                coefficients[variable_name] = (
                    dict(coefficient=match.group(2),
                         std_error=match.group(3),
                         p_value=match.group(4)))

    return coefficients


def parse_regression(block):
    table_string = find_first_table_in(block)
    parameters = extract_from_stata.model.common.find_parameters_in(block)

    return dict(sample_size=extract_sample_size(table_string),
                number_of_clusters=extract_number_of_clusters(
                                       table_string),
                dependent_variable=extract_dependent_variable(
                                       table_string),
                coefficients=extract_coefficients(
                                 table_string, parameters),
                parameters=parameters)
