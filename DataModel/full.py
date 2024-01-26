import json
from svaeva.Paths.MultiAPI.Models import DataModel

from typing import Any

class apollo(DataModel):

    def __init__(self,token):
        self.start(token)
        self.add_model("open_ai")
        self.add_model("deepgram")
        self.add_model("elevanlabs")
        self.load_wallet()
        self.load_config("auto_deep")
        self.load_config("voice_rachel_elevanlabs")
        self.load_config("vision")

    def build_history(self,config,data):
        model = config["config"]["model"]
        targets = {
            "gpt-4-turbo": 128000,
            "gpt-4-turbo-with-vision": 128000,
            "gpt-4": 8192,
            "gpt-4-0613": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-32k-0613": 32768,
            "gpt-3.5-turbo-1106": 16385,
            "gpt-3.5-turbo": 4096,
            "gpt-3.5-turbo-16k": 16384,
            "gpt-3.5-turbo-instruct": 4097,
            "gpt-3.5-turbo-0613": 4096,
            "gpt-3.5-turbo-16k-0613": 16384,
            "text-davinci-003": 4097,
            "text-davinci-002": 4097,
            "code-davinci-002": 8001
        }
        tokens = 0
        target = targets[model]
        history = self.svaeva.database.actions(user_id=data["sender"],model_id="costume_llm")
        for i in history:
            if i["content_type"] == "str":
                tokens += len(i["content_text"])
                if tokens >= target:
                    break
                agent_type = "assistant"
                if i["direction"] == "user_to_model":
                    agent_type = "user"
                yield {
                    "role":agent_type,
                    "content":i["content_text"]
                }

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
        elif data["type"] == "image":
            # Image to text
            history = self.build_history(config=self.configs["vision"],data=data)
            config = history["messages"].pop(0)
            if "text" in data.keys():
                config["content"][0]["text"] = data["text"]
                config["content"][1]["image_url"] = {
                    "url":data["image"]
                }
            history.append(config)
            reply = self.ai_models["vision"].complete(json=history)
            return reply                
        return "I don't understand"