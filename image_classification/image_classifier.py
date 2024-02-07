import requests
import starlette
from transformers import pipeline
from io import BytesIO
from PIL import Image
from ray import serve
from ray.serve.handle import DeploymentHandle


@serve.deployment
def downloader(image_url: str):
    image_bytes = requests.get(image_url).content
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return image

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
class ImageClassifier:
    def __init__(self, downloader: DeploymentHandle):
        self.downloader = downloader
        self.model = pipeline(
            "image-classification", model="google/vit-base-patch16-224"
        )

    async def classify(self, image_url: str) -> str:
        image = await self.downloader.remote(image_url)
        results = self.model(image)
        return results[0]["label"]

    async def __call__(self, req: starlette.requests.Request):
        req = await req.json()
        return await self.classify(req["image_url"])


app = ImageClassifier.options(route_prefix="/imageclassify").bind(downloader.bind())