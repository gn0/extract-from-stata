import collections

import extract_from_stata.view.common


# FIXME This whole function is part of a bit of an ugly hack.
# This boils down to how to transform individual hypothesis
# tables in the Stata log into composite output tables that pre-
# ferably match the column layout of regression tables.  The al-
# ternative is to be explicit about which column each hypothesis
# table should be sorted into.  This would require always adding
# parameters like @column(1), @column(2), etc., to Stata output.
#
def coalesce(parsed_tables):
    coalesced_tables = tuple()
    this_table = None

    for test in parsed_tables:
        if (this_table is not None
            and (this_table.get("dependent_variable")
                 != test.get("dependent_variable")
                 or this_table.get("coefficients").keys()[0]
                    in test.get("coefficients"))):
            coalesced_tables += (this_table,)
            this_table = None

        if this_table is None:
            this_table = test
            this_table["coefficients"] = collections.OrderedDict(
                                             this_table.get("coefficients"))
        else:
            this_table["coefficients"].update(
                        test.get("coefficients"))

    if this_table is not None:
        coalesced_tables += (this_table,)

    return coalesced_tables


def compile_output_table(parsed_tables, mark_significance):
    coalesced_tables = coalesce(parsed_tables)

    variables = extract_from_stata.view.common.find_variables_in(coalesced_tables)
    tags = extract_from_stata.view.common.find_tags_in(coalesced_tables)

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
        output_coefficients.append([None])

    for row_name in tags:
        output_tags.append([row_name])

    # Rest of the cells for each parsed table.
    #
    for k, table in enumerate(coalesced_tables, 1):
        # Header.
        #
        output_header[0].append("(%d)" % k)
        output_header[1].append(table.get("dependent_variable"))

        # Variables.
        #
        for pos in xrange(len(variables)):
            i = 3 * pos

            if output_coefficients[i][0] not in table.get("coefficients"):
                output_coefficients[i].append(None)
                output_coefficients[i + 1].append(None)
                output_coefficients[i + 2].append(None)
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
                output_coefficients[i + 2].append(
                    "[%s]" % (table
                              .get("coefficients")
                              .get(output_coefficients[i][0])
                              .get("p_value")))

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

    return (output_header,
            output_coefficients,
            output_tags,
            output_misc)
