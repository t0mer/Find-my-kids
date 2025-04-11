# Find My Kids - WhatsApp Face Recognition Bot

This application uses AWS Rekognition and WhatsApp Green API to detect and notify when specific faces appear in images sent to a WhatsApp group.

## Table of Contents

- [Find My Kids - WhatsApp Face Recognition Bot](#find-my-kids---whatsapp-face-recognition-bot)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
    - [1. AWS Account Setup](#1-aws-account-setup)
      - [Create an AWS Account](#create-an-aws-account)
      - [Create IAM User and Access Keys](#create-iam-user-and-access-keys)
    - [2. Green API Setup](#2-green-api-setup)
      - [Setup Green API account](#setup-green-api-account)
      - [***Important Note:***](#important-note)
    - [3. Environment Setup](#3-environment-setup)
    - [4. Running the Application](#4-running-the-application)
  - [Usage](#usage)
    - [Configuration file](#configuration-file)
    - [Training](#training)
    - [Things to know](#things-to-know)

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

[![YouTube](http://i.ytimg.com/vi/lIdh92JmWtg/hqdefault.jpg)](https://www.youtube.com/watch?v=lIdh92JmWtg)

#### Create IAM User and Access Keys

1. Sign in to the AWS Management Console
2. Navigate to IAM (Identity and Access Management)
3. Click on "Users" in the left navigation pane
4. Click "Create user"
5. Enter a username (e.g., `find-my-kids-bot`)
6. Click "Next"
7. Click "Attach policies directly"
8. Search for and select "AmazonRekognitionFullAccess"
9. Click "Next"
10. Now Review and create (you can skip the tags step)
11. Click "Create user"
12. Select the user you just created and click on the "Users" tab
13. Go to the "Security credentials" tab
14. Click "Create access key"
15. Select "CLI" as the access key type
16. Click "Next"
17. Write a Description for the access key (e.g., `find-my-kids-bot`)
18. Click "Create access key"
19. **IMPORTANT**: Download the CSV file containing your access key and secret key

### 2. Green API Setup

#### Setup Green API account

Nevigate to [https://green-api.com/en](https://green-api.com/en) and register for a new account:
![Register](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/register.png)

Fill up your details and click on **Register**:
![Create Account](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/create_acoount.png)

Next, click on the "Create an instance":
![Create Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/create_instance.png)

Select the "Developer" instance (Free):
![Developer Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/developer_instance.png)

Copy the InstanceId and Token, we need it for the integration settings:
![Instance Details](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/instance_details.png)

Next, Lets connect our whatsapp with green-api. On the left side, Under API --> Account, click on QR and copy the QR URL to the browser and click on "Scan QR code"

![Send QR](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/send_qr.png)

![Scan QR](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/scan_qr.png)

Next, Scan the QR code to link you whatsapp with Green API:

![QR Code](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/qr.png)

After the account link, you will notice that the instance is active by the green light in the instance header:
![Active Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/active_instance.png)

#### ***Important Note:***

Do not set webhook url for your instance, otherwise the bot will not work.
![Green API webhook](screenshots/green-api-webhook.png)

### 3. Environment Setup

1. Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

2. Edit the `.env` file with your credentials:

```bash
   # AWS Credentials
   AWS_REGION=your_aws_region
   AWS_KEY=your_aws_access_key
   AWS_SECRET=your_aws_secret_key

   # WhatsApp API Credentials
   GREEN_API_INSTANCE=your_whatsapp_instance_id
   GREEN_API_TOKEN=your_whatsapp_api_token
```

### 4. Running the Application

1. Use the following docker-compose.yaml :

```yaml
   services:
  app:
    image: techblog/find-my-kids:latest
    ports:
      - "7020:7020"
    environment:
      - AWS_REGION=${AWS_REGION}
      - AWS_KEY=${AWS_KEY}
      - AWS_SECRET=${AWS_SECRET}
      - GREEN_API_INSTANCE=${GREEN_API_INSTANCE}
      - GREEN_API_TOKEN=${GREEN_API_TOKEN}
    volumes:
      - ./find-my-kids/images:/app/images
      - ./find-my-kids/config:/app/config
    restart: unless-stopped 
```

Where:

- /find-my-kids/images is the volume for the model training images and downloaded images.
- ./find-my-kids/config is the path to the config file.

2. Start the application:

```bash
docker-compose up -d
```

3. The application will be available at `http://[Server_IP]:[Port]`

## Usage

### Configuration file

Under the config folder you will find a file named *config.yaml* with the following content:

```yaml
kids:
  Kid1: 
    collection_id: Kid1
    chat_ids:
      - 000000000000000000@g.us

target: 972000000000-1000000000@g.us
```

- Kid1 is the name of the kid/person
- collection_id: The Id of the collection in AWS rekognition.
- chat_ids: list of whatsapp chats (Groups or Contacts) to monitor.
- target: The target group or contact to forward the pictures to.

In order to get the list of groups, enter the following URL: `http://[server_ip]:[port]/contacts`

The web page will contain a table with the list of contacts and group:

![Contacts and Groups](screenshots/greenapi-contacts.png)

> **After updating the config file, restart the container to reload the configuration**

### Training

In order to train the Rekognition model open your browser and navigate to: `http://[SERVER_IP]:[PORT]/trainer`

An error may popup, it is because there are no images related for the collections, just click on OK.
![No images](screenshots/no-images-error.png)

Next, select the collecion you would like to train, Select a picture and click "Upload and Train" button:

![Upload and Train](screenshots/upload-and-train.png)

![Train Completed](screenshots/train-completed.png)

In the Gallery tab, you will see all the pictured used to train the model:
![re-train](screenshots/re-train.png)

You can click the "re-train" button to re-train the model with the pictures.

*Congrats, you can now use the bot.*

### Things to know

AWS Rekognition is included in the Free Tier for 12 Months (5000 images per month):
![Rekognition free tier](screenshots/rekognition-free.png)

After 12 months, The pricing will be 0.001$ per API call:
![Rekognition pricing](screenshots/rekognition-pricing.png)
