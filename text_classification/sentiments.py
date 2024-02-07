import starlette
from transformers import pipeline
from ray import serve
import torch

@serve.deployment(
    ray_actor_options={"num_cpus": 0.5},
    max_concurrent_queries=5,
    autoscaling_config={
        "target_num_ongoing_requests_per_replica": 1,
        "min_replicas": 1,
        "initial_replicas": 1,
        "max_replicas": 200,
    },
)
class Sentiment:
    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased",
            framework="pt",
            # Transformers requires you to pass device with index
            device=torch.device("cpu"),
        )

    def classify(self, sentence: str):
        return self.classifier(sentence)

    async def __call__(self, req: starlette.requests.Request):
        req = await req.json()
        return self.classify(req["text"])

app = Sentiment.options(route_prefix="/textclassify").bind()