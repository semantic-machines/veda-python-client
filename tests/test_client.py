"""
Tests for the Veda Platform API client.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import requests

from veda_client import VedaClient
from veda_client.exceptions import VedaAuthError, VedaResponseError, VedaServerError
from veda_client.models import Individual


class TestVedaClient(unittest.TestCase):
    """Test cases for the VedaClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = VedaClient(base_url="http://test.example.com/api")
    
    @patch('requests.get')
    def test_authenticate_success(self, mock_get):
        """Test successful authentication."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "end_time": 1635858783968916000,
            "id": "a7e13ad5-f846-4f8f-8543-aceda5fc4718",
            "result": 200,
            "user_uri": "td:TestUser"
        }
        mock_get.return_value = mock_response
        
        # Call authenticate
        result = self.client.authenticate("test_user", "test_password")
        
        # Verify the call
        mock_get.assert_called_once_with(
            "http://test.example.com/api/authenticate",
            params={"login": "test_user", "password": "test_password"}
        )
        
        # Verify the result
        self.assertEqual(result["id"], "a7e13ad5-f846-4f8f-8543-aceda5fc4718")
        self.assertEqual(result["user_uri"], "td:TestUser")
        
        # Verify the client state
        self.assertEqual(self.client.ticket, "a7e13ad5-f846-4f8f-8543-aceda5fc4718")
        self.assertEqual(self.client.user_uri, "td:TestUser")
    
    @patch('requests.get')
    def test_authenticate_failure(self, mock_get):
        """Test authentication failure."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 472
        mock_get.return_value = mock_response
        
        # Call authenticate and expect exception
        with self.assertRaises(VedaAuthError):
            self.client.authenticate("test_user", "wrong_password")
    
    @patch('requests.get')
    def test_is_ticket_valid_true(self, mock_get):
        """Test ticket validation when valid."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = True
        mock_get.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Call is_ticket_valid
        result = self.client.is_ticket_valid()
        
        # Verify the call
        mock_get.assert_called_once_with(
            "http://test.example.com/api/is_ticket_valid",
            params={"ticket": "valid-ticket"}
        )
        
        # Verify the result
        self.assertTrue(result)
    
    @patch('requests.get')
    def test_is_ticket_valid_false(self, mock_get):
        """Test ticket validation when invalid."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = False
        mock_get.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "invalid-ticket"
        
        # Call is_ticket_valid
        result = self.client.is_ticket_valid()
        
        # Verify the result
        self.assertFalse(result)
    
    def test_is_ticket_valid_no_ticket(self):
        """Test ticket validation with no ticket."""
        # No ticket in client
        self.client.ticket = None
        
        # Call is_ticket_valid and expect exception
        with self.assertRaises(VedaAuthError):
            self.client.is_ticket_valid()
    
    @patch('requests.post')
    def test_query(self, mock_post):
        """Test executing a query."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": ["td:User1", "td:User2", "td:User3"],
            "count": 3,
            "estimated": 3,
            "processed": 3,
            "cursor": 3,
            "result_code": 200
        }
        mock_post.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Call query
        result = self.client.query(
            query="( 'rdf:type'=='v-s:UserThing' )",
            sort="'v-s:created' desc",
            limit=10
        )
        
        # Verify the call
        mock_post.assert_called_once_with(
            "http://test.example.com/api/query",
            json={
                "ticket": "valid-ticket",
                "query": "( 'rdf:type'=='v-s:UserThing' )",
                "sort": "'v-s:created' desc",
                "limit": 10
            }
        )
        
        # Verify the result
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["result"], ["td:User1", "td:User2", "td:User3"])
    
    @patch('requests.get')
    def test_get_individual(self, mock_get):
        """Test retrieving an individual."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "@": "v-ui:DefaultLanguage",
            "rdf:type": [{"data": "rdfs:Resource", "type": "Uri"}],
            "rdf:value": [{"data": "v-ui:RU", "type": "Uri"}],
            "rdfs:label": [
                {"data": "Язык по-умолчанию", "lang": "RU", "type": "String"},
                {"data": "Default language", "lang": "EN", "type": "String"}
            ],
            "v-s:updateCounter": [{"data": 1, "type": "Integer"}]
        }
        mock_get.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Call get_individual
        individual = self.client.get_individual("v-ui:DefaultLanguage")
        
        # Verify the call
        mock_get.assert_called_once_with(
            "http://test.example.com/api/get_individual",
            params={
                "ticket": "valid-ticket",
                "uri": "v-ui:DefaultLanguage"
            }
        )
        
        # Verify the result is an Individual
        self.assertIsInstance(individual, Individual)
        self.assertEqual(individual.uri, "v-ui:DefaultLanguage")
        
        # Verify properties
        self.assertEqual(len(individual.get_property("rdfs:label")), 2)
        self.assertEqual(individual.get_first_value("v-s:updateCounter"), 1)
    
    @patch('requests.put')
    def test_put_individual(self, mock_put):
        """Test putting an individual."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "op_id": 12246,
            "result": 200
        }
        mock_put.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Create an individual
        individual = Individual(uri="v-s:TestDocument")
        individual.add_value("rdf:type", "v-s:Document", "Uri")
        individual.add_value("rdfs:label", "Test Document", "String", "EN")
        
        # Call put_individual
        result = self.client.put_individual(individual)
        
        # Verify the call
        mock_put.assert_called_once()
        call_args = mock_put.call_args[1]
        self.assertEqual(call_args["url"], "http://test.example.com/api/put_individual")
        
        # Verify JSON payload
        json_data = call_args["json"]
        self.assertEqual(json_data["ticket"], "valid-ticket")
        self.assertEqual(json_data["individual"]["@"], "v-s:TestDocument")
        
        # Verify the result
        self.assertEqual(result["op_id"], 12246)
        self.assertEqual(result["result"], 200)
    
    @patch('requests.put')
    def test_remove_individual(self, mock_put):
        """Test removing an individual."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "op_id": 12236,
            "result": 200
        }
        mock_put.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Call remove_individual
        result = self.client.remove_individual("v-s:TestDocument")
        
        # Verify the call
        mock_put.assert_called_once_with(
            "http://test.example.com/api/remove_individual",
            json={
                "ticket": "valid-ticket",
                "uri": "v-s:TestDocument"
            }
        )
        
        # Verify the result
        self.assertEqual(result["op_id"], 12236)
        self.assertEqual(result["result"], 200)
    
    @patch('requests.get')
    def test_server_error(self, mock_get):
        """Test handling server errors."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Set ticket in client
        self.client.ticket = "valid-ticket"
        
        # Call get_individual and expect exception
        with self.assertRaises(VedaServerError):
            self.client.get_individual("v-ui:DefaultLanguage")


if __name__ == '__main__':
    unittest.main()
