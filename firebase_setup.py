"""
Firebase Admin SDK initialization and configuration.
This module handles Firebase connection and provides database abstractions.
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from firebase_admin.exceptions import FirebaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FirebaseManager:
    """Manages Firebase connection and provides database operations."""
    
    _initialized = False
    _db = None
    
    @classmethod
    def initialize(cls, credential_path: Optional[str] = None) -> None:
        """
        Initialize Firebase Admin SDK.
        
        Args:
            credential_path: Path to Firebase service account JSON file.
                           If None, uses environment variables.
        
        Raises:
            FirebaseError: If initialization fails
            ValueError: If credentials are invalid
        """
        if cls._initialized:
            logger.info("Firebase already initialized")
            return
            
        try:
            if credential_path and Path(credential_path).exists():
                # Load from file
                cred = credentials.Certificate(credential_path)
                logger.info(f"Loaded Firebase credentials from {credential_path}")
            else:
                # Load from environment variables
                firebase_config = {
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                }
                
                # Validate required environment variables
                required_vars = ["FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", 
                               "FIREBASE_CLIENT_EMAIL"]
                missing_vars = [var for var in required_vars if not os.getenv(var)]
                if missing_vars:
                    raise ValueError(f"Missing environment variables: {missing_vars}")
                
                cred = credentials.Certificate(firebase_config)
                logger.info("Loaded Firebase credentials from environment variables")
            
            # Initialize Firebase
            app = initialize_app(cred)
            cls._db = firestore.client(app)
            cls._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise FirebaseError(f"Firebase initialization failed: {str(e)}")
    
    @classmethod
    def get_db(cls) -> firestore.Client:
        """
        Get Firestore database instance.
        
        Returns:
            firestore.Client: Firestore database instance
            
        Raises:
            RuntimeError: If Firebase is not initialized
        """
        if not cls._initialized or cls._db is None:
            raise RuntimeError("Firebase not initialized. Call initialize() first.")
        return cls._db
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Check if Firebase is initialized."""
        return cls._initialized


def test_firebase_connection() -> bool:
    """
    Test Firebase connection by performing a simple read operation.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        if not FirebaseManager.is_initialized():
            FirebaseManager.initialize()
        
        db = FirebaseManager.get_db()
        # Try to read a non-existent document to test connection
        doc_ref = db.collection("_test").document("connection_test")
        doc_ref.get()
        logger.info("Firebase connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Firebase connection test failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Test the Firebase setup
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        success = test_firebase_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        sys.exit(1)