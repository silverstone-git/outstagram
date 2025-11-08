
import boto3
from botocore.client import BaseClient
from botocore.exceptions import NoCredentialsError, ClientError
from os import getenv

from .exceptions import CouldntInitS3

# It's better to fetch these from environment variables
# directly within the function/class that uses them to facilitate testing and dynamic configuration.
S3_REGION = getenv("S3_REGION", "us-east-1")
S3_BUCKET = getenv("S3_BUCKET")
S3_ENDPOINT = getenv("S3_ENDPOINT")


class S3ClientManager:
    """
    A singleton class to manage the Boto3 S3 client instance.
    This avoids globals and handles initialization securely.
    """
    _instance = None
    _client: BaseClient | None = None

    def __new__(cls):
        if cls._instance is None:
            print("Creating new S3ClientManager instance...")
            cls._instance = super(S3ClientManager, cls).__new__(cls)
            cls._initialize_client()
        return cls._instance

    @classmethod
    def _initialize_client(cls):
        """Initializes the Boto3 client without hardcoded credentials."""
        try:
            # The session will automatically pick up credentials from standard locations
            # (IAM role, environment variables, or ~/.aws/credentials)
            # session = boto3.Session()
            
            # Check if credentials are found
            # credentials = session.get_credentials()
            # if credentials is None:
            #     raise NoCredentialsError()

            # The client is created here
            cls._client = boto3.client(
                "s3",
                region_name=S3_REGION,
                endpoint_url=S3_ENDPOINT,
            )
            
            # A simple check to verify credentials and connectivity
            cls._client.list_buckets() 
            print("✅ S3 client initialized and credentials verified successfully.")

        except NoCredentialsError:
            print("❌ Error: AWS credentials not found.")
            raise Exception("Could not find AWS credentials. Configure them via IAM role, env vars, or ~/.aws/credentials.")
        except ClientError as e:
            # Handles errors like "InvalidAccessKeyId"
            print(f"❌ An AWS client error occurred: {e}")
            raise Exception("Invalid AWS credentials or insufficient permissions.")
        except Exception as e:
            print(f"❌ An unexpected error occurred during S3 client initialization: {e}")
            raise

    @classmethod
    def get_client(cls) -> BaseClient:
        """Returns the initialized S3 client."""
        if cls._instance is None:
            cls.__new__(cls)

        if cls._client is not None:
            return cls._client
        else:
            raise CouldntInitS3

    @classmethod
    def get_bucket(cls):
        return S3_BUCKET
