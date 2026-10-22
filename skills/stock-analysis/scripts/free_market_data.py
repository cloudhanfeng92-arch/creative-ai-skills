#!/usr/bin/env python3
"""Account-free stock research data: AKShare for CN, yfinance for HK/US."""
from __future__ import annotations
import argparse
import contextlib
from datetime import datetime, timezone
from importlib.util import find_spec
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

RUNTIME = Path.home() / '.local' / 'share' / 'stock-analysis' / 'venv'
PACKAGES = ('akshare', 'yfinance')


def runtime_python():
    candidate = RUNTIME / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    return str(candidate) if candidate.is_file() else sys.executable


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    subs = p.add_subparsers(dest='command', required=True)
    subs.add_parser('doctor', help='Check local libraries without a data network request')
    for command in ('quote', 'daily', 'financials'):
        q = subs.add_parser(command)
        q.add_argument('--market', required=True, choices=('CN', 'HK', 'US'))
        q.add_argument('--symbol', required=True, help='600519.SH / 00700.HK / AAPL / BRK-B; resolve names first')
        q.add_argument('--timeout', type=int, default=45, help='Whole request timeout, 5–90 seconds')
        q.add_argument('--max-rows', type=int, default=1500, help='Output limit, 1–5000; truncation is explicit')
        if command == 'daily':
            q.add_argument('--start', required=True, help='YYYYMMDD, inclusive')
            q.add_argument('--end', required=True, help='YYYYMMDD, inclusive')
            q.add_argument('--adjust', choices=('none', 'qfq', 'hfq'), default='none')
        if command == 'financials':
            q.add_argument('--statement', required=True, choices=('income', 'balancesheet', 'cashflow'))
            q.add_argument('--period', help='Optional exact report end date YYYYMMDD')
            q.add_argument('--frequency', choices=('annual', 'quarterly'), default='quarterly')
    return p


def validate(args):
    patterns = {'CN': r'(?:6[0-9]{5}\.SH|[03][0-9]{5}\.SZ|[489][0-9]{5}\.BJ)',
                'HK': r'[0-9]{4,5}\.HK', 'US': r'[A-Z][A-Z0-9]{0,9}(?:-[A-Z0-9]{1,4})?'}
    if not re.fullmatch(patterns[args.market], args.symbol):
        raise ValueError('Symbol format does not match market; use CN/HK exchange suffixes or Yahoo US symbols such as BRK-B.')
    if args.market == 'HK' and int(args.symbol.split('.')[0]) == 0:
        raise ValueError('HK stock code cannot be zero.')
    if not 5 <= args.timeout <= 90 or not 1 <= args.max_rows <= 5000:
        raise ValueError('Timeout or row limit is outside the supported range.')
    for name in ('start', 'end', 'period'):
        value = getattr(args, name, None)
        if value:
            if not re.fullmatch(r'[0-9]{8}', value):
                raise ValueError('Dates must be YYYYMMDD.')
            datetime.strptime(value, '%Y%m%d')
    if args.command == 'daily':
        if args.start > args.end:
            raise ValueError('Start date must not be after end date.')
        if args.market != 'CN' and args.adjust != 'none':
            raise ValueError('HK/US supports none only; Yahoo adjustment is not CN qfq/hfq.')


def doctor():
    from importlib import metadata
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = metadata.version(package) if find_spec(package) else None
        except metadata.PackageNotFoundError:
            versions[package] = None
    return {'status': 'ok' if all(versions.values()) and sys.version_info >= (3, 11) else 'dependency_missing',
            'python': sys.executable, 'python_version': sys.version.split()[0], 'packages': versions,
            'credentials_required': False, 'network_data_tested': False,
            'setup': 'Run scripts/setup_free_data.py using Python 3.11+; no API keys required.'}


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    if hasattr(value, 'item'):
        return clean(value.item())
    return str(value)


def bound_lists(value, limit, paths=None, path='$', keep_head=False):
    if paths is None:
        paths = []
    if isinstance(value, dict):
        return {k: bound_lists(v, limit, paths, path + '.' + k, keep_head) for k, v in value.items()}
    if isinstance(value, list):
        # Only row arrays are bounded. Column names, limitations and nested values
        # are metadata; truncating them corrupts the meaning of retained rows.
        row_paths = {'$.data', '$.records', '$.raw.records', '$.normalized'}
        if not keep_head:
            row_paths.update({'$.raw.rows', '$.raw.history'})
        if path in row_paths and len(value) > limit:
            paths.append({'path': path, 'original_count': len(value), 'kept': limit})
            value = value[:limit] if keep_head else value[-limit:]
        return [bound_lists(v, limit, paths, path + '[]', keep_head) for v in value]
    return value


def request(args):
    provider_name = 'akshare' if args.market == 'CN' else 'yfinance'
    if find_spec(provider_name) is None:
        return {'status': 'dependency_missing', 'provider': provider_name,
                'message': 'Run scripts/setup_free_data.py once. No account or data token is needed.'}
    # Third-party progress/logging never interleaves with the single JSON result.
    with open(os.devnull, 'w') as sink, contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        if args.market == 'CN':
            from providers import akshare_provider as provider
        else:
            from providers import yfinance_provider as provider
        if args.command == 'quote':
            result = provider.quote(args.symbol)
        elif args.command == 'daily':
            result = provider.daily(args.symbol, args.start, args.end, args.adjust)
        else:
            result = provider.financials(args.symbol, args.statement, args.period, args.frequency)
    if not isinstance(result, dict) or not isinstance(result.get('status'), str):
        return {'status': 'protocol_error', 'provider': provider_name}
    result = clean(result)
    result.update(market=args.market, requested_symbol=args.symbol, operation=args.command, credentials_required=False)
    result.setdefault('fetched_at', datetime.now(timezone.utc).isoformat())
    truncated = []
    result = bound_lists(result, args.max_rows, truncated, keep_head=args.command == 'financials')
    if truncated:
        result['truncation'] = truncated
        result['limitations'] = result.get('limitations', []) + ['Output was truncated; do not treat it as a complete history or report.']
        if result['status'] == 'ok':
            result['status'] = 'partial'
    if args.command == 'quote':
        from quote_check import check_quote, InputError
        result['metadata_checks'] = []
        for row in result.get('normalized', []):
            row.setdefault('fetched_at', result['fetched_at'])
            try:
                assessment = check_quote(row, now=datetime.now(timezone.utc).isoformat(), max_age_seconds=120)
                assessment['notice'] += ' The 120 second threshold is a diagnostic default, not proof of real-time suitability.'
                result['metadata_checks'].append(assessment)
            except InputError as exc:
                result['metadata_checks'].append({'real_time_usable': False, 'use_class': 'incomplete_metadata', 'reason': str(exc)})
    return result


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parser().parse_args(argv)
    try:
        if args.command != 'doctor':
            validate(args)
        if args.worker:
            result = doctor() if args.command == 'doctor' else request(args)
        else:
            timeout = 15 if args.command == 'doctor' else args.timeout
            process = subprocess.run([runtime_python(), '-B', str(Path(__file__).resolve()), '--worker', *argv],
                                     capture_output=True, text=True, timeout=timeout)
            if len(process.stdout) > 2_000_000:
                result = {'status': 'response_too_large', 'message': 'Request a shorter date range.'}
            else:
                try:
                    result = json.loads(process.stdout)
                except ValueError:
                    result = {'status': 'worker_error', 'message': 'Data worker returned no valid JSON; no vendor logs are echoed.'}
    except subprocess.TimeoutExpired:
        result = {'status': 'timeout', 'message': 'Request exceeded its time budget; no stale result substituted.'}
    except ValueError as exc:
        result = {'status': 'invalid_input', 'message': str(exc)}
    except Exception as exc:
        result = {'status': 'provider_error', 'error_type': type(exc).__name__}
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))
    return 0 if result.get('status') in ('ok', 'partial') else 2


if __name__ == '__main__':
    sys.exit(main())
