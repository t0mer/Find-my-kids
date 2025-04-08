import os
import boto3
from loguru import logger
from pathlib import Path
from typing import List, Dict, Any
from botocore.exceptions import ClientError

class Trainer:
    """
    Class for handling face collection training using AWS Rekognition.
    Manages the creation of collections and indexing of faces.
    """
    
    SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
    
    def __init__(self):
        """
        Initialize the Trainer with AWS Rekognition client and base paths.
        """
        self.rekognition = boto3.client(
            'rekognition',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET")
        )
        self.trainer_images_path = Path.cwd() / "images" / "trainer"
        self.trainer_images_path.mkdir(parents=True, exist_ok=True)

    def train(self, collection_id: str) -> bool:
        """
        Train a face collection by creating it and indexing faces from images.
        
        Args:
            collection_id (str): The ID of the collection to create/train
            
        Returns:
            bool: True if training was successful, False otherwise
        """
        # Set up collection-specific path
        self.trainer_images_path = Path.cwd() / "images" / "trainer" / collection_id
        self.trainer_images_path.mkdir(parents=True, exist_ok=True)

        try:
            # Create collection if it doesn't exist
            self._create_collection(collection_id)
            
            # Process and index images
            return self._process_images(collection_id)
            
        except Exception as e:
            logger.error(f"Error during training: {e}")
            return False

    def _create_collection(self, collection_id: str) -> None:
        """
        Create a new face collection in AWS Rekognition.
        
        Args:
            collection_id (str): The ID of the collection to create
            
        Raises:
            ClientError: If there's an AWS service error
        """
        try:
            self.rekognition.create_collection(CollectionId=collection_id)
            logger.info(f"Collection '{collection_id}' created successfully.")
        except self.rekognition.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Collection '{collection_id}' already exists.")
        except ClientError as e:
            logger.error(f"AWS error creating collection: {e}")
            raise

    def _process_images(self, collection_id: str) -> bool:
        """
        Process and index all images in the trainer directory.
        
        Args:
            collection_id (str): The ID of the collection to index faces into
            
        Returns:
            bool: True if all images were processed successfully
        """
        try:
            for filename in os.listdir(self.trainer_images_path):
                if filename.lower().endswith(self.SUPPORTED_IMAGE_EXTENSIONS):
                    image_path = self.trainer_images_path / filename
                    self._index_faces(collection_id, image_path)
            return True
        except Exception as e:
            logger.error(f"Error processing images: {e}")
            return False

    def _index_faces(self, collection_id: str, image_path: Path) -> None:
        """
        Index faces from a single image into the collection.
        
        Args:
            collection_id (str): The ID of the collection to index into
            image_path (Path): Path to the image file
            
        Raises:
            Exception: If there's an error reading or processing the image
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_bytes = image_file.read()

            response = self.rekognition.index_faces(
                CollectionId=collection_id,
                Image={'Bytes': image_bytes},
                ExternalImageId=collection_id,
                DetectionAttributes=[]
            )
            
            face_records = response.get('FaceRecords', [])
            if face_records:
                logger.info(f"Indexed {len(face_records)} faces from {image_path.name}")
            else:
                logger.warning(f"No faces detected in {image_path.name}")
                
        except Exception as e:
            logger.error(f"Error indexing faces from {image_path.name}: {e}")
            raise

