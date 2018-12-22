import re


def find_parameters_in(string):
    pattern = re.compile(r"@([a-z0-9_]+)(?:\(([^)]*)\))?")
    parameters = list()

    for line in string.splitlines(True):
        for match in pattern.finditer(line):
            if not match.group(2):
                parameters.append(
                    (match.group(1), None))
            else:
                parameters.append(
                    (match.group(1),
                     tuple(component.strip()
                           for component in match.group(2).split(","))))

    return parameters
