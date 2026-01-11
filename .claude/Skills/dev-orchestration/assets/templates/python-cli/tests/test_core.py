"""
Tests for core module.
"""
import pytest
from src.core import process_data, validate_input, transform_data


class TestProcessData:
    """Tests for process_data function."""
    
    def test_add_action(self):
        """Test adding an item."""
        result = process_data(action="add", item="test_item")
        assert "test_item" in result
        assert "added" in result.lower()
    
    def test_add_action_missing_item(self):
        """Test add action fails without item parameter."""
        with pytest.raises(ValueError, match="Item parameter required"):
            process_data(action="add")
    
    def test_list_action(self):
        """Test listing items."""
        result = process_data(action="list")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_remove_action(self):
        """Test removing an item."""
        result = process_data(action="remove", item_id=1)
        assert "removed" in result.lower()
    
    def test_remove_action_missing_id(self):
        """Test remove action fails without item_id."""
        with pytest.raises(ValueError, match="item_id parameter required"):
            process_data(action="remove")
    
    def test_invalid_action(self):
        """Test that invalid actions raise ValueError."""
        with pytest.raises(ValueError, match="Unknown action"):
            process_data(action="invalid_action")


class TestValidateInput:
    """Tests for validate_input function."""
    
    def test_valid_input(self):
        """Test validation of valid input."""
        assert validate_input("valid_data") is True
    
    def test_empty_string(self):
        """Test validation rejects empty string."""
        assert validate_input("") is False
    
    def test_whitespace_only(self):
        """Test validation rejects whitespace-only string."""
        assert validate_input("   ") is False
    
    def test_none_input(self):
        """Test validation rejects None."""
        assert validate_input(None) is False
    
    def test_non_string_input(self):
        """Test validation rejects non-string types."""
        assert validate_input(123) is False
        assert validate_input([]) is False


class TestTransformData:
    """Tests for transform_data function."""
    
    def test_strip_whitespace(self):
        """Test that transform strips whitespace."""
        result = transform_data("  hello  ")
        assert result == "hello"
    
    def test_lowercase_conversion(self):
        """Test that transform converts to lowercase."""
        result = transform_data("HELLO")
        assert result == "hello"
    
    def test_combined_transformation(self):
        """Test that transform handles both strip and lowercase."""
        result = transform_data("  HELLO WORLD  ")
        assert result == "hello world"
    
    def test_already_clean_input(self):
        """Test that clean input passes through unchanged."""
        result = transform_data("hello")
        assert result == "hello"
