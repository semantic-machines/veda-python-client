"""
Tests for the Veda Platform API models.
"""

import unittest
from datetime import datetime, timezone, timedelta
from veda_client.models import Individual, ValueItem
from veda_client.utils import format_datetime


class TestValueItem(unittest.TestCase):
    """Test cases for the ValueItem class."""

    def test_init(self):
        """Test ValueItem initialization."""
        value = ValueItem(data="Test", type_="String", lang="EN")
        self.assertEqual(value.data, "Test")
        self.assertEqual(value.type, "String")
        self.assertEqual(value.lang, "EN")
    
    def test_from_dict(self):
        """Test creating ValueItem from a dictionary."""
        data = {
            "data": "Test",
            "type": "String",
            "lang": "EN"
        }
        value = ValueItem.from_dict(data)
        self.assertEqual(value.data, "Test")
        self.assertEqual(value.type, "String")
        self.assertEqual(value.lang, "EN")
    
    def test_to_dict(self):
        """Test converting ValueItem to a dictionary."""
        value = ValueItem(data="Test", type_="String", lang="EN")
        data = value.to_dict()
        self.assertEqual(data, {
            "data": "Test",
            "type": "String",
            "lang": "EN"
        })
    
    def test_to_dict_no_lang(self):
        """Test converting ValueItem with no language to a dictionary."""
        value = ValueItem(data=42, type_="Integer")
        data = value.to_dict()
        self.assertEqual(data, {
            "data": 42,
            "type": "Integer"
        })


class TestIndividual(unittest.TestCase):
    """Test cases for the Individual class."""

    def test_init(self):
        """Test Individual initialization."""
        individual = Individual(uri="test:123")
        self.assertEqual(individual.uri, "test:123")
        self.assertEqual(individual.properties, {})
    
    def test_from_dict(self):
        """Test creating Individual from a dictionary."""
        data = {
            "@": "test:123",
            "rdf:type": [{"data": "test:Type", "type": "Uri"}],
            "rdfs:label": [
                {"data": "Test Label", "type": "String", "lang": "EN"},
                {"data": "Тестовая метка", "type": "String", "lang": "RU"}
            ]
        }
        individual = Individual.from_dict(data)
        self.assertEqual(individual.uri, "test:123")
        self.assertEqual(len(individual.properties["rdf:type"]), 1)
        self.assertEqual(len(individual.properties["rdfs:label"]), 2)
        self.assertEqual(individual.properties["rdf:type"][0].data, "test:Type")
        self.assertEqual(individual.properties["rdfs:label"][0].data, "Test Label")
        self.assertEqual(individual.properties["rdfs:label"][1].lang, "RU")
    
    def test_to_dict(self):
        """Test converting Individual to a dictionary."""
        individual = Individual(uri="test:123")
        individual.add_value("rdf:type", "test:Type", "Uri")
        individual.add_value("rdfs:label", "Test Label", "String", "EN")
        
        data = individual.to_dict()
        self.assertEqual(data["@"], "test:123")
        self.assertEqual(len(data["rdf:type"]), 1)
        self.assertEqual(len(data["rdfs:label"]), 1)
        self.assertEqual(data["rdf:type"][0]["data"], "test:Type")
        self.assertEqual(data["rdfs:label"][0]["data"], "Test Label")
        self.assertEqual(data["rdfs:label"][0]["lang"], "EN")
    
    def test_get_property(self):
        """Test getting a property."""
        individual = Individual(uri="test:123")
        individual.add_value("rdfs:label", "Test Label", "String", "EN")
        
        # Get existing property
        labels = individual.get_property("rdfs:label")
        self.assertEqual(len(labels), 1)
        self.assertEqual(labels[0].data, "Test Label")
        
        # Get non-existing property
        comments = individual.get_property("rdfs:comment")
        self.assertEqual(comments, [])
    
    def test_get_first_value(self):
        """Test getting the first value of a property."""
        individual = Individual(uri="test:123")
        individual.add_value("rdfs:label", "Test Label 1", "String", "EN")
        individual.add_value("rdfs:label", "Test Label 2", "String", "EN")
        
        # Get first value of existing property
        label = individual.get_first_value("rdfs:label")
        self.assertEqual(label, "Test Label 1")
        
        # Get first value of non-existing property
        comment = individual.get_first_value("rdfs:comment")
        self.assertIsNone(comment)
    
    def test_set_property(self):
        """Test setting a property."""
        individual = Individual(uri="test:123")
        
        # Set property with ValueItem instances
        individual.set_property("rdfs:label", [
            ValueItem(data="Test Label", type_="String", lang="EN")
        ])
        self.assertEqual(len(individual.properties["rdfs:label"]), 1)
        self.assertEqual(individual.properties["rdfs:label"][0].data, "Test Label")
        
        # Set property with dictionaries
        individual.set_property("rdfs:comment", [
            {"data": "Test Comment", "type": "String", "lang": "EN"}
        ])
        self.assertEqual(len(individual.properties["rdfs:comment"]), 1)
        self.assertEqual(individual.properties["rdfs:comment"][0].data, "Test Comment")
        
        # Override existing property
        individual.set_property("rdfs:label", [
            {"data": "New Label", "type": "String", "lang": "EN"}
        ])
        self.assertEqual(len(individual.properties["rdfs:label"]), 1)
        self.assertEqual(individual.properties["rdfs:label"][0].data, "New Label")
    
    def test_add_value(self):
        """Test adding a value to a property."""
        individual = Individual(uri="test:123")
        
        # Add to non-existing property
        individual.add_value("rdfs:label", "Test Label", "String", "EN")
        self.assertEqual(len(individual.properties["rdfs:label"]), 1)
        
        # Add to existing property
        individual.add_value("rdfs:label", "Another Label", "String", "EN")
        self.assertEqual(len(individual.properties["rdfs:label"]), 2)
        self.assertEqual(individual.properties["rdfs:label"][1].data, "Another Label")
    
    def test_remove_property(self):
        """Test removing a property."""
        individual = Individual(uri="test:123")
        individual.add_value("rdfs:label", "Test Label", "String", "EN")
        individual.add_value("rdfs:comment", "Test Comment", "String", "EN")
        
        # Remove existing property
        individual.remove_property("rdfs:label")
        self.assertNotIn("rdfs:label", individual.properties)
        self.assertIn("rdfs:comment", individual.properties)
        
        # Remove non-existing property (should not raise an error)
        individual.remove_property("non:existing")


class TestFormatDatetime(unittest.TestCase):
    """Test cases for the format_datetime utility function."""

    def test_naive_datetime_no_microseconds(self):
        """Naive datetime without microseconds is formatted as-is."""
        dt = datetime(2026, 3, 1, 18, 49, 13)
        self.assertEqual(format_datetime(dt), "2026-03-01T18:49:13")

    def test_naive_datetime_strips_microseconds(self):
        """Naive datetime with microseconds has them stripped."""
        dt = datetime(2026, 3, 1, 18, 49, 13, 604389)
        self.assertEqual(format_datetime(dt), "2026-03-01T18:49:13")

    def test_utc_aware_datetime(self):
        """UTC-aware datetime is formatted with Z suffix."""
        dt = datetime(2026, 3, 1, 18, 49, 13, tzinfo=timezone.utc)
        self.assertEqual(format_datetime(dt), "2026-03-01T18:49:13Z")

    def test_utc_aware_datetime_strips_microseconds(self):
        """UTC-aware datetime with microseconds has them stripped."""
        dt = datetime(2026, 3, 1, 18, 49, 13, 604389, tzinfo=timezone.utc)
        self.assertEqual(format_datetime(dt), "2026-03-01T18:49:13Z")

    def test_offset_aware_datetime_converted_to_utc(self):
        """Offset-aware datetime is converted to UTC before formatting."""
        tz_plus3 = timezone(timedelta(hours=3))
        dt = datetime(2026, 3, 1, 21, 49, 13, tzinfo=tz_plus3)
        self.assertEqual(format_datetime(dt), "2026-03-01T18:49:13Z")


class TestValueItemDatetime(unittest.TestCase):
    """Test cases for ValueItem datetime serialization."""

    def test_to_dict_with_datetime_object(self):
        """ValueItem with type Datetime and datetime object serializes correctly."""
        dt = datetime(2026, 3, 1, 18, 49, 13, 604389, tzinfo=timezone.utc)
        item = ValueItem(data=dt, type_="Datetime")
        result = item.to_dict()
        self.assertEqual(result["data"], "2026-03-01T18:49:13Z")
        self.assertEqual(result["type"], "Datetime")

    def test_to_dict_with_string_data_unchanged(self):
        """ValueItem with type Datetime and string data passes through unchanged."""
        item = ValueItem(data="2026-03-01T18:49:13Z", type_="Datetime")
        result = item.to_dict()
        self.assertEqual(result["data"], "2026-03-01T18:49:13Z")

    def test_to_dict_non_datetime_type_unchanged(self):
        """ValueItem with non-Datetime type and datetime-like object is not converted."""
        item = ValueItem(data="2026-03-01T18:49:13.604389", type_="String")
        result = item.to_dict()
        self.assertEqual(result["data"], "2026-03-01T18:49:13.604389")


class TestIndividualDatetimeMethods(unittest.TestCase):
    """Test cases for Individual datetime helper methods."""

    def test_add_datetime_value_naive(self):
        """add_datetime_value with naive datetime stores formatted string."""
        individual = Individual(uri="test:1")
        dt = datetime(2026, 3, 1, 18, 49, 13, 604389)
        individual.add_datetime_value("v-s:lastSeen", dt)

        values = individual.get_property("v-s:lastSeen")
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].type, "Datetime")
        self.assertEqual(values[0].data, "2026-03-01T18:49:13")

    def test_add_datetime_value_utc(self):
        """add_datetime_value with UTC datetime stores formatted string with Z."""
        individual = Individual(uri="test:1")
        dt = datetime(2026, 3, 1, 18, 49, 13, 604389, tzinfo=timezone.utc)
        individual.add_datetime_value("v-s:lastSeen", dt)

        values = individual.get_property("v-s:lastSeen")
        self.assertEqual(values[0].data, "2026-03-01T18:49:13Z")

    def test_add_datetime_value_appends(self):
        """add_datetime_value appends to existing values."""
        individual = Individual(uri="test:1")
        individual.add_datetime_value("v-s:date", datetime(2026, 1, 1))
        individual.add_datetime_value("v-s:date", datetime(2026, 6, 1))
        self.assertEqual(len(individual.get_property("v-s:date")), 2)

    def test_set_datetime_value_replaces(self):
        """set_datetime_value replaces all existing values."""
        individual = Individual(uri="test:1")
        individual.add_datetime_value("v-s:lastSeen", datetime(2026, 1, 1))
        individual.add_datetime_value("v-s:lastSeen", datetime(2026, 2, 1))
        individual.set_datetime_value("v-s:lastSeen", datetime(2026, 3, 1, 18, 49, 13, 604389))

        values = individual.get_property("v-s:lastSeen")
        self.assertEqual(len(values), 1)
        self.assertEqual(values[0].data, "2026-03-01T18:49:13")

    def test_to_dict_contains_formatted_datetime(self):
        """to_dict() on Individual with datetime value contains correct string."""
        individual = Individual(uri="test:1")
        individual.add_datetime_value("v-s:lastSeen", datetime(2026, 3, 1, 18, 49, 13, 604389, tzinfo=timezone.utc))

        data = individual.to_dict()
        self.assertEqual(data["v-s:lastSeen"][0]["data"], "2026-03-01T18:49:13Z")


if __name__ == '__main__':
    unittest.main()
