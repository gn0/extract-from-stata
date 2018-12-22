

def find_variables_in(parsed_tables):
    variables = list()

    for table in parsed_tables:
        for var in table.get("coefficients"):
            if var not in variables:
                variables.append(var)

    return variables


def find_tags_in(parsed_tables):
    tags = list()

    for table in parsed_tables:
        for param, value in table.get("parameters"):
            if param == "tag" and len(value) == 2:
                if value[0] not in tags:
                    tags.append(value[0])

    return tags


def tags_from(parameters):
    return dict(value
                for param, value in parameters
                if param == "tag" and len(value) == 2)
