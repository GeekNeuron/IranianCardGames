import random
from game_basics import Card, Player, Deck, SUITS, RANKS

class ShelemDeck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        self.shuffle()
    def shuffle(self):
        random.shuffle(self.cards)
    def deal(self):
        return self.cards.pop() if self.cards else None
    def __len__(self):
        return len(self.cards)

class ShelemGame:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(4)]
        self.teams = {"تیم ۱": [self.players[0], self.players[2]], "تیم ۲": [self.players[1], self.players[3]]}
        self.deck = ShelemDeck()
        self.kitty = []
        
        self.hakem = None
        self.hokm_suit = None
        self.bids = {}
        self.highest_bid = 100
        self.bid_winner = None
        
        self.bidding_turn_index = 0
        self.players_in_bid = self.players[:]
        self.current_player_index = 0
        self.trick_cards = []
        
        self.team_scores = {"تیم ۱": 0, "تیم ۲": 0}
        self.collected_cards = {"تیم ۱": [], "تیم ۲": []}
        
    def _deal_initial_cards(self):
        for _ in range(12):
            for player in self.players:
                player.add_card(self.deck.deal())
        self.kitty = [self.deck.deal() for _ in range(4)]

    def _estimate_hand_value(self, player: Player) -> int:
        value = 0
        for card in player.hand:
            if card.rank in ['A', '10']: value += 10
            elif card.rank == '5': value += 5
            elif card.rank in ['K', 'Q']: value += 3
        return int(round(value / 5.0)) * 5

    def set_hokm_by_suit(self, suit):
        self.hokm_suit = suit
        self.current_player_index = self.players.index(self.hakem)
