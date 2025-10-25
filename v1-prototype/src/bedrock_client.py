import os
from typing import Optional

import boto3
from dotenv import load_dotenv
from langchain_aws import BedrockEmbeddings, ChatBedrock

load_dotenv()


class BedrockClientManager:
    def __init__(self, region_name: Optional[str] = None):
        self.region_name = region_name or os.getenv("AWS_REGION", "us-east-1")

        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime", region_name=self.region_name
        )

        print(f"✅ Bedrock client initialized (region: {self.region_name})")

    def get_embeddings(self, model_id: Optional[str] = None):
        model_id = model_id or os.getenv(
            "EMBEDDING_MODEL", "amazon.titan-embed-text-v1"
        )

        embeddings = BedrockEmbeddings(client=self.bedrock_client, model_id=model_id)

        print(f"✅ Embeddings model loaded: {model_id}")
        return embeddings

    def get_llm(
        self, model_id: Optional[str] = None, streaming: bool = False, **kwargs
    ):
        model_id = model_id or os.getenv("LLM_MODEL", "amazon.titan-text-express-v1")

        if "claude" in model_id.lower():
            default_kwargs = {"max_tokens": 512, "temperature": 0.1, "top_p": 0.9}
        elif "titan" in model_id.lower():
            default_kwargs = {
                "maxTokenCount": 512,
                "temperature": 0.1,
                "stopSequences": [],
            }
        else:
            default_kwargs = {"max_tokens": 512, "temperature": 0.1}

        default_kwargs.update(kwargs)

        llm = ChatBedrock(
            client=self.bedrock_client,
            model_id=model_id,
            model_kwargs=default_kwargs,
            streaming=streaming,
        )

        print(f"✅ LLM loaded: {model_id}")
        return llm


if __name__ == "__main__":
    client = BedrockClientManager()
    embeddings = client.get_embeddings()
    llm = client.get_llm()

    test_text = "Hello, this is a test."
    vector = embeddings.embed_query(test_text)
    print(f"\nEmbedding test:")
    print(f"Vector dimension: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")

    from langchain.schema import HumanMessage

    response = llm.invoke([HumanMessage(content="Say hello in one sentence.")])
    print(f"\nLLM test:")
    print(f"Response: {response.content}")
