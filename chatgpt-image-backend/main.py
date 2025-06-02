# import torch
# from diffusers import FluxPipeline

# pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", torch_dtype=torch.bfloat16)
# pipe.enable_model_cpu_offload() #save some VRAM by offloading the model to CPU. Remove this if you have enough GPU power

# prompt = "A cat holding a sign that says hello world"
# image = pipe(
#     prompt,
#     height=1024,
#     width=1024,
#     guidance_scale=3.5,
#     num_inference_steps=50,
#     max_sequence_length=512,
#     generator=torch.Generator("cpu").manual_seed(0)
# ).images[0]
# image.save("flux-dev.png")

# from diffusers import DiffusionPipeline

# pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
# pipe.load_lora_weights("ZB-Tech/Text-to-Image")

# prompt = "Draw a picture of two female boxers fighting each other."
# image = pipe(prompt).images[0]
# image.save("flux-dev.png")


# from dotenv import load_dotenv
# import fal_client

# # Load variables from .env into environment
# load_dotenv()

# # Now this will work because FAL_KEY is available
# result = fal_client.subscribe(
#     "fal-ai/flux/schnell",
#     arguments={
#         "prompt": "Astronaut riding a horse",
#     },
# )

# print(result)

# Audio to text 
from faster_whisper import WhisperModel

model = WhisperModel("base")
segments, info = model.transcribe("voice.mp3")
for segment in segments:
    print(segment.text)
# print(segment.audio)  # This is a numpy array