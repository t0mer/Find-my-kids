# Find My Kids - WhatsApp Face Recognition Bot

This application integrates DeepFace with the WhatsApp Green API to detect predetermined faces in images shared within a WhatsApp group and to notify designated contacts immediately.

## Components

This solution leverages the following technologies:

- **[Green-API](https://green-api.com/):** Facilitates WhatsApp communication.
- **[DeepFace](https://github.com/serengil/deepface):** Provides robust face recognition capabilities.
- **[FastAPI](https://fastapi.tiangolo.com/):** Powers the web server interface.

## Prerequisites

Before proceeding with the setup, ensure that you have the following:

- [Docker and Docker Compose installed](https://medium.com/@tomer.klein/step-by-step-tutorial-installing-docker-and-docker-compose-on-ubuntu-a98a1b7aaed0)
- A registered [Green API Account](https://green-api.com/)


## Setup Instructions

### 1. Green API Configuration

#### Account Registration

1. Visit [https://green-api.com/en](https://green-api.com/en) and register for a new account.
2. Complete the registration form by entering your details and then click **Register**.

   ![Register](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/register.png)
   ![Create Account](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/create_acoount.png)

3. Once registered, select **Create an instance**.

   ![Create Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/create_instance.png)

4. Choose the **Developer** instance (Free Tier).

   ![Developer Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/developer_instance.png)

5. Copy the generated InstanceId and Token—these will be required for integration.

   ![Instance Details](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/instance_details.png)

6. To link your WhatsApp account, navigate to the API section on the left under **Account** and select **QR**. Open the provided QR URL in your browser, then click on **Scan QR code**:

   ![Send QR](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/send_qr.png)
   ![Scan QR](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/scan_qr.png)

7. Scan the QR code to complete the linking process:

   ![QR Code](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/qr.png)

8. Once linked, the instance status will display a green light, indicating it is active:

   ![Active Instance](https://raw.githubusercontent.com/t0mer/green-api-custom-notifier/refs/heads/main/screenshots/active_instance.png)

> **Important:** Do not configure a webhook URL for your instance, as this will interfere with the bot’s functionality.
>
> ![Green API webhook](screenshots/green-api-webhook.png)

### 2. Environment Configuration

1. Duplicate the sample environment file by running:
  ```bash
   cp .env.example .env
```

2. Edit the `.env` file with your credentials:
  ```
  # WhatsApp API Credentials
  GREEN_API_INSTANCE=your_whatsapp_instance_id
  GREEN_API_TOKEN=your_whatsapp_api_token
  ```
3. AWS IAM user creation
   1. Create an AWS IAM user with permissions to use Amazon Rekognition.
   2. Generate credentials (access & secret key) for the IAM user created in the previous step to be used later.

### 3. Running the Application

1. Use the following docker-compose.yaml :
  ```yaml
   services:
  find-my-kids:
    image: techblog/find-my-kids:latest
    container_name: find-my-kids
    ports:
      - "7020:7020"
    environment:
      - GREEN_API_INSTANCE=${GREEN_API_INSTANCE}
      - GREEN_API_TOKEN=${GREEN_API_TOKEN}
      - GREEN_API_TOKEN=${GREEN_API_TOKEN}
      - AWS_REGION=${AWS_REGION}
      - AWS_KEY=${AWS_KEY}
      - AWS_SECRET=${AWS_SECRET}
    volumes:
      - ./find-my-kids/images:/app/images
      - ./find-my-kids/config:/app/config
    restart: unless-stopped 
   ```
Where:
* /find-my-kids/images is the volume for the model training images and downloaded images.
* ./find-my-kids/config is the path to the config file.


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

* Kid1: the name of the kid/person
* collection_id: The Id of the collection in AWS rekognition.
* chat_ids: list of whatsapp chats (Groups or Contacts) to monitor.
* target: The target group or contact to forward the pictures to.

In order to get the list of groups, enter the following URL: http://[server_ip]:[port]/contacts

The web page will contain a table with the list of contacts and group:

![Contacts and Groups](screenshots/greenapi-contacts.png)

**After updating the config file, restart the container to reload the configuration**

### Training

#### Manual Images Upload

In order to train the Rekognition model open your browser and navigate to: http://[SERVER_IP]:[PORT]/trainer

An error may popup, it is because there are no images related for the collections, just click on OK.
![No images](screenshots/no-images-error.png)

Next, select the collecion you would like to train, Select a picture and click "Upload and Train" button:

![Upload and Train](screenshots/upload-and-train.png)

![Train Completed](screenshots/train-completed.png)

In the Gallery tab, you will see all the pictured used to train the model:
![re-train](screenshots/re-train.png)

You can click the "re-train" button to re-train the model with the pictures.


#### Bulk Images Upload

The bot also support bulk imags upload for training by adding Images to the trainer folder as follows:

```
images
    |──trainer/
          ├── Kid1/
          │   ├── image1.jpg
          │   ├── image2.jpg
          │   └── ...
          ├── Kid2/
          │   ├── image1.jpg
          │   └── ...
          └── Kid3/
              ├── image1.jpg
              └── ...
```

Next, in the Gallery tab (Web UI), you will see all the pictured used to train the model:
![re-train](screenshots/re-train.png)

You can click the "re-train" button to re-train the model with the pictures.



*Congrats, you can now use the bot.*


