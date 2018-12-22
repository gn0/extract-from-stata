import argh
import sys

import extract_from_stata.model.parser

import extract_from_stata.view.regressions
import extract_from_stata.view.hypotheses
import extract_from_stata.view.equalmeans
import extract_from_stata.view.tabulations
import extract_from_stata.view.as_csv
import extract_from_stata.view.as_latex


@argh.arg("--extraction-type", "-t", required=True, choices=("regression", "hypothesis", "equalmeans", "tabulation"))
@argh.arg("--extraction-id", "-i", required=False)
@argh.arg("--view-as-csv", "-c", required=False)
@argh.arg("--view-as-latex", "-l", required=False)
@argh.arg("--mark-significance", "-s", required=False)
def dispatcher(extraction_type=None,
               extraction_id=None,
               view_as_csv=False,
               view_as_latex=False,
               mark_significance=False):
    if not view_as_csv and not view_as_latex:
        print >> sys.stderr, (
           "error: Must specify either --view-as-csv or --view-as-latex.")
        sys.exit(1)

    parsed_tables = (
        extract_from_stata.model.parser.parse_stata_log(
            stata_log=sys.stdin.read(),
            extraction_type=extraction_type,
            extraction_id=extraction_id))

    if extraction_type == "regression":
        extraction_view = extract_from_stata.view.regressions
    elif extraction_type == "hypothesis":
        extraction_view = extract_from_stata.view.hypotheses
    elif extraction_type == "equalmeans":
        extraction_view = extract_from_stata.view.equalmeans
    elif extraction_type == "tabulation":
        extraction_view = extract_from_stata.view.tabulations

    if view_as_csv:
        extract_from_stata.view.as_csv.print_as_csv(
                extraction_view.compile_output_table(
                        parsed_tables, mark_significance))
    elif view_as_latex:
        extract_from_stata.view.as_latex.print_as_latex_table(
                extraction_view.compile_output_table(
                        parsed_tables, mark_significance))


def main():
    argh.dispatch_command(dispatcher)


if __name__ == "__main__":
    main()
