import requests
import json
from functools import cache
from typing import List

class _AccountInfoMetadata:
    def __init__(
            self,
            puuid: str,
            region: str,
            account_level: int,
            name: str,
            tag: str,
    ):
        self.puuid = puuid
        self.region = region
        self.level = account_level
        self.username = name
        self.tag = tag

class AccountInfo:
    def __init__(self, username: str, tag: str) -> None:
        self.username: str = username
        self.tag: str = tag
        self.endpoint: str = f'https://api.henrikdev.xyz/valorant/v1/account/{self.username}/{self.tag}'

    @cache
    def get_account_info(self) -> _AccountInfoMetadata:
        response = requests.request('GET', self.endpoint)
        response = json.loads(response.text)['data']
        return _AccountInfoMetadata(
            response['puuid'],
            response['region'],
            response['account_level'],
            response['name'],
            response['tag']
        )

    def get_puuid(self) -> str:
        return self.get_account_info().puuid

class Player:
    def __init__(self, raw_data):
        self.puuid = raw_data['puuid']
        self.username: str = raw_data['name']
        self.tag = raw_data['tag']
        self.character = raw_data['character']
        self.tier = raw_data['currenttier_patched']
        self.kills = raw_data['stats']['kills']
        self.deaths = raw_data['stats']['deaths']
        self.assists = raw_data['stats']['assists']
        self.headshots = raw_data['stats']['headshots']

    def json(self) -> dict:
        return {
            'puuid': self.puuid,
            'username': self.username,
            'tag': self.tag,
            'character': self.character,
            'tier': self.tier,
            'kills': self.kills,
            'deaths': self.deaths,
            'assists': self.assists,
            'headshots': self.headshots
        }

class MatchMetadata:
    def __init__(self, metadata):
        self.map = metadata['map']
        self.game_length = self.__format_game_length(metadata['game_length'])
        self.rounds_played = metadata['rounds_played']
        self.mode = metadata['mode']
        self.match_id = metadata['matchid']
        self.region = metadata['region']
        self.cluster = metadata['cluster']

    def __format_game_length(self, seconds) -> str:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f'{minutes} minutes and {remaining_seconds} seconds'

    def json(self) -> dict:
        return {
            'map': self.map,
            'length': self.game_length,
            'rounds_played': self.rounds_played,
            'game_mode': self.mode,
            'match_id': self.match_id,
            'region': self.region,
            'cluster': self.cluster
        }

class Match:
    def __init__(self, raw_data):
        self.metadata = MatchMetadata(raw_data['metadata'])
        self.players: List[Player] = self.__parse_player_data(raw_data['players']['all_players'])

    def __parse_player_data(self, raw_players) -> list:
        players = []
        for raw_player in raw_players:
            players.append(Player(raw_player))
        return players

    def contains_user(self, username: str) -> Player | None:
        for player in self.players:
            if player.username.lower() == username.lower():
                return player
        return None

    def json(self) -> dict:
        players_list = []
        for player in self.players:
            players_list.append(player.json())
        return {
            'metadata': self.metadata.json(),
            'players': players_list
        }

class UserMatchData:
    def __init__(self, puuid: str):
        self.matches: List[Match] = []
        self.puuid = puuid
        self.endpoint = f'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/na/{self.puuid}'
        self.__get_matches()

    def __get_matches(self):
        response = requests.request('GET', self.endpoint)
        response = json.loads(response.text)
        games = response['data']
        for game in games:
            self.matches.append(Match(game))
