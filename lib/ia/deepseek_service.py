"""
Deepseek AI service module for making requests to the Deepseek API.
This module uses the OpenAI SDK to interact with the Deepseek API.
"""

import os
import logging
from openai import OpenAI
from django.conf import settings

logger = logging.getLogger(__name__)

class DeepSeekService:
    """
    A service class for interacting with the Deepseek API using the OpenAI SDK.
    """

    def __init__(self, api_key=None, base_url=None, default_model=None):
        """
        Initialize the DeepSeek service with API credentials.

        Args:
            api_key (str, optional): The API key for authentication
            base_url (str, optional): The base URL for the API
            default_model (str, optional): The default model to use for requests
        """
        # Get API key from settings or environment variable
        self.api_key = api_key or getattr(settings, 'DEEPSEEK_API_KEY', os.environ.get('DEEPSEEK_API_KEY'))

        if not self.api_key:
            error_msg = "Deepseek API key not found in settings or environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get base URL from settings or use default
        self.base_url = base_url or getattr(settings, 'DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

        # Use default model if not specified
        self.default_model = default_model or getattr(settings, 'DEEPSEEK_DEFAULT_MODEL', 'deepseek-chat')

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def send_prompt(self, prompt, model=None, temperature=0.7, max_tokens=1000, system_message=None):
        """
        Send a prompt to the Deepseek API and return the response.

        Args:
            prompt (str): The prompt to send to the API
            model (str, optional): The model to use for the request
            temperature (float, optional): Controls randomness in the response (0.0 to 1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            system_message (str, optional): System message to set the behavior of the assistant

        Returns:
            dict: The API response or an error message
        """
        try:
            # Use the specified model or default
            model_to_use = model or self.default_model

            # Prepare messages
            messages = []

            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            else:
                messages.append({"role": "system", "content": "You are a helpful assistant"})

            # Add user message
            messages.append({"role": "user", "content": prompt})

            # Make the API request using the OpenAI client
            response = self.client.chat.completions.create(
                model=model_to_use,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )

            logger.info("Successfully received response from Deepseek API")
            return response

        except Exception as e:
            error_msg = f"Error making request to Deepseek API: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
