"""Backups preserve private records and never overwrite active storage."""

import json
import sqlite3

import pytest

from backend.services import hosted_access as hosted
from backend.tests.test_api import _save_estimate
from backend.tests.test_hosted_access import HEADERS, login
from backend.tests.test_hosted_access import hosted_client as _hosted_client_fixture
from scripts.backup_hosted import create_backup, digest, restore_backup, verify_backup

hosted_client = _hosted_client_fixture


def test_backup_restore_retains_estimates_and_revokes_sessions(hosted_client, tmp_path):
    client, first, second = hosted_client
    login(client)
    client.headers.update(HEADERS)
    estimate_id = _save_estimate(client, 'Synthetic recovery evidence').json()['id']
    root = hosted.storage_root()
    original = {name: digest(root / name) for name in ['control.db', f'accounts/{first.id}.db', f'accounts/{second.id}.db']}
    # No requests/writers run while the snapshot is copied, matching the CLI precondition.
    backup = tmp_path.parent / (tmp_path.name + '-backup')
    restored = tmp_path.parent / (tmp_path.name + '-recovered')
    assert len(create_backup(backup)['databases']) == 3
    assert verify_backup(backup)['schema'] == 1
    report = restore_backup(backup, restored)
    assert report['sessions_revoked']
    with sqlite3.connect(restored / 'control.db') as connection:
        assert connection.execute('SELECT count(*) FROM hosted_login_sessions').fetchone()[0] == 0
        assert connection.execute('SELECT count(*) FROM hosted_accounts').fetchone()[0] == 2
    with sqlite3.connect(restored / f'accounts/{first.id}.db') as connection:
        assert connection.execute('SELECT name FROM estimates WHERE id=?', (estimate_id,)).fetchone()[0] == 'Synthetic recovery evidence'
    assert original == {name: digest(root / name) for name in original}
    with pytest.raises(ValueError, match='new directory'):
        restore_backup(backup, root)
    with pytest.raises(ValueError):
        create_backup(root / 'nested-backup')


@pytest.mark.parametrize('corruption', ['hash', 'missing', 'traversal', 'duplicate'])
def test_corrupt_or_incomplete_backup_is_rejected_before_restore(hosted_client, tmp_path, corruption):
    _, _, _ = hosted_client
    backup = tmp_path.parent / (tmp_path.name + '-backup')
    create_backup(backup)
    manifest_path = backup / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if corruption == 'hash':
        manifest['databases'][0]['sha256'] = '0' * 64
    elif corruption == 'missing':
        manifest['databases'].pop()
    elif corruption == 'traversal':
        manifest['databases'][0]['file'] = '../control.db'
    else:
        manifest['databases'].append(manifest['databases'][0])
    manifest_path.write_text(json.dumps(manifest))
    target = tmp_path.parent / (tmp_path.name + '-never-created')
    with pytest.raises(ValueError):
        restore_backup(backup, target)
    assert not target.exists()
