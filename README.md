
# Extract From Stata

This Python package provides a command-line tool to extract regression tables and hypothesis-test results from Stata log files.
It is equipped to translate results into two types of output: csv and tex.

The tool recognizes the following families of Stata tables:

- regressions
- equal-means tests
- hypothesis tests

## Installation

To install this package using pip, type

```
pip install git+https://github.com/gn0/extract-from-stata
```

or, alternatively,

```
git clone https://github.com/gn0/extract-from-stata
pip install ./extract-from-stata
```

## Usage

### Basic function

The tool looks for labels in the Stata log file to know which tables to extract.
The basic labels are:

- `@regression`
- `@hypothesis`
- `@equalmeans`

These should be put in comments so that Stata does not parse them but shows them in the log.
They need to precede the corresponding Stata commands:

```Stata
// @regression
reg y x
```

```Stata
reg y x z

// @hypothesis
lincom x + z
```

```Stata
// @equalmeans
ttest x == z
```

Suppose the Stata log is saved in a file called `stata.log`.
The tool operates on this log file.
To translate all regression tables into csv, type:

```
cat stata.log | extract_from_stata -t regression -c
```

To translate all regression tables into tex:

```
cat stata.log | extract_from_stata -t regression -l
```

To add stars to indicate significance levels:

```
cat stata.log | extract_from_stata -t regression -l -s
```

As is evident from these examples, the tool is designed to fit into the Unix pipeline.
This means that you can combine it with any other tools that operate within the Unix pipeline to modify the Stata log that `extract_from_stata` takes as input, and the csv table that it generates as output.

### Using modifiers for regression output tables

As the default behavior, the constant and categorical variables are suppressed in the output.
They can be brought back by adding the `@show_constant` and the `@show_categoricals` labels after the `@regression` label.

```Stata
// @regression
// @show_constant
reg y x
```

```Stata
// @regression
// @show_categoricals
reg y c.x##i.z
```

### Using identifiers to select which tables to extract

If you want to organize your regression results into separate tables, you can add identifiers to the `@regression`, `@hypothesis`, and `@equalmeans` labels.
For example,

```Stata
// @regression(foo)
reg y x

// @regression(foo)
reg y x, robust

// @regression(bar)
reg y z

// @regression(bar)
reg y z, robust
```

allows you to extract regressions belonging to `foo` and `bar` separately:

```
cat stata.log | extract_from_stata -t regression -i foo -c
cat stata.log | extract_from_stata -t regression -i bar -c
```

## Author

Gabor Nyeki.  Contact information is on http://www.gabornyeki.com/.

## License

This package is licensed under the Creative Commons Attribution 4.0 International License: http://creativecommons.org/licenses/by/4.0/.

