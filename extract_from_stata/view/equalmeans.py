import extract_from_stata.view.common


def label_for(table):
    for param, value in table.get("parameters"):
        if param == "label" and len(value) >= 1:
            # FIXME Hack.  Value shouldn't've been split.
            #
            return ", ".join(value)

    return None


def compile_output_table(parsed_tables, mark_significance):
    tags = extract_from_stata.view.common.find_tags_in(parsed_tables)

    output_header = list()
    output_means = list()

    # Header.
    #
    output_header.append([None, "(1)", "(2)", "(1) -- (2)", "p-value"] + tags)

    # Rows.
    #
    for table in parsed_tables:
        output_means.append([label_for(table)]
                            + [m.get("mean")
                               for m in table.get("means")]
                            + [table.get("difference").get("mean")]
                            + [table.get("p_value")])
        output_means.append([None]
                            + ["(%s)" % m.get("std_error")
                               for m in table.get("means")]
                            + ["(%s)" % (table
                                         .get("difference")
                                         .get("std_error"))]
                            + [None])

        if mark_significance:
            p_value = float(table.get("p_value"))

            if p_value <= .01:
                output_means[-2][-2] += "***"
            elif p_value <= .05:
                output_means[-2][-2] += "**"
            elif p_value <= .1:
                output_means[-2][-2] += "*"

        # Tags.
        #
        tags_for_table = extract_from_stata.view.common.tags_from(table.get("parameters"))

        for tag in tags:
            if tag not in tags_for_table:
                output_means[-2].append(None)
            else:
                output_means[-2].append(
                    tags_for_table.get(tag))

    return (output_header,
            output_means,
            list(),
            list())
