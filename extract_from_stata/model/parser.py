import re

import extract_from_stata.model.regressions
import extract_from_stata.model.hypotheses
import extract_from_stata.model.equalmeans
import extract_from_stata.model.tabulations


def blocks_in(stata_log):
    pattern = re.compile(r"@(regression|hypothesis|equalmeans|tabulation)")

    starting_positions = tuple(match.start()
                               for match in pattern.finditer(stata_log))

    for start_pos, end_pos in zip(starting_positions,
                                  starting_positions[1:] + (None,)):
        yield stata_log[start_pos:end_pos]


def parse_block(extraction_type, block):
    if extraction_type == "regression":
        return extract_from_stata.model.regressions.parse_regression(block)
    elif extraction_type == "hypothesis":
        return extract_from_stata.model.hypotheses.parse_hypothesis(block)
    elif extraction_type == "equalmeans":
        return extract_from_stata.model.equalmeans.parse_equalmeans(block)
    elif extraction_type == "tabulation":
        return extract_from_stata.model.tabulations.parse_tabulation(block)


def parse_stata_log(stata_log, extraction_type, extraction_id):
    if extraction_id is None:
        start_string = "@%s" % extraction_type
    else:
        start_string = "@%s(%s)" % (extraction_type, extraction_id)

    parsed_tables = (
        tuple(parse_block(extraction_type, block)
              for block in blocks_in(stata_log)
              if block.startswith(start_string)))

    return parsed_tables
