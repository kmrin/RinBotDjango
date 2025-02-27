import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .paths import Path


class _Status(BaseModel):
    language: str
    interval: int
    log: bool


class _AutoKick(BaseModel):
    enabled: bool
    warn_limit: int


class _SpamFilterActions(BaseModel):
    mute: bool
    warn: bool
    kick: bool


class _SpamFilter(BaseModel):
    enabled: bool
    time_window: int
    max_per_window: int
    actions: _SpamFilterActions


class _Danbooru(BaseModel):
    enabled: bool
    api_key: Optional[str] = None


class _Rule34(BaseModel):
    enabled: bool
    api_key: Optional[str] = None


class _E621(BaseModel):
    enabled: bool
    api_key: Optional[str] = None


class _NSFWExtensions(BaseModel):
    danbooru: _Danbooru
    rule34: _Rule34
    e621: _E621


class _Lavalink(BaseModel):
    host: str
    port: int
    password: str


class Config(BaseModel):
    version: str
    debug: bool
    forward_discord_logs: bool
    status: _Status
    auto_kick: _AutoKick = Field(alias="auto-kick")
    spam_filter: _SpamFilter = Field(alias="spam-filter")
    nsfw_extensions: _NSFWExtensions = Field(alias="nsfw-extensions")
    lavalink: _Lavalink
    tasks: List[str]
    internal_extensions: List[str] = Field(alias="internal-extensions")
    intents: Dict[str, bool]


def load_config() -> Config:
    try:
        with open(Path.CONFIG.value, encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f)

        if not data:
            raise ValueError("Config file is empty or invalid")

        return Config.model_validate(data)
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {Path.CONFIG.value}")
    
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML configuration: {e}")
    
    except Exception as e:
        raise ValueError(f"Error loading configuration: {e}")


conf = load_config()
