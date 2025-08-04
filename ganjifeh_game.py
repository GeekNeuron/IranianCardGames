import random

class Player:
    """یک کلاس ساده برای بازیکن که در این فایل استفاده می‌شود."""
    def __init__(self, name):
        self.name = name
        self.hand = []
    def __repr__(self):
        return self.name
    def add_card(self, card):
        if card: self.hand.append(card)

class GanjifehCard:
    """یک کارت گنجفه با خال و رتبه مخصوص به خود."""
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    def __repr__(self):
        return f"{self.rank} {self.suit}"
    def __eq__(self, other):
        return isinstance(other, GanjifehCard) and self.rank == other.rank and self.suit == other.suit
    def __hash__(self):
        return hash((self.rank, self.suit))

class GanjifehGame:
    """
    موتور و منطق یک بازی ساده شده با کارت‌های گنجفه (سبک حکم).
    """
    SUITS = ["شمشیر", "اشرفی", "چنگ", "برات", "تاج", "قماش", "غلام", "سکه"]
    RANKS = ["۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹", "۱۰", "وزیر", "شاه"]
    RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}

    def __init__(self, num_players=4, difficulty='medium'):
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        self.deck = self._create_ganjifeh_deck()
        random.shuffle(self.deck)

        self.teams = {
            "تیم ۱": [self.players[0], self.players[2]],
            "تیم ۲": [self.players[1], self.players[3]]
        }
        self.team_trick_wins = {"تیم ۱": 0, "تیم ۲": 0}

        self.current_player_index = 0
        self.hokm_suit = None
        self.trick_cards = []

        self._deal_cards(8)
        self._determine_hokm()

    def _create_ganjifeh_deck(self) -> list[GanjifehCard]:
        return [GanjifehCard(s, r) for s in self.SUITS for r in self.RANKS]

    def _deal_cards(self, num_cards: int):
        for _ in range(num_cards):
            for player in self.players:
                if self.deck:
                    player.add_card(self.deck.pop())

    def _determine_hokm(self):
        hakem = self.players[0]
        suit_counts = {suit: 0 for suit in self.SUITS}
        for card in hakem.hand:
            suit_counts[card.suit] += 1
        self.hokm_suit = max(suit_counts, key=suit_counts.get) if hakem.hand else random.choice(self.SUITS)

    def _get_valid_moves(self, player: Player) -> list[GanjifehCard]:
        if not self.trick_cards:
            return player.hand
        
        lead_suit = self.trick_cards[0][1].suit
        hand_suits = [c.suit for c in player.hand]
        
        if lead_suit in hand_suits:
            return [c for c in player.hand if c.suit == lead_suit]
        else:
            return player.hand

    def _determine_trick_winner(self) -> Player:
        if not self.trick_cards: return None
        lead_suit = self.trick_cards[0][1].suit
        
        hokm_cards_in_trick = [(p, c) for p, c in self.trick_cards if c.suit == self.hokm_suit]
        
        if hokm_cards_in_trick:
            winner_player, _ = max(hokm_cards_in_trick, key=lambda item: self.RANK_VALUES[item[1].rank])
        else:
            lead_suit_cards = [(p, c) for p, c in self.trick_cards if c.suit == lead_suit]
            winner_player, _ = max(lead_suit_cards, key=lambda item: self.RANK_VALUES[item[1].rank])
        
        return winner_player

    def ai_choose_card(self, player: Player) -> GanjifehCard:
        valid_moves = self._get_valid_moves(player)
        if not valid_moves: return None
        
        if self.difficulty == 'easy':
            return random.choice(valid_moves)
        else: # Medium / Hard
            return max(valid_moves, key=lambda c: self.RANK_VALUES[c.rank])
