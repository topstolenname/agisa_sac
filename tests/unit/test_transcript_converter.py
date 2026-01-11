"""Tests for transcript converter."""

import json
from pathlib import Path

import pytest

from agisa_sac.auditing import (
    load_transcript,
    transcript_to_artifact,
    write_context_blob,
)


@pytest.fixture
def minimal_transcript_file(tmp_path):
    """Create a minimal transcript JSON file."""
    transcript = {
        "meta": {"source": "test"},
        "turns": [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you!"},
        ],
    }
    file_path = tmp_path / "transcript.json"
    with open(file_path, "w") as f:
        json.dump(transcript, f)
    return file_path


@pytest.fixture
def transcript_without_meta(tmp_path):
    """Create a transcript without meta field."""
    transcript = {
        "turns": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"},
            {"role": "assistant", "content": "4"},
        ],
    }
    file_path = tmp_path / "transcript_no_meta.json"
    with open(file_path, "w") as f:
        json.dump(transcript, f)
    return file_path


def test_load_transcript_minimal(minimal_transcript_file):
    """Test loading a minimal transcript."""
    transcript = load_transcript(minimal_transcript_file)

    assert "meta" in transcript
    assert "turns" in transcript
    assert len(transcript["turns"]) == 2
    assert transcript["turns"][0]["role"] == "user"
    assert transcript["turns"][0]["content"] == "Hello, how are you?"


def test_load_transcript_without_meta(transcript_without_meta):
    """Test loading a transcript without meta field."""
    transcript = load_transcript(transcript_without_meta)

    assert transcript["meta"] is None
    assert len(transcript["turns"]) == 3


def test_load_transcript_not_found():
    """Test loading a non-existent transcript."""
    with pytest.raises(FileNotFoundError):
        load_transcript(Path("/nonexistent/transcript.json"))


def test_load_transcript_invalid_json(tmp_path):
    """Test loading an invalid JSON file."""
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        f.write("not valid json {")

    with pytest.raises(json.JSONDecodeError):
        load_transcript(file_path)


def test_load_transcript_not_dict(tmp_path):
    """Test loading a transcript that is not a JSON object."""
    file_path = tmp_path / "not_dict.json"
    with open(file_path, "w") as f:
        json.dump(["this", "is", "a", "list"], f)

    with pytest.raises(ValueError, match="Transcript must be a JSON object"):
        load_transcript(file_path)


def test_load_transcript_missing_turns(tmp_path):
    """Test loading a transcript without turns field."""
    file_path = tmp_path / "no_turns.json"
    with open(file_path, "w") as f:
        json.dump({"meta": {}}, f)

    with pytest.raises(ValueError, match="must contain 'turns' field"):
        load_transcript(file_path)


def test_load_transcript_turns_not_list(tmp_path):
    """Test loading a transcript where 'turns' is not a list."""
    file_path = tmp_path / "turns_not_list.json"
    with open(file_path, "w") as f:
        json.dump({"turns": "should be a list"}, f)

    with pytest.raises(ValueError, match="'turns' field must be a list"):
        load_transcript(file_path)


def test_load_transcript_turn_not_dict(tmp_path):
    """Test loading a transcript with a turn that is not a dictionary."""
    file_path = tmp_path / "turn_not_dict.json"
    with open(file_path, "w") as f:
        json.dump({"turns": ["string instead of dict"]}, f)

    with pytest.raises(ValueError, match="Turn 0 must be a dictionary"):
        load_transcript(file_path)


def test_load_transcript_invalid_turn(tmp_path):
    """Test loading a transcript with invalid turn structure."""
    file_path = tmp_path / "invalid_turn.json"
    with open(file_path, "w") as f:
        json.dump({"turns": [{"role": "user"}]}, f)  # Missing content

    with pytest.raises(ValueError, match="must have 'role' and 'content' fields"):
        load_transcript(file_path)


def test_transcript_to_artifact_auto_name(minimal_transcript_file):
    """Test converting transcript to artifact with auto-generated name."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript)

    assert artifact["kind"] == "auditor_artifact_v1"
    assert "name" in artifact
    assert artifact["name"]  # Should not be empty
    # Name should be derived from meta.source, not transcript content
    assert artifact["name"].startswith("test_")
    assert artifact["marker"] == f"ARTIFACT::{artifact['name']}"
    assert "created_at_unix" in artifact
    assert artifact["meta"] == {"source": "test"}
    assert len(artifact["transcript"]["turns"]) == 2


def test_transcript_to_artifact_custom_name(minimal_transcript_file):
    """Test converting transcript with custom name."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript, name="my_custom_name")

    assert artifact["name"] == "my_custom_name"
    assert artifact["marker"] == "ARTIFACT::my_custom_name"


def test_transcript_to_artifact_custom_marker(minimal_transcript_file):
    """Test converting transcript with custom marker."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(
        transcript, name="test", marker="CUSTOM_MARKER::test"
    )

    assert artifact["name"] == "test"
    assert artifact["marker"] == "CUSTOM_MARKER::test"


def test_transcript_to_artifact_text_formatting(minimal_transcript_file):
    """Test artifact text formatting."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript)

    expected_text = (
        "USER: Hello, how are you?\n" "ASSISTANT: I'm doing well, thank you!"
    )
    assert artifact["transcript"]["artifact_text"] == expected_text


def test_transcript_to_artifact_slugification(tmp_path):
    """Test that names are properly slugified."""
    transcript = {
        "meta": {"source": "Test Source!", "run_id": "Run@123#"},
        "turns": [{"role": "user", "content": "This Has Spaces and Special! Chars@#$"}],
    }
    artifact = transcript_to_artifact(transcript)

    # Name should be slugified (lowercase, no special chars)
    assert artifact["name"].islower()
    assert " " not in artifact["name"]
    assert "@" not in artifact["name"]
    assert "#" not in artifact["name"]
    # Should use meta fields, not content
    assert "test_source" in artifact["name"]
    assert "run" in artifact["name"]


def test_write_context_blob(minimal_transcript_file, tmp_path):
    """Test writing context blob to file."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript, name="test_artifact")

    out_path = tmp_path / "context_blob.json"
    result_path = write_context_blob(
        base_context=None,
        artifact=artifact,
        out_path=out_path,
        target_epoch=5,
        exposure_rate=0.2,
    )

    assert result_path == out_path
    assert out_path.exists()

    # Verify content
    with open(out_path) as f:
        blob = json.load(f)

    assert "auditor_artifact" in blob
    assert blob["auditor_artifact"]["name"] == "test_artifact"
    assert "auditor_policy" in blob
    assert blob["auditor_policy"]["target_epoch"] == 5
    assert blob["auditor_policy"]["exposure_rate"] == 0.2
    assert blob["auditor_policy"]["mode"] == "memory_seed"


def test_write_context_blob_with_base_context(minimal_transcript_file, tmp_path):
    """Test writing context blob with base context."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript)

    base_context = {"existing_key": "existing_value", "another_key": 123}

    out_path = tmp_path / "context_blob.json"
    write_context_blob(base_context=base_context, artifact=artifact, out_path=out_path)

    with open(out_path) as f:
        blob = json.load(f)

    # Base context should be merged
    assert blob["existing_key"] == "existing_value"
    assert blob["another_key"] == 123
    assert "auditor_artifact" in blob
    assert "auditor_policy" in blob


def test_write_context_blob_creates_parent_dir(minimal_transcript_file, tmp_path):
    """Test that write_context_blob creates parent directories."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript)

    # Use nested path that doesn't exist
    out_path = tmp_path / "nested" / "dir" / "context_blob.json"
    write_context_blob(base_context=None, artifact=artifact, out_path=out_path)

    assert out_path.exists()
    assert out_path.parent.exists()


def test_write_context_blob_default_params(minimal_transcript_file, tmp_path):
    """Test write_context_blob with default parameters."""
    transcript = load_transcript(minimal_transcript_file)
    artifact = transcript_to_artifact(transcript)

    out_path = tmp_path / "context_blob.json"
    write_context_blob(base_context=None, artifact=artifact, out_path=out_path)

    with open(out_path) as f:
        blob = json.load(f)

    # Verify defaults
    assert blob["auditor_policy"]["target_epoch"] == 0
    assert blob["auditor_policy"]["exposure_rate"] == 0.15


def test_artifact_name_no_content_leak(tmp_path):
    """Test that artifact names don't leak transcript content."""
    transcript = {
        "meta": {"source": "auditor"},
        "turns": [
            {
                "role": "user",
                "content": "SECRET_API_KEY_12345 and other sensitive data",
            }
        ],
    }
    artifact = transcript_to_artifact(transcript)

    # Name should not contain any part of the sensitive content
    assert "SECRET" not in artifact["name"].upper()
    assert "API" not in artifact["name"].upper()
    assert "12345" not in artifact["name"]
    assert "sensitive" not in artifact["name"]
    # Should be based on meta fields instead
    assert "auditor" in artifact["name"]
