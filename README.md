# whyfail


<img width="960" height="540" alt="whyfail-demo" src="https://github.com/user-attachments/assets/76cd50b2-ff1e-4e8b-91af-fd11f8faa94e" />


**Your test failed. Now what?** `whyfail` runs your tests and tells you, in plain English, why each one broke and how to fix it.

```bash
pip install whyfail
whyfail
```

<!-- Put a 10-second recording here: the red failures, then the explanations appearing. -->

```
✗ test_regular_discount
  Expected 0, but the function returned None
  Why: Nothing was returned on this path, so the value is None.
  Fix: Look for a code path that reaches the end of the function without a `return`.

✗ test_total_with_tax
  Got 29.0, expected 33
  Why: The computed value differs from the expected one.
  Fix: Print the intermediate values in the function, or check the expected value in the test.

✗ test_customer_email
  The key 'email' does not exist
  Why: The dictionary has no entry for this key at that point in the code.
  Fix: Use .get(key, default) if the key is optional, or check that the data really contains it.

3 failure(s) explained, 1 passed
```

You have already stared at a traceback at 11 pm, trying to spot the one line that matters. `whyfail` does that first pass for you.

## What it understands

- `assert None == 0`: the function returned nothing on that path
- `assert 29.0 == 33`: the value you got and the value you expected
- `KeyError`, `IndexError`, `ZeroDivisionError`, `TypeError`
- `AttributeError` on `None` (the most common bug in Python)
- `ModuleNotFoundError`, with the exact `pip install` command
- `FileNotFoundError`, usually a working-directory problem

When it does not recognize an error, it says so and shows the raw message instead of guessing.

## Usage

`whyfail` forwards its arguments to pytest, so everything you already know still works:

```bash
whyfail                       # run the whole suite
whyfail tests/test_api.py     # one file
whyfail -k checkout           # filter by name
whyfail -x                    # stop at the first failure
```

Set `NO_COLOR=1` to disable colors.

## Try it in 30 seconds

```bash
git clone https://github.com/your-handle/whyfail
cd whyfail
pip install -e ".[dev]"
whyfail examples/test_checkout.py
```

`examples/test_checkout.py` contains three real bugs so you can see every kind of explanation.

## How it works

1. Runs `pytest` in a subprocess with a short traceback format.
2. Groups the `E` lines (pytest's error lines) by test.
3. Matches each error against a set of rules, most specific first.
4. Prints the title, the likely cause, and a fix.

The rules live in one file, `whyfail/rules.py`. Adding one takes a regex and a function that returns an `Explanation`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Roadmap

- [ ] `--ai` flag: a longer explanation generated from the failing code
- [ ] Support for `unittest` output
- [ ] More rules, starting with the ones users contribute
- [ ] GitHub Action that comments on pull requests with the explanations

## Contributing

The easiest contribution is a new rule. Add a test in `tests/test_rules.py` first, then the rule. Issues with a failing traceback you would like explained are very welcome.

## License

MIT
