from channels.generic.websocket import WebsocketConsumer
import json
from random import randint


class WSConsumer(WebsocketConsumer):
    connected_players = {}  # Keeps track of players and their WebSocket instances

    def connect(self):
        self.accept()
        player_id = self.scope['url_route']['kwargs']['player_id']
        numbers = [randint(1, 100) for _ in range(3)]
        self.connected_players[player_id] = {
            'numbers': numbers,
            'websocket': self
        }
        self.send(json.dumps({'your_numbers': numbers}))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        player_id = text_data_json['player_id']
        target_player_id = text_data_json['target_player_id']
        number = text_data_json['number']

        if player_id in self.connected_players and number in self.connected_players[player_id]['numbers']:
            target_player = self.connected_players.get(target_player_id)
            if target_player:
                target_player['websocket'].send(json.dumps({'number_from': player_id, 'number': number}))

    def disconnect(self, close_code):
        player_id = self.scope['url_route']['kwargs']['player_id']
        if player_id in self.connected_players:
            del self.connected_players[player_id]
