from typing import List, Tuple
from client.hendrik.http_requests import Match, Player

class LambdaResponse:
    def __init__(self, results: List[Tuple[Match, Player]]):
        self.results = results

    def json(self):
        matches = []
        for result in self.results:
            item = {
                'match': result[0].json(),
                'player': result[1].json()
            }
            matches.append(item)
        return {
            'matches': matches
        }