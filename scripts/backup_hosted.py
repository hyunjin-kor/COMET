"""Private SQLite backup/verification and restore to a new, unused directory."""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.services.hosted_access import storage_root  # noqa: E402


def private_path(value):
    path = Path(value)
    source = Path(__file__).resolve().parents[1]
    if not path.is_absolute() or path.resolve() != path.absolute():
        raise ValueError('Use an absolute private path without redirected components')
    path = path.resolve()
    if path == Path(path.anchor) or path.is_relative_to(source) or source.is_relative_to(path):
        raise ValueError('Backup and recovery directories must be outside the source tree')
    return path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def connect_readonly(path):
    if not path.is_file() or path.is_symlink():
        raise ValueError('Missing or redirected private database')
    return sqlite3.connect(f'file:{path.as_posix()}?mode=ro', uri=True)


def check_database(path):
    with connect_readonly(path) as connection:
        if connection.execute('PRAGMA quick_check').fetchall() != [('ok',)]:
            raise ValueError('SQLite integrity check failed')


def database_names(root):
    with connect_readonly(root / 'control.db') as connection:
        ids = [row[0] for row in connection.execute('SELECT id FROM hosted_accounts ORDER BY id')]
    if any(not re.fullmatch(r'[0-9a-f]{32}', value) for value in ids):
        raise ValueError('Invalid server account identifier in control database')
    return ['control.db', *[f'accounts/{value}.db' for value in ids]]


def copy_database(source, destination):
    if destination.exists():
        raise ValueError('Never overwrite an existing database')
    check_database(source)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with connect_readonly(source) as origin, sqlite3.connect(destination) as target:
        origin.backup(target)
    check_database(destination)


def create_backup(destination):
    root, target = private_path(storage_root()), private_path(destination)
    if target.is_relative_to(root) or root.is_relative_to(target) or target.exists():
        raise ValueError('Use a new backup directory separate from service storage')
    names = database_names(root)
    target.mkdir(parents=True, mode=0o700)
    records = []
    for name in names:
        copy_database(root / name, target / name)
        records.append({'file': name, 'sha256': digest(target / name)})
    manifest = {'schema': 1, 'created_at': datetime.now(UTC).isoformat(), 'requires_quiesced_service': True,
                'databases': records, 'scope': 'control and all account databases; not host configuration or bundled data'}
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    verify_backup(target)
    return manifest


def verify_backup(directory):
    root = private_path(directory)
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema') != 1 or not isinstance(manifest.get('databases'), list):
        raise ValueError('Unknown backup format')
    names = []
    for record in manifest['databases']:
        name = record.get('file', '')
        if not re.fullmatch(r'(control\.db|accounts/[0-9a-f]{32}\.db)', name) or name in names:
            raise ValueError('Invalid or duplicate backup database path')
        names.append(name)
        path = root / name
        if path.resolve() != path.absolute() or digest(path) != record.get('sha256'):
            raise ValueError('Backup hash or path verification failed')
        check_database(path)
    if sorted(names) != sorted(database_names(root)):
        raise ValueError('Backup does not contain every account database')
    return manifest


def restore_backup(directory, destination):
    source, target = private_path(directory), private_path(destination)
    manifest = verify_backup(source)
    if target.exists() or target.is_relative_to(source) or source.is_relative_to(target):
        raise ValueError('Restore requires a new directory; active storage is never overwritten')
    target.mkdir(parents=True, mode=0o700)
    for record in manifest['databases']:
        copy_database(source / record['file'], target / record['file'])
    # Restoring a historic control DB must not resurrect old browser credentials.
    with sqlite3.connect(target / 'control.db') as connection:
        connection.execute('DELETE FROM hosted_login_sessions')
    check_database(target / 'control.db')
    report = {'source_manifest_sha256': digest(source / 'manifest.json'), 'restored_at': datetime.now(UTC).isoformat(),
              'sessions_revoked': True, 'databases': [{'file': row['file'], 'sha256': digest(target / row['file'])} for row in manifest['databases']]}
    (target / 'recovery-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    backup = sub.add_parser('backup')
    backup.add_argument('destination')
    backup.add_argument('--service-stopped', action='store_true', required=True, help='Confirm all service workers and operator writes have stopped')
    sub.add_parser('verify').add_argument('directory')
    restore = sub.add_parser('restore')
    restore.add_argument('directory')
    restore.add_argument('destination')
    restore.add_argument('--service-stopped', action='store_true', required=True)
    args = parser.parse_args()
    try:
        result = (create_backup(args.destination) if args.action == 'backup' else
                  verify_backup(args.directory) if args.action == 'verify' else restore_backup(args.directory, args.destination))
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f'Backup/recovery failed: {exc}\n')


if __name__ == '__main__':
    main()
