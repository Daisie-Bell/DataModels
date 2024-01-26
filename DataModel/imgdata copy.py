import json

from PIL import Image
import io

import requests

from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any

class imgdata(DataModel):

    def __init__(self,token):
        self.start(token)
        self.add_model("open_ai")
        self.load_wallet()

    
    def resize_image_with_bytes_limit(self,image_bytes, max_size,rgb=False):
        # Open the image from bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Resize the image while maintaining the aspect ratio
        image.thumbnail(max_size)
        if rgb:
            image = image.convert('RGBA')

        # Save the resized image to bytes
        output_bytes = io.BytesIO()
        image.save(output_bytes, format='PNG')  # Adjust the format as needed

        return output_bytes.getvalue()

    def forward(self,data : Any) -> Any:
        if data["type"] == "websocket.receive":
            data = json.loads(data["text"])
        if data is None:
            return "I don't understand"
        output = {
            "sender":data["sender"],
            "type":"img",
            "text": None,
            "platform": data["platform"],
        }
        max_image_size = (500, 500)  # Adjust the dimensions as needed
        if data["type"] == "(img/text)2img":

            # Voice to text
            edit_config = {
                "image": self.resize_image_with_bytes_limit(requests.get(data["(img/text)2img"]).content,max_image_size,True)
            }
            params = {
                "prompt" : data["text"],
                "model":"dall-e-2",
                "n": 1
            }
            reply = self.ai_models["open_ai"].image2image(data=params,files=edit_config).json()
            print(reply)
            return reply["data"][0]["url"]
        elif data["type"] == "img2img":

            # Variation
            variantio_config = {
                "image": self.resize_image_with_bytes_limit(requests.get(data["img2img"]).content,max_image_size)
            }
            params = {
                "model":"dall-e-2",
                "n": 1
            }
            # Assuming you have the image bytes in a variable named 'image_bytes'
            reply = self.ai_models["open_ai"].images2images(data=params,files=variantio_config).json()
            return reply["data"][0]["url"]
        elif data["type"] == "text":
            # Text to image
            edit_config = {
                "model" : "dall-e-3",
                "prompt": data["text"],
                "quality": "standard",
                "n": 1
            }
            reply = self.ai_models["open_ai"].text2image(json=edit_config).json()
            return reply["data"][0]["url"]
        return "I don't understand"