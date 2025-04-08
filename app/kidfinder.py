import os
import io
import boto3
from PIL import Image
from loguru import logger
from typing import Dict, Any, Tuple
from pathlib import Path
from botocore.exceptions import ClientError

class KidFinder:
    """
    Class for finding and matching faces in images using AWS Rekognition.
    Handles face detection, cropping, and matching against a collection.
    """
    
    FACE_MATCH_THRESHOLD = 90  # Minimum confidence threshold for face matches
    
    def __init__(self):
        """
        Initialize the KidFinder with AWS Rekognition client.
        """
        self.rekognition = boto3.client(
            'rekognition',
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_KEY"),          # Replace with your AWS Access Key
            aws_secret_access_key=os.getenv("AWS_SECRET")         # Replace with your AWS Secret Key
        )

    def find(self, collection_id: str, image_path: str, label: str) -> bool:
        """
        Find a specific person in an image by matching faces against a collection.
        
        Args:
            collection_id (str): The ID of the collection to search in
            image_path (str): Path to the image file
            label (str): The label/name to match against
            
        Returns:
            bool: True if a match is found, False otherwise
            
        Raises:
            Exception: If there's an error processing the image or matching faces
        """
        try:
            # Load and process the image
            image_bytes = self._load_image(image_path)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Detect faces in the image
            face_details = self._detect_faces(image_bytes)
            
            # Check each detected face for a match
            for face_detail in face_details:
                if self._check_face_match(collection_id, image, face_detail, label):
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error finding face in image: {e}")
            raise

    def _load_image(self, image_path: str) -> bytes:
        """
        Load an image file as bytes.
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            bytes: The image data as bytes
        """
        with open(image_path, 'rb') as image_file:
            return image_file.read()

    def _detect_faces(self, image_bytes: bytes) -> list:
        """
        Detect faces in an image using AWS Rekognition.
        
        Args:
            image_bytes (bytes): The image data as bytes
            
        Returns:
            list: List of face details detected in the image
        """
        try:
            response = self.rekognition.detect_faces(
                Image={'Bytes': image_bytes},
                Attributes=['DEFAULT']
            )
            return response.get('FaceDetails', [])
        except ClientError as e:
            logger.error(f"AWS error detecting faces: {e}")
            raise

    def _check_face_match(self, collection_id: str, image: Image.Image, 
                         face_detail: Dict[str, Any], label: str) -> bool:
        """
        Check if a detected face matches the given label in the collection.
        
        Args:
            collection_id (str): The ID of the collection to search in
            image (Image.Image): The PIL Image object
            face_detail (Dict[str, Any]): Details of the detected face
            label (str): The label to match against
            
        Returns:
            bool: True if a match is found, False otherwise
        """
        # Get face coordinates and crop
        bbox = face_detail['BoundingBox']
        cropped_face = self._crop_face(image, bbox)
        
        # Search for matches in the collection
        matches = self._search_face_collection(collection_id, cropped_face)
        
        # Check if any match corresponds to the label
        return any(match['Face'].get('ExternalImageId', '').lower() == label.lower() 
                  for match in matches)

    def _crop_face(self, image: Image.Image, bbox: Dict[str, float]) -> bytes:
        """
        Crop a face region from an image and convert to bytes.
        
        Args:
            image (Image.Image): The PIL Image object
            bbox (Dict[str, float]): Bounding box coordinates (relative values)
            
        Returns:
            bytes: The cropped face image as JPEG bytes
        """
        width, height = image.size
        left = int(bbox['Left'] * width)
        top = int(bbox['Top'] * height)
        face_width = int(bbox['Width'] * width)
        face_height = int(bbox['Height'] * height)
        
        cropped_face = image.crop((left, top, left + face_width, top + face_height))
        
        buf = io.BytesIO()
        cropped_face.save(buf, format='JPEG')
        return buf.getvalue()

    def _search_face_collection(self, collection_id: str, face_bytes: bytes) -> list:
        """
        Search for face matches in a collection.
        
        Args:
            collection_id (str): The ID of the collection to search in
            face_bytes (bytes): The face image data as bytes
            
        Returns:
            list: List of face matches found
        """
        try:
            response = self.rekognition.search_faces_by_image(
                CollectionId=collection_id,
                Image={'Bytes': face_bytes},
                FaceMatchThreshold=self.FACE_MATCH_THRESHOLD,
                MaxFaces=1
            )
            return response.get('FaceMatches', [])
        except ClientError as e:
            logger.error(f"AWS error searching face collection: {e}")
            raise
    
    
