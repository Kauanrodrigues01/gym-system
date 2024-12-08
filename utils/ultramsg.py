import requests
import urllib.parse
from decouple import config


class UltraMsgAPI:
    def __init__(self):
        """
        Initializes the UltraMsg API with data from the .env file.
        """
        self.token = config('ULTRAMSG_TOKEN', default=None, cast=str)
        self.instance = config('ULTRAMSG_INSTANCE', default=None, cast=str)
        if not self.token or not self.instance:
            # O coverage está dizendo que não testei essa possibilidade
            raise ValueError('ULTRAMSG_TOKEN or ULTRAMSG_INSTANCE not configured in .env')

        self.base_url = f'https://api.ultramsg.com/{self.instance}/messages'
        self.headers = {'content-type': 'application/x-www-form-urlencoded'}

    def send_message(self, to, message):
        """
        Sends a text message via WhatsApp.

        :param to: Recipient phone number (e.g., '558599275573').
        :param message: Message to be sent.
        :return: API response or error message.
        """
        url = f'{self.base_url}/chat'
        encoded_message = urllib.parse.quote(message)  # Encode the message
        payload = f"token={self.token}&to={to}&body={encoded_message}"

        try:
            response = requests.post(url, data=payload, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # O coverage está dizendo que não testei essa possibilidade
            return {'error': str(e)}
        
    def send_image(self, to, image_url, caption=""):
        """
        Sends an image via WhatsApp.

        :param to: Recipient phone number (e.g., '55859xxxxxxxx').
        :param image_url: URL of the image to be sent.
        :param caption: Caption for the image.
        :return: API response or error message.
        """
        url = f'{self.base_url}/image'
        encoded_caption = urllib.parse.quote(caption)
        payload = f'token={self.token}&to={to}&image={image_url}&caption={encoded_caption}'

        try:
            response = requests.post(url, data=payload, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # O coverage está dizendo que não testei essa possibilidade
            return {'error': str(e)}


# Example usage:
if __name__ == '__main__': # pragma: no cover
    try:
        ultramsg = UltraMsgAPI()

        response = ultramsg.send_image(to='The-number', image_url='https://blog.emania.com.br/wp-content/uploads/2016/02/direitos-autorais-e-de-imagem.jpg', caption='Imagem aleatória')
        
        print(response) 
    except ValueError as e:
        print(f'Invalid configuration: {e}')