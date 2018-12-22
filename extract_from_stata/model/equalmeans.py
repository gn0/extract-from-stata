import re
import collections

import extract_from_stata.model.common


def is_beginning_of_table(line):
    return (line.startswith("Paired t test")
            or line.startswith("Two-sample t test"))


def param_to_show_test_if_positive(parameters):
    return ("show_test_if_positive"
            in set(param for param, value in parameters))


def param_to_show_test_if_negative(parameters):
    return ("show_test_if_negative"
            in set(param for param, value in parameters))


def param_to_show_test_if_zero(parameters):
    if "show_test_if_zero" in set(param for param, value in parameters):
        return True

    return (not param_to_show_test_if_positive(parameters)
            and not param_to_show_test_if_negative(parameters))


def find_first_table_in(string):
    table_string = ""

    for line in string.splitlines(True):
        if is_beginning_of_table(line):
            table_string += line
        elif table_string:
            table_string += line

            if line.startswith(" Pr(T < t) = "):
                break

    return table_string


def extract_means(table_string):
    pattern = re.compile(r"^ *([A-Za-z0-9_~#.]+) +\| +[0-9]+ +(-?[0-9.e-]+) +([0-9.e-]+) +")

    means = tuple()

    separators = 0

    for line in table_string.splitlines():
        if line.startswith("----"):
            separators += 1
        elif separators == 2:
            match = pattern.match(line)

            if match is None:
                continue

            means += (dict(mean=match.group(2),
                           std_error=match.group(3)),)
        elif separators > 2:
            break

    return means


def is_test_of_two_variables(table_string):
    pattern = re.compile(r"^ *Variable +\| ")

    separators = 0

    for line in table_string.splitlines():
        if line.startswith("----"):
            separators += 1
        elif separators == 1:
            return pattern.match(line) is not None

    return None


def extract_difference_skeleton(table_string, diff_pattern, separator_count):
    separators = 0

    for line in table_string.splitlines():
        if line.startswith("----"):
            separators += 1
        elif separators == separator_count:
            match = diff_pattern.match(line)

            if match is None:
                continue

            return dict(mean=match.group(1),
                        std_error=match.group(2))
        elif separators > separator_count:
            break

    return dict()


def extract_difference_for_test_of_two_variables(table_string):
    return extract_difference_skeleton(
               table_string,
               diff_pattern=re.compile(r"^ *diff +\| +[0-9]+ +(-?[0-9.e-]+) +([0-9.e-]+) +"),
               separator_count=3)


def extract_difference_for_test_of_one_variable_by_group(table_string):
    return extract_difference_skeleton(
               table_string,
               diff_pattern=re.compile(r"^ *diff +\| +(-?[0-9.e-]+) +([0-9.e-]+) +"),
               separator_count=4)


def extract_difference(table_string):
    if is_test_of_two_variables(table_string):
        return extract_difference_for_test_of_two_variables(
                   table_string)
    else:
        return extract_difference_for_test_of_one_variable_by_group(
                   table_string)


def extract_p_value(table_string, parameters):
    pattern = re.compile(r"^ *Pr\(T < t\) = ([0-9.]+) +Pr\(\|T\| > \|t\|\) = ([0-9.]+) +Pr\(T > t\) = ([0-9.]+) *$")

    for line in table_string.splitlines():
        if line.startswith(" Pr(T < t) = "):
            match = pattern.match(line)

            if match is None:
                continue

            if param_to_show_test_if_positive(parameters):
                return match.group(1)
            elif param_to_show_test_if_zero(parameters):
                return match.group(2)
            elif param_to_show_test_if_negative(parameters):
                return match.group(3)

    return None


def parse_equalmeans(block):
    table_string = find_first_table_in(block)
    parameters = extract_from_stata.model.common.find_parameters_in(block)

    return dict(means=extract_means(table_string),
                difference=extract_difference(table_string),
                p_value=extract_p_value(table_string, parameters),
                parameters=parameters)
