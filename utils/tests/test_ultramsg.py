from django.test import TestCase
from unittest.mock import patch, MagicMock
from utils.ultramsg import UltraMsgAPI
import requests


class UltraMsgAPITest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Set up the test environment with valid UltraMsgAPI configurations.
        """
        cls.api = UltraMsgAPI()
        cls.valid_number = '558599999999'
        cls.valid_message = 'Hello, this is a test message!'
        cls.valid_image_url = 'https://example.com/image.jpg'
        cls.valid_caption = 'Test Caption'

    @patch('utils.ultramsg.requests.post')  
    def test_send_message_success(self, mock_post):
        """
        Test sending a text message successfully.
        """
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        # Call the method
        response = self.api.send_message(self.valid_number, self.valid_message)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        mock_post.assert_called_once()

    @patch('utils.ultramsg.requests.post')  
    def test_send_message_failure(self, mock_post):
        """
        Test sending a text message with failure.
        """
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'status': 'failure', 'message': 'Invalid number'}
        mock_post.return_value = mock_response

        # Call the method
        response = self.api.send_message(self.valid_number, self.valid_message)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'status': 'failure', 'message': 'Invalid number'})
        mock_post.assert_called_once()

    @patch('utils.ultramsg.requests.post')  
    def test_send_image_success(self, mock_post):
        """
        Test sending an image message successfully.
        """
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        # Call the method
        response = self.api.send_image(self.valid_number, self.valid_image_url, self.valid_caption)

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
        mock_post.assert_called_once()

    @patch('utils.ultramsg.requests.post')  
    def test_send_image_failure(self, mock_post):
        """
        Test sending an image message with failure.
        """
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {'status': 'failure', 'message': 'Invalid image URL'}
        mock_post.return_value = mock_response

        # Call the method
        response = self.api.send_image(self.valid_number, self.valid_image_url, self.valid_caption)

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'status': 'failure', 'message': 'Invalid image URL'})
        mock_post.assert_called_once()

    @patch('utils.ultramsg.config')  # Mock das variáveis de ambiente
    def test_missing_env_variables(self, mock_config):
        """
        Test exception raised when ULTRAMSG_TOKEN or ULTRAMSG_INSTANCE are not configured.
        """
        # Configurar mock para retornar None
        mock_config.side_effect = lambda key, default=None, cast=str: None

        with self.assertRaises(ValueError) as context:
            UltraMsgAPI()

        self.assertIn('ULTRAMSG_TOKEN or ULTRAMSG_INSTANCE not configured in .env', str(context.exception))

    @patch('utils.ultramsg.requests.post')
    def test_send_message_request_exception(self, mock_post):
        """
        Test handling of RequestException in send_message.
        """
        # Simular uma exceção de rede
        mock_post.side_effect = requests.exceptions.RequestException('Connection error')

        api = UltraMsgAPI()
        response = api.send_message(to='558599999999', message='Test message')

        # Verificar se o retorno contém o erro
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Connection error')

    @patch('utils.ultramsg.requests.post')
    def test_send_image_request_exception(self, mock_post):
        """
        Test handling of RequestException in send_image.
        """
        # Simular uma exceção de rede
        mock_post.side_effect = requests.exceptions.RequestException('Connection error')

        api = UltraMsgAPI()
        response = api.send_image(to='558599999999', image_url='https://example.com/image.jpg', caption='Test image')

        # Verificar se o retorno contém o erro
        self.assertIn('error', response)
        self.assertEqual(response['error'], 'Connection error')