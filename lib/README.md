# Email Service

This library provides functionality for sending emails from the Gemstone application using Gmail's SMTP server.

## Configuration

### Environment Variables

Add the following environment variables to your `.env` file:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SITE_URL=http://your-site-url.com
```

### Gmail Configuration

To use Gmail's SMTP server, you need to:

1. **Enable 2-Step Verification**:
   - Go to your Google Account settings
   - Select "Security"
   - Under "Signing in to Google," select "2-Step Verification" and follow the steps

2. **Create an App Password**:
   - After enabling 2-Step Verification, go back to the Security page
   - Under "Signing in to Google," select "App passwords"
   - Select "Mail" as the app and "Other" as the device (give it a name like "Gemstone")
   - Click "Generate"
   - Use the generated 16-character password as your `EMAIL_HOST_PASSWORD` in the environment variables

3. **Allow Less Secure Apps** (Alternative if App Passwords don't work):
   - Go to https://myaccount.google.com/lesssecureapps
   - Turn on "Allow less secure apps"
   - Note: This option is not recommended and may not be available if you have 2-Step Verification enabled

## Usage

### Sending a Welcome Email

To send a welcome email to a newly registered user:

```python
from lib.email_service import send_welcome_email

# Send welcome email
send_welcome_email(user_email='user@example.com', user_name='John Doe')
```

### Sending a Custom Email

To send a custom email:

```python
from lib.email_service import send_email

# Send custom email
send_email(
    subject='Your Subject',
    to_email='recipient@example.com',
    template_name='emails/your_template.html',
    context={'key': 'value'}
)
```

## Email Templates

Email templates are stored in the `templates/emails/` directory. To create a new email template:

1. Create a new HTML file in the `templates/emails/` directory
2. Use Django template syntax for dynamic content
3. Reference the template in your code using the path relative to the templates directory