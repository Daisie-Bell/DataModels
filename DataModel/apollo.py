import json
from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any

class apollo(DataModel):

    def __init__(self,token):
        super().__init__(token)
        self.add_model("open_ai")
        self.add_model("deepgram")
        self.add_model("elevanlabs")
        self.load_wallet()
        self.load_config("auto_deep")
        self.load_config("voice_rachel_elevanlabs")

    def forward(self,data : Any) -> Any:
        if data["type"] == "websocket.receive":
            data = json.loads(data["text"])
        if data is None:
            return "I don't understand"
        output = {
            "sender":data["sender"],
            "type":"text",
            "text": None,
            "platform": data["platform"],
        }
        if data["type"] == "voice":
            # Voice to text
            config = self.configs["auto_deep"]
            deep_reply = self.ai_models["deepgram"].pre_recode(params=config,json={"url":data["voice"]})
            data["text"] = deep_reply.json()
            data["text"] = data["text"]["results"]["channels"][0]
            data["text"] = data["text"]["alternatives"][0]
            data["text"] = data["text"]["transcript"]
            output["text"] = data["text"]
            self.store(data=data,skeleton="deepgram",config=config["id"],user=False)
            # Text to text
            open_reply_text = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=output)
            # Text to speech
            audio_reply = self.ai_models["elevanlabs"].text_to_speech(url_params=self.configs["voice_rachel_elevanlabs"]["config"]["url_params"],json={"text":open_reply_text})
            output["type"] = "voice"
            output["voice"] = audio_reply.json()["url"]
            self.store(data=output,skeleton="elevanlabs",config=self.configs["voice_rachel_elevanlabs"]["id"],user=False)
            return output["text"]
        elif data["type"] == "text":
            output["text"] = data["text"]
            self.store(data=data,skeleton="open_ai",config=None,user=False)
            open_reply_text = self.svaeva.multi_api.forward.send(model_id="costume_llm",input_data=output)
            output["text"] = open_reply_text
            return output["text"]
        return "I don't understand"