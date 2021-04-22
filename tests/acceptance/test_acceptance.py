import datetime
import sqlite3
import subprocess

import pytest
from digital_land.model.entry import Entry
from digital_land.repository.entry_repository import EntryRepository


@pytest.fixture()
def entry_repository(tmp_path):
    repo_path = str(tmp_path / "test.db")
    repo = EntryRepository(repo_path, create=True)
    today = datetime.date.today().isoformat()
    data = [{"name": "Some Type", "entry-date": today}]
    for idx, d in enumerate(data, start=1):
        repo.add(Entry(dict(d, slug=f"/abc/{idx}"), "abc123", idx))
    return str(repo_path)


def test_view_model(entry_repository, tmp_path):
    """
    EntryRepository in, SQLite3 DB out

    """
    view_db_path = str(tmp_path / "view_test.db")
    command = [
        "view_builder",
        "build",
        "developer-agreement-type",
        entry_repository,
        view_db_path,
    ]
    proc = subprocess.run(command)
    proc.check_returncode()

    con = sqlite3.connect(view_db_path)
    c = con.cursor()
    c.execute("SELECT name FROM category")
    rows = c.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "Some Type"

    c.execute("SELECT slug FROM slug")
    rows = c.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "/abc/1"
