"""Unit tests for enums module."""

from src.madousho.models.enums import FlowStatus


class TestFlowStatus:
    """Test FlowStatus enum class."""

    def test_enum_members(self):
        """Test that all expected enum members exist."""
        # Arrange
        expected_members = ["CREATED", "PROCESSING", "FINISHED"]

        # Act
        actual_members = [member.name for member in FlowStatus]

        # Assert
        assert set(actual_members) == set(expected_members)

    def test_enum_values(self):
        """Test that enum members have correct string values."""
        # Arrange
        expected_values = {
            "CREATED": "created",
            "PROCESSING": "processing",
            "FINISHED": "finished",
        }

        # Act & Assert
        for member_name, expected_value in expected_values.items():
            enum_member = getattr(FlowStatus, member_name)
            assert enum_member.value == expected_value

    def test_enum_string_values(self):
        """Test that list of all enum values equals expected list."""
        # Arrange
        expected_values = ["created", "processing", "finished"]

        # Act
        actual_values = [member.value for member in FlowStatus]

        # Assert
        assert sorted(actual_values) == sorted(expected_values)
