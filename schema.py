from datetime import datetime
from time import timezone

from dhi import BaseModel, ConfigDict


class Response(BaseModel):
	status_code: int
	project: str
	current_time: datetime

	model_config = ConfigDict(from_attributes=True)