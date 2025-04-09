# Find My Kids - WhatsApp Face Recognition Bot

This application uses AWS Rekognition and WhatsApp Green API to detect and notify when specific faces appear in images sent to a WhatsApp group.

## Prerequisites

- [Docker and Docker Compose installed](https://medium.com/@tomer.klein/step-by-step-tutorial-installing-docker-and-docker-compose-on-ubuntu-a98a1b7aaed0)
- [AWS Account](https://signin.aws.amazon.com/signup?request_type=register)
- [Green API Account](https://green-api.com/)

## Setup Instructions

### 1. AWS Account Setup

#### Create an AWS Account
1. Go to [AWS Sign Up](https://signin.aws.amazon.com/signup?request_type=register)
2. Follow the registration process
3. Complete the account verification

#### Create IAM User and Access Keys
1. Sign in to the AWS Management Console
2. Navigate to IAM (Identity and Access Management)
3. Click on "Users" in the left navigation pane
4. Click "Create user"
5. Enter a username (e.g., `find-my-kids-bot`)
6. Select "Access key - Programmatic access"
7. Click "Next: Permissions"
8. Click "Attach existing policies directly"
9. Search for and select "AmazonRekognitionFullAccess"
10. Click "Next: Tags" (optional)
11. Click "Next: Review"
12. Click "Create user"
13. **IMPORTANT**: Download the CSV file containing your access key and secret key

[![YouTube](http://i.ytimg.com/vi/lIdh92JmWtg/hqdefault.jpg)](https://www.youtube.com/watch?v=lIdh92JmWtg)


### 2. Green API Setup

#### Create a Green API Account
1. Go to [Green API](https://green-api.com/)
2. Click "Sign Up" and create an account
3. Verify your email address

#### Get API Credentials
1. Log in to your Green API account
2. Go to "API Settings"
3. Create a new instance
4. Note down your:
   - Instance ID
   - API Token

### 3. Environment Setup

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your credentials:
   ```
   # AWS Credentials
   AWS_REGION=your_aws_region
   AWS_KEY=your_aws_access_key
   AWS_SECRET=your_aws_secret_key

   # WhatsApp API Credentials
   GREEN_API_INSTANCE=your_whatsapp_instance_id
   GREEN_API_TOKEN=your_whatsapp_api_token
   ```

### 4. Running the Application

1. Pull the latest image:
   ```bash
   docker-compose pull
   ```

2. Start the application:
   ```bash
   docker-compose up -d
   ```

3. The application will be available at `http://[Server_IP]:[Port]`

## Usage

1. Send an image to your WhatsApp number
2. The bot will process the image and check for matches
3. If a match is found, you'll receive a notification

## API Endpoints

- `POST /train` - Train a new face collection
- `DELETE /collection/delete` - Delete a face collection

## Troubleshooting

If you encounter any issues:

1. Check the logs:
   ```bash
   docker-compose logs -f
   ```

2. Verify your environment variables are set correctly
3. Ensure your AWS and Green API credentials are valid
4. Check that your WhatsApp number is properly linked to Green API

## Security Notes

- Never commit your `.env` file to version control
- Keep your AWS and Green API credentials secure
- Regularly rotate your access keys
- Use environment variables for sensitive data

## Support

For support, please open an issue in the GitHub repository. 