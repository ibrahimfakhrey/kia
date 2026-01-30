import os
import firebase_admin
from firebase_admin import credentials, messaging


class FirebaseService:
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK."""
        if cls._initialized:
            return

        try:
            # Path to service account key file
            # Points to config/firebase-credentials.json in the project root
            cred_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'firebase-credentials.json'
            )

            if not os.path.exists(cred_path):
                print(f"Warning: Firebase credentials not found at {cred_path}")
                return

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            cls._initialized = True
            print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")

    @staticmethod
    def send_notification(token, title, body, data=None):
        """
        Send a notification to a specific device.

        Args:
            token (str): FCM device token
            title (str): Notification title
            body (str): Notification body
            data (dict): Additional data to send with notification

        Returns:
            str: Message ID if successful, None otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='high_importance_channel',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                        ),
                    ),
                ),
            )

            response = messaging.send(message)
            print(f"Successfully sent notification: {response}")
            return response
        except Exception as e:
            print(f"Error sending notification: {e}")
            return None

    @staticmethod
    def send_multicast_notification(tokens, title, body, data=None):
        """
        Send a notification to multiple devices.

        Args:
            tokens (list): List of FCM device tokens
            title (str): Notification title
            body (str): Notification body
            data (dict): Additional data to send with notification

        Returns:
            BatchResponse: Response containing success and failure info
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='high_importance_channel',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                        ),
                    ),
                ),
            )

            response = messaging.send_multicast(message)
            print(f"Successfully sent {response.success_count} notifications")
            if response.failure_count > 0:
                print(f"Failed to send {response.failure_count} notifications")
            return response
        except Exception as e:
            print(f"Error sending multicast notification: {e}")
            return None

    @staticmethod
    def send_to_topic(topic, title, body, data=None):
        """
        Send a notification to a topic.

        Args:
            topic (str): Topic name
            title (str): Notification title
            body (str): Notification body
            data (dict): Additional data to send with notification

        Returns:
            str: Message ID if successful, None otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                topic=topic,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='high_importance_channel',
                    ),
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                        ),
                    ),
                ),
            )

            response = messaging.send(message)
            print(f"Successfully sent topic notification: {response}")
            return response
        except Exception as e:
            print(f"Error sending topic notification: {e}")
            return None
