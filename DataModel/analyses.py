
from datetime import datetime
from typing import Any
from svaeva.Paths.MultiAPI.Models import DataModel

class analyses(DataModel):
    def __init__(self, token):
        self.start(token)
    
    def store(self,data,skeleton,config=None,user=False):
        deploy_data = data["deploy_data"]
        direction = "model_to_user"
        if user:
            direction = "user_to_model"
        if deploy_data is None:
            deploy_data = datetime.now()
        
        action = {
            "model_id": self.name,
            "skeleton_id": skeleton,
            "config_id": config,
            "user_id": data["sender"],
            "direction": direction,
            "content_data": data[data["type"]],
            "content_text": str(data[data["type"]]),
            "platform": data["platform"],
            "status_message" : "pending",
            "deploy_data" : deploy_data
        }
        self.svaeva.database.actions.add(action)
        self.logger.debug("Action added: %s",action)

    def forward(self,data : Any):
        self.store(data=data,skeleton="open_ai",config=None,user=True)