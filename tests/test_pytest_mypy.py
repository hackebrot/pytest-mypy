def test_mypy_success(testdir):
    """Verify that running on a module with no type errors passes."""
    testdir.makepyfile('''
        def myfunc(x: int) -> int:
            return x * 2
    ''')
    result = testdir.runpytest_subprocess()
    result.stdout.fnmatch_lines(['* no tests ran *'])
    assert result.ret != 0
    result = testdir.runpytest_subprocess('--mypy')
    result.stdout.fnmatch_lines(['* 1 passed *'])
    assert result.ret == 0


def test_mypy_error(testdir):
    """Verify that running on a module with type errors fails."""
    testdir.makepyfile('''
        def myfunc(x: int) -> str:
            return x * 2
    ''')

    result = testdir.runpytest_subprocess('--mypy', '-v')

    result.stdout.fnmatch_lines([
        'test_mypy_error.py:2: error: Incompatible return value*',
    ])
    assert result.ret != 0


def test_mypy_ignore_missings_imports(testdir):
    """
    Verify that --mypy-ignore-missing-imports
    causes mypy to ignore missing imports.
    """
    testdir.makepyfile('''
        import pytest_mypy
    ''')
    result = testdir.runpytest_subprocess('--mypy')
    result.stdout.fnmatch_lines([
        '*1: error: Cannot find module named*',
        '* 1 failed *',
    ])
    assert result.ret != 0
    result = testdir.runpytest_subprocess('--mypy-ignore-missing-imports')
    result.stdout.fnmatch_lines(['* 1 passed *'])
    assert result.ret == 0


def test_mypy_marker(testdir):
    """Verify that -m mypy only runs the mypy tests."""
    testdir.makepyfile('''
        def test_fails():
            assert False
    ''')
    result = testdir.runpytest_subprocess('--mypy')
    result.stdout.fnmatch_lines(['* 1 failed, 1 passed *'])
    assert result.ret != 0
    result = testdir.runpytest_subprocess('--mypy', '-m', 'mypy')
    result.stdout.fnmatch_lines(['* 1 passed, 1 deselected *'])
    assert result.ret == 0
