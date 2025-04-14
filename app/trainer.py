import os
import joblib
import numpy as np
from pathlib import Path
from loguru import logger
from sklearn.svm import SVC
from deepface import DeepFace
from typing import List, Dict, Any



class Trainer:
    """
    Handles face embedding extraction and one-vs-all classifier training
    for each identity. The classifiers are stored in the "classifiers" folder.
    """
    def __init__(self):
        # Define and create the dataset directory and classifiers output folder.
        self.dataset_dir = Path.cwd() / "images" / "trainer"
        self.dataset_dir.mkdir(parents=True, exist_ok=True)
        self.classifiers_path = Path.cwd() / "classifiers"
        self.classifiers_path.mkdir(parents=True, exist_ok=True)

    def load_dataset(self, model_name="VGG-Face", detector_backend="opencv"):
        """
        Extracts face embeddings from images organized by subdirectory.
        Returns:
            embeddings: A numpy array of face embeddings.
            labels: A numpy array of corresponding identity labels.
        """
        valid_extensions = ('.jpg', '.jpeg', '.png')
        embeddings = []
        labels = []
        
        # Iterate over each person's folder.
        for person_dir in self.dataset_dir.iterdir():
            if not person_dir.is_dir():
                continue
            person = person_dir.name
            # Process each valid image file in the folder.
            for img_path in person_dir.glob("*"):
                if img_path.suffix.lower() in valid_extensions:
                    try:
                        reps = DeepFace.represent(
                            img_path=str(img_path),
                            model_name=model_name,
                            detector_backend=detector_backend
                        )
                        # Take the first embedding from the image.
                        embeddings.append(reps[0]["embedding"])
                        labels.append(person)
                        logger.info(f"Processed: {img_path}")
                    except Exception as e:
                        logger.error(f"Error processing {img_path}: {e}")
                        
        if len(embeddings) == 0:
            raise ValueError("No embeddings were extracted. Check your dataset and paths.")
        
        return np.array(embeddings), np.array(labels)

    def train_per_face_classifiers(self, embeddings, labels):
        """
        Trains one binary classifier (one-vs-all) per identity and saves each model
        as a joblib file in the classifiers folder.
        """
        unique_ids = np.unique(labels)
        for identity in unique_ids:
            # Positive samples: embeddings with this identity.
            pos_idx = labels == identity
            # Negative samples: embeddings from all other identities.
            neg_idx = labels != identity

            X_pos = embeddings[pos_idx]
            y_pos = np.ones(len(X_pos))          # Label '1' for positive samples
            X_neg = embeddings[neg_idx]
            y_neg = np.zeros(len(X_neg))         # Label '0' for negative samples
            
            # Combine the samples.
            X = np.concatenate([X_pos, X_neg], axis=0)
            y = np.concatenate([y_pos, y_neg], axis=0)
            
            # Train an SVM classifier with probability estimation.
            classifier = SVC(kernel="linear", probability=True)
            classifier.fit(X, y)
            
            # Save the trained classifier.
            save_path = self.classifiers_path / f"{identity}_classifier.joblib"
            joblib.dump(classifier, save_path)
            logger.info(f"Trained and saved classifier for {identity} at {save_path}")

    def train(self):
        try:
            embeddings, labels = self.load_dataset()
            self.train_per_face_classifiers(embeddings, labels)
            return True
        except Exception as e:
            logger.error(str(e))
            return False

