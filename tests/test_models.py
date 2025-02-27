"""
Tests for the Veda Platform API models.
"""

import unittest
from veda_client.models import Individual, ValueItem


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


if __name__ == '__main__':
    unittest.main()
