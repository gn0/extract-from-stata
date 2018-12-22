import extract_from_stata.view.common


def compile_output_table(parsed_tables, mark_significance):
    variables = extract_from_stata.view.common.find_variables_in(parsed_tables)
    tags = extract_from_stata.view.common.find_tags_in(parsed_tables)

    output_header = list()
    output_coefficients = list()
    output_tags = list()
    output_misc = list()

    # First cells in rows for header.
    #
    output_header.append([None])
    output_header.append([None])

    # First cells in rows for variables and tags.
    #
    for row_name in variables:
        output_coefficients.append([row_name])
        output_coefficients.append([None])

    for row_name in tags:
        output_tags.append([row_name])

    # First cells in rows for miscellaneous stuff.
    #
    output_misc.append(["clusters"])
    output_misc.append(["sample size"])

    # Rest of the cells for each parsed table.
    #
    for k, table in enumerate(parsed_tables, 1):
        # Header.
        #
        output_header[0].append("(%d)" % k)
        output_header[1].append(table.get("dependent_variable"))

        # Variables.
        #
        for pos in xrange(len(variables)):
            i = 2 * pos

            if output_coefficients[i][0] not in table.get("coefficients"):
                output_coefficients[i].append(None)
                output_coefficients[i + 1].append(None)
            else:
                output_coefficients[i].append(
                    table
                    .get("coefficients")
                    .get(output_coefficients[i][0])
                    .get("coefficient"))
                output_coefficients[i + 1].append(
                    "(%s)" % (table
                              .get("coefficients")
                              .get(output_coefficients[i][0])
                              .get("std_error")))

                if mark_significance:
                    p_value = (table
                               .get("coefficients")
                               .get(output_coefficients[i][0])
                               .get("p_value"))

                    if p_value != ".":
                        if float(p_value) <= .01:
                            output_coefficients[i][-1] += "***"
                        elif float(p_value) <= .05:
                            output_coefficients[i][-1] += "**"
                        elif float(p_value) <= .1:
                            output_coefficients[i][-1] += "*"

        # Tags.
        #
        tags_for_table = extract_from_stata.view.common.tags_from(table.get("parameters"))

        for i in xrange(len(tags)):
            if output_tags[i][0] not in tags_for_table:
                output_tags[i].append(None)
            else:
                output_tags[i].append(
                    tags_for_table
                    .get(output_tags[i][0]))

        # Misc.
        #
        output_misc[0].append(table.get("number_of_clusters"))
        output_misc[1].append(table.get("sample_size"))

    return (output_header,
            output_coefficients,
            output_tags,
            output_misc)
