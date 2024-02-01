from typing import List, Tuple, Optional
from client.hendrik.http_requests import Match, Player

class LambdaResponse:
    error_msg: Optional[str] = None
    results: Optional[List[Tuple[Match, Player]]] = None

    @classmethod
    def set_results(cls, results: List[Tuple[Match, Player]]):
        cls.results = results

    @classmethod
    def set_error(cls, error_msg: str):
        cls.error_msg = error_msg

    @classmethod
    def json(cls):
        if cls.error_msg:
            return {
                'error': {
                    'message': cls.error_msg
                }
            }
        matches = []
        for result in cls.results:
            item = {
                'match': result[0].json(),
                'player': result[1].json()
            }
            matches.append(item)
        return {
            'matches': matches
        }