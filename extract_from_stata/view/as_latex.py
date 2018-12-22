import re

import extract_from_stata.view.common


def latex_escape(string):
    if string is None:
        return ""

    return (string
            .replace("_", r"\_")
            .replace("~", r"\~")
            .replace("#", r"\#")
            .replace("&", r"\&"))


def latex_numbers_to_math_mode(string):
    if string is None:
        return ""

    pattern = re.compile(r"(-?[0-9.]+)")

    return pattern.sub(r"$\1$", string)


def add_commas_to_numbers(string):
    if string is None:
        return ""

    pattern = re.compile(r"(-?(?:\d+[.]\d*|\d*[.]\d+|\d+))")

    retval = ""
    for k, chunk in enumerate(pattern.split(string)):
        if k % 2 == 0:
            retval += chunk
        else:
            dp_position = chunk.find(".")

            if dp_position == -1:
                dp_position = len(chunk)

            if chunk[:dp_position] in ("", "-"):
                retval += chunk
            else:
                retval += "{:,d}".format(int(chunk[:dp_position]))
                retval += chunk[dp_position:]

    return retval


assert (add_commas_to_numbers("foo -.34 12345 -12345.6789")
        == "foo -.34 12,345 -12,345.6789")


def make_latex_table(header, coefficients, tags, misc):
    code = ""

    code += (r"\begin{tabular}{l%s}" % ("c" * (len(header[0]) - 1))
             + "\n")
    code += r"    \toprule" + "\n"

    for row in header:
        code += (r"    "
                 + " & ".join(latex_escape(value) for value in row)
                 + r" \\"
                 + "\n")

    code += r"    \midrule" + "\n"

    for row in coefficients:
        code += (r"    "
                 + latex_escape(row[0])
                 + " & "
                 + " & ".join(latex_numbers_to_math_mode(value)
                              for value in row[1:])
                 + r" \\"
                 + "\n")

    code += r"    \midrule" + "\n"

    for row in tags:
        code += (r"    "
                 + latex_escape(row[0])
                 + " & "
                 + " & ".join(latex_escape(value)
                              for value in row[1:])
                 + r" \\"
                 + "\n")

    code += r"    \midrule" + "\n"

    for row in misc:
        code += (r"    "
                 + latex_escape(row[0])
                 + " & "
                 + " & ".join(latex_escape(
                                  add_commas_to_numbers(value))
                              for value in row[1:])
                 + r" \\"
                 + "\n")

    code += r"    \bottomrule" + "\n"
    code += r"\end{tabular}"

    return code


def print_as_latex_table(output_table):
    print make_latex_table(*output_table)
