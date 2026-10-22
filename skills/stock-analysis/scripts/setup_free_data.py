#!/usr/bin/env python3
"""Install public data libraries in a private virtualenv; no data account needed."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


DEFAULT_RUNTIME = Path.home() / '.local' / 'share' / 'stock-analysis' / 'venv'


def find_python(explicit=None):
    candidates = [explicit] if explicit else [sys.executable] + [shutil.which('python3.' + str(v)) for v in (14, 13, 12, 11)]
    for candidate in candidates:
        if not candidate:
            continue
        try:
            check = subprocess.run([candidate, '-c', 'import sys; print(int(sys.version_info >= (3,11)))'],
                                   capture_output=True, text=True, timeout=5)
            if check.returncode == 0 and check.stdout.strip() == '1':
                return candidate
        except (OSError, subprocess.TimeoutExpired):
            pass
    raise ValueError('Python 3.11+ is required. Use a host-provided interpreter with --python PATH.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python', help='Optional existing Python 3.11+ interpreter')
    parser.add_argument('--index-url', choices=('https://pypi.org/simple', 'https://mirrors.aliyun.com/pypi/simple/'),
                        default='https://pypi.org/simple', help='Explicit public package index; default official PyPI')
    args = parser.parse_args(argv)
    runtime = DEFAULT_RUNTIME.expanduser().resolve()
    try:
        python = find_python(args.python)
        if runtime.exists() and not (runtime / 'pyvenv.cfg').is_file():
            raise ValueError('Runtime path exists but is not a virtualenv; choose a dedicated directory.')
        if not runtime.exists():
            runtime.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run([python, '-m', 'venv', str(runtime)], check=True, capture_output=True, timeout=90)
        executable = runtime / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        find_python(str(executable))
        requirements = Path(__file__).resolve().parent.parent / 'assets/requirements-free.txt'
        command = [str(executable), '-m', 'pip', '--isolated', 'install', '--disable-pip-version-check',
                   '--index-url', args.index_url, '--timeout', '15', '--retries', '1', '-r', str(requirements)]
        installed = subprocess.run(command, capture_output=True, text=True, timeout=300)
        if installed.returncode:
            # Dependency diagnostics may contain proxy settings; return no raw installer logs.
            raise ValueError('Package installation failed; check network/index access. No credentials are needed. Existing runtime is preserved.')
        check = subprocess.run([str(executable), '-c',
                                'import importlib.metadata as m; import akshare, yfinance; import json; '
                                'print(json.dumps({p:m.version(p) for p in ("akshare","yfinance")}))'],
                               capture_output=True, text=True, timeout=45)
        if check.returncode:
            raise ValueError('Packages were installed but imports failed; runtime is not ready.')
        print(json.dumps({'status': 'ok', 'python': str(executable), 'versions': json.loads(check.stdout),
                          'credentials_required': False, 'network_data_tested': False}))
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        message = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(json.dumps({'status': 'setup_failed', 'message': message}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
