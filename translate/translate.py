import starlette

from transformers import pipeline

from ray import serve


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
class Translator:
    def __init__(self):
        self.model = pipeline("translation_en_to_de", model="t5-small")

    def translate(self, text: str) -> str:
        return self.model(text)[0]["translation_text"]

    async def __call__(self, req: starlette.requests.Request):
        req = await req.json()
        return self.translate(req["text"])


app = Translator.options(route_prefix="/translate").bind()