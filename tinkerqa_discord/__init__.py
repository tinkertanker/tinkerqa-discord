from collections import namedtuple

from .TinkerQaDiscord import TinkerQaDiscord

Config = namedtuple("Config", ["guild", "qa_channel", "helper_role"])