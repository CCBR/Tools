from ccbr_tools.pipeline.hpc import get_hpcname


def test_hpcname_type():
    hpcname = get_hpcname()
    assert isinstance(hpcname, str), "Expected hpcname to be a string"


def test_hpcname_expected_values():
    hpcname = get_hpcname().strip().lower()
    if hpcname:
        assert hpcname in ["biowulf", "frce", "helix"], f"Unexpected hpcname: {hpcname}"


def test_hpcname_print_output():
    import io
    import sys

    captured = io.StringIO()
    sys.stdout = captured
    print(get_hpcname())
    sys.stdout = sys.__stdout__

    printed = captured.getvalue().strip()
    expected = get_hpcname().strip()
    assert printed == expected, f"Printed output '{printed}' != return value '{expected}'"


if __name__ == "__main__":
    test_hpcname_type()
    test_hpcname_expected_values()
    test_hpcname_print_output()
    print("All tests passed.")