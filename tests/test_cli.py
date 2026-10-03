"""
Tests for Hermes Meeting CLI Commands.
"""

import os
import tempfile
from unittest.mock import patch

from hermes_meeting_intelligence.cli import main


def test_cli_validate(sample_meeting_json_path, capsys):
    test_args = ["hermes-meeting", "validate", sample_meeting_json_path]
    with patch("sys.argv", test_args):
        main()
    captured = capsys.readouterr()
    assert "is a valid MeetingRecord" in captured.out


def test_cli_ingest_and_query(capsys):
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt") as tf:
        tf.write(
            "[Alice]: We decided to use SQLite for memory.\n[Bob]: Bob will finish the CI by Friday."
        )
        tf_path = tf.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite") as db_f:
        db_path = db_f.name

    try:
        # Ingest
        ingest_args = [
            "hermes-meeting",
            "--db",
            db_path,
            "ingest",
            tf_path,
            "--title",
            "CLI Sync Meeting",
        ]
        with patch("sys.argv", ingest_args):
            main()
        captured = capsys.readouterr()
        assert "Ingested meeting 'CLI Sync Meeting'" in captured.out

        # Query decisions
        query_args = ["hermes-meeting", "--db", db_path, "query", "decisions", "SQLite"]
        with patch("sys.argv", query_args):
            main()
        captured = capsys.readouterr()
        assert "Found 1 decision(s)" in captured.out

        # List
        list_args = ["hermes-meeting", "--db", db_path, "list"]
        with patch("sys.argv", list_args):
            main()
        captured = capsys.readouterr()
        assert "Stored Meetings (1)" in captured.out
    finally:
        if os.path.exists(tf_path):
            os.remove(tf_path)
        if os.path.exists(db_path):
            os.remove(db_path)
