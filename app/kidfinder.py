import os
import io
import sys
import joblib
import numpy as np
from PIL import Image
from pathlib import Path
from loguru import logger
from deepface import DeepFace
from typing import Dict, Any, Tuple



class KidFinder:
    """
    Class for finding and matching faces in images using AWS Rekognition.
    Handles face detection, cropping, and matching against a collection.
    """
    def __init__(self):
        self.probability_threshold = os.getenv("PROBABILITY_THRESHOLD",0.5)
        self.classifiers_path = "classifiers"
        self.classifier_suffix = "_classifier.joblib"
        self.classifiers_path = Path.cwd() / self.classifiers_path
        self.classifiers_path.mkdir(parents=True, exist_ok=True)
        
    
    def verify_query(self ,query_image, classifier, model_name="VGG-Face", detector_backend="opencv"):
        try:
            query_rep = DeepFace.represent(img_path=query_image, model_name=model_name, detector_backend=detector_backend)
            query_embedding = np.array(query_rep[0]["embedding"]).reshape(1, -1)
        except Exception as e:
            logger.error(f"Error processing query image: {e}")
            return None, 0.0

        prediction = classifier.predict(query_embedding)
        probabilities = classifier.predict_proba(query_embedding)
        max_probability = np.max(probabilities)
        predicted_identity = prediction[0]

        if max_probability < self.probability_threshold:
            print("Confidence below threshold. Face might be unknown.")
            return False, max_probability
        logger.warning(f"predicted_identity: {predicted_identity}, max_probability: {max_probability}")
        return int(predicted_identity)==1, max_probability
    
    def find(self,query_image,collection_id):
        classifier = joblib.load(f"{self.classifiers_path}/{collection_id}{self.classifier_suffix}")
        return self.verify_query(query_image=query_image,classifier=classifier)