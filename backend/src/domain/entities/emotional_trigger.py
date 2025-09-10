from pydantic import BaseModel


class EmotionalTrigger(BaseModel):
    name: str

    class Config:
        extra = 'forbid'
