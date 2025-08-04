import random
from game_basics import Card, Deck, Player, RANK_VALUES

class HokmGame:
    def __init__(self, num_players=4, difficulty='medium'):
        self.num_players = num_players
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        self.deck = Deck()
        self.deck.shuffle()
        
        self.hakem = None
        self.hokm_suit = None
        self.current_player_index = 0
        self.trick_cards = []  # لیستی از تاپل‌های (player, card)
        self.is_round_over = False
        self.is_game_over = False
        
        self.trick_scores = {"تیم ۱": 0, "تیم ۲": 0}
        self.team_scores = {"تیم ۱": 0, "تیم ۲": 0}

        if self.num_players == 4:
            self.teams = {"تیم ۱": [self.players[0], self.players[2]], "تیم ۲": [self.players[1], self.players[3]]}
        elif self.num_players == 2:
            self.teams = {"تیم ۱": [self.players[0]], "تیم ۲": [self.players[1]]}
        
        self._start_new_round()

    def _start_new_round(self):
        # ریست کردن متغیرهای دور
        self.deck = Deck()
        self.deck.shuffle()
        for p in self.players:
            p.hand = []
        self.trick_scores = {"تیم ۱": 0, "تیم ۲": 0}
        self.trick_cards = []
        self.is_round_over = False
        
        self._deal_cards_for_hakem()
        self._determine_hakem()

    def _deal_cards_for_hakem(self):
        for _ in range(5):
            for player in self.players:
                player.add_card(self.deck.deal())

    def _determine_hakem(self):
        # در بازی دو نفره، بازیکن اول حاکم است
        if self.num_players == 2:
            self.hakem = self.players[0]
            self.current_player_index = 0
            return

        # در بازی چهار نفره، بر اساس آس
        card_order = []
        for i in range(5):
            for p_idx, p in enumerate(self.players):
                card_order.append((p, p.hand[i]))
        
        for p, card in card_order:
            if card.rank == 'A':
                self.hakem = p
                self.current_player_index = self.players.index(p)
                return
        
        # اگر کسی آس نداشت
        self.hakem = self.players[0]
        self.current_player_index = 0
        
    def set_hokm(self, suit):
        self.hokm_suit = suit
        self._deal_remaining_cards()

    def _deal_remaining_cards(self):
        num_remaining = 13 - len(self.players[0].hand)
        for _ in range(num_remaining):
            for player in self.players:
                player.add_card(self.deck.deal())

    def _get_valid_moves(self, player: Player) -> list[Card]:
        if not self.trick_cards:
            return player.hand
        
        lead_suit = self.trick_cards[0][1].suit
        hand_suits = [c.suit for c in player.hand]
        
        if lead_suit in hand_suits:
            return [c for c in player.hand if c.suit == lead_suit]
        else:
            return player.hand

    def _determine_trick_winner(self) -> Player:
        if not self.trick_cards:
            return None
            
        lead_suit = self.trick_cards[0][1].suit
        
        hokm_cards_in_trick = [(p, c) for p, c in self.trick_cards if c.suit == self.hokm_suit]
        
        if hokm_cards_in_trick:
            winner_player, winning_card = max(hokm_cards_in_trick, key=lambda item: RANK_VALUES[item[1].rank])
        else:
            lead_suit_cards = [(p, c) for p, c in self.trick_cards if c.suit == lead_suit]
            winner_player, winning_card = max(lead_suit_cards, key=lambda item: RANK_VALUES[item[1].rank])
        
        return winner_player

    def ai_choose_card(self, player: Player) -> Card:
        valid_moves = self._get_valid_moves(player)
        
        if self.difficulty == 'easy':
            return random.choice(valid_moves)
        
        elif self.difficulty == 'medium' or self.difficulty == 'hard':
            # استراتژی ساده: بالاترین کارت مجاز را بازی می‌کند
            return max(valid_moves, key=lambda c: RANK_VALUES.get(c.rank, 0))
        
        return random.choice(valid_moves)
