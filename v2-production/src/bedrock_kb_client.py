from typing import Dict, List

import boto3
from config import config


class BedrockKBClient:
    def __init__(self):
        self.client = boto3.client(
            "bedrock-agent-runtime", region_name=config.AWS_REGION
        )
        self.kb_id = config.KNOWLEDGE_BASE_ID

    def retrieve(self, query: str, max_results: int = 5) -> List[Dict]:
        response = self.client.retrieve(
            knowledgeBaseId=self.kb_id,
            retrievalQuery={"text": query},
            retrievalConfiguration={
                "vectorSearchConfiguration": {"numberOfResults": max_results}
            },
        )

        return response["retrievalResults"]

    def retrieve_and_generate(self, query: str) -> Dict:
        response = self.client.retrieve_and_generate(
            input={"text": query},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": self.kb_id,
                    "modelArn": f"arn:aws:bedrock:{config.AWS_REGION}::foundation-model/{config.MODEL_ID}",
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "numberOfResults": config.MAX_RESULTS
                        }
                    },
                },
            },
        )

        return {
            "answer": response["output"]["text"],
            "citations": response.get("citations", []),
            "session_id": response.get("sessionId"),
        }


if __name__ == "__main__":
    client = BedrockKBClient()
    result = client.retrieve_and_generate(
        "What are LG Energy Solution's main products?"
    )

    print("Answer:", result["answer"])
    print("\nCitations:", len(result["citations"]))
