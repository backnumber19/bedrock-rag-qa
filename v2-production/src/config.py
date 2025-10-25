import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"WARNING: .env not found at {env_path}")


@dataclass
class Config:
    AWS_REGION: str = os.getenv("AWS_REGION", "us-west-2")
    KNOWLEDGE_BASE_ID: str = os.getenv("KNOWLEDGE_BASE_ID", "")
    DATA_SOURCE_ID: str = os.getenv("DATA_SOURCE_ID", "")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "")

    MODEL_ID: str = "anthropic.claude-3-haiku-20240307-v1:0"
    MAX_RESULTS: int = 5
    LOG_GROUP: str = os.getenv("LOG_GROUP", "/aws/bedrock-rag-qa-v2-west/application")

    def validate(self):
        required = {
            "KNOWLEDGE_BASE_ID": self.KNOWLEDGE_BASE_ID,
            "DATA_SOURCE_ID": self.DATA_SOURCE_ID,
            "S3_BUCKET": self.S3_BUCKET,
        }

        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please copy .env.example to .env and fill in your values."
            )

        print("Configuration loaded successfully")
        return True


config = Config()

if __name__ == "__main__":
    try:
        config.validate()
        print(f"\nConfiguration:")
        print(f"   Region: {config.AWS_REGION}")
        print(f"   Knowledge Base: {config.KNOWLEDGE_BASE_ID}")
        print(f"   Data Source: {config.DATA_SOURCE_ID}")
        print(f"   S3 Bucket: {config.S3_BUCKET}")
    except ValueError as e:
        print(f"\nError: {e}")
