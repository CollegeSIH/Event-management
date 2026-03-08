# EventHub Email Configuration Guide

## Email Verification Setup

EventHub now supports real-time email verification for user registration. In development mode, verification codes are logged to the console. For production, configure SMTP settings to send actual emails.

## Development Mode (Current Setup)

- Verification codes are generated and logged to the backend console
- Codes are also returned in API responses for testing
- No email credentials required

## Production Setup

### 1. Configure SMTP Settings

Edit `backend/.env` file with your email service credentials:

#### Gmail Setup
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
```

**Important:** Use Gmail App Passwords, not your regular password:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "EventHub"
3. Use this password in SMTP_PASSWORD

#### SendGrid Setup
```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
FROM_EMAIL=your-verified-sender@yourdomain.com
```

#### Other SMTP Providers
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
FROM_EMAIL=noreply@yourdomain.com
```

### 2. Security Considerations

- **Remove test code in production:** Edit `backend/app.py` and remove the `'code'` field from the `/send-verification` endpoint response
- **Use HTTPS:** Ensure your application uses HTTPS in production
- **Rate limiting:** Consider adding rate limiting to prevent abuse
- **Code expiration:** Implement proper code expiration (currently 10 minutes mentioned in email)

### 3. Testing Production Email

After configuring credentials:

```bash
cd backend
python -c "
import requests
response = requests.post('http://localhost:5000/send-verification', json={'email': 'your-test-email@example.com'})
print('Status:', response.status_code)
print('Response:', response.json())
"
```

Check your email for the verification code!

## API Endpoints

### POST /send-verification
Sends verification code to email address.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (Development):**
```json
{
  "message": "Verification code sent",
  "code": "123456"
}
```

**Response (Production):**
```json
{
  "message": "Verification code sent"
}
```

## Troubleshooting

### Common Issues

1. **"Failed to send email" error**
   - Check SMTP credentials in `.env`
   - Verify SMTP server settings
   - Check firewall/antivirus blocking SMTP

2. **Gmail authentication failed**
   - Enable 2-factor authentication
   - Generate App Password instead of using regular password
   - Check if less secure apps are allowed

3. **Emails going to spam**
   - Use a verified domain email
   - Add SPF/DKIM records
   - Ask users to check spam folder

### Email Service Alternatives

- **SendGrid:** Professional email service with good deliverability
- **Mailgun:** Good for transactional emails
- **AWS SES:** Cost-effective for high volume
- **Postmark:** Excellent deliverability rates

## Security Best Practices

1. Store verification codes securely (database with expiration)
2. Implement rate limiting on verification endpoints
3. Use HTTPS for all email-related requests
4. Validate email formats server-side
5. Implement account lockout after failed attempts
6. Clean up expired verification codes regularly