"""
Email service module for sending emails using Gmail SMTP.
"""

import os
import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def send_email(subject, to_email, template_name, context=None, from_email=None):
    """
    Send an email using the specified template.
    
    Args:
        subject (str): The email subject
        to_email (str or list): The recipient email address(es)
        template_name (str): The name of the HTML template to use
        context (dict, optional): The context to render the template with
        from_email (str, optional): The sender email address
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    if context is None:
        context = {}
    
    # Use the configured from_email or default to settings
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    try:
        # Render the HTML content
        html_content = render_to_string(template_name, context)
        # Create a plain text version
        text_content = strip_tags(html_content)
        
        # Create the email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[to_email] if isinstance(to_email, str) else to_email
        )
        
        # Attach the HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send the email
        email.send()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_welcome_email(user_email, user_name=None):
    """
    Send a welcome email to a newly registered user.
    
    Args:
        user_email (str): The user's email address
        user_name (str, optional): The user's name
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    subject = "Welcome to Gemstone!"
    context = {
        'user_name': user_name or user_email.split('@')[0],
        'site_name': 'Gemstone',
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else '/',
    }
    
    return send_email(
        subject=subject,
        to_email=user_email,
        template_name='emails/welcome_email.html',
        context=context
    )