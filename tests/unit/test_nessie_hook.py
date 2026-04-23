from __future__ import annotations

from plugins.hooks.nessie_hook import NessieReference, branch_url, commit_url


def test_branch_url():
    ref = NessieReference(name="main")
    assert branch_url("http://nessie:19120", ref) == "http://nessie:19120/api/v2/trees/branch/main"


def test_commit_url_includes_hash_when_present():
    ref = NessieReference(name="main", hash="abcd1234")
    assert commit_url("http://nessie", ref) == "http://nessie/api/v2/trees/main@abcd1234/history"


def test_commit_url_without_hash():
    ref = NessieReference(name="dev")
    assert commit_url("http://nessie", ref).endswith("/trees/dev/history")
