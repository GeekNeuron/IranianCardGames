import random
from game_basics import Card, Player, Deck, RANKS

class BibiSalamGame:
    """
    موتور و منطق اصلی بازی بی‌بی سلام.
    """
    SUIT_ORDER = ['♠️', '♥️', '♣️', '♦️']

    def __init__(self, num_players=3, difficulty='medium'):
        if num_players < 2:
            raise ValueError("تعداد بازیکنان باید حداقل ۲ نفر باشد.")

        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        deck = Deck()
        deck.shuffle()
        self._deal_all_cards(deck)

        self.current_suit_index = 0
        self.current_rank_index = RANKS.index('A') # Start with Ace
        self.center_pile = []
        self.is_game_over = False
        self.winner = None

    def _deal_all_cards(self, deck: Deck):
        """تمام کارت‌های دسته را بین بازیکنان پخش می‌کند."""
        player_index = 0
        while len(deck) > 0:
            player = self.players[player_index]
            player.add_card(deck.deal())
            player_index = (player_index + 1) % len(self.players)

    def get_card_to_play(self) -> Card | None:
        """کارت مورد نیاز بعدی را برمی‌گرداند."""
        if self.current_suit_index >= len(self.SUIT_ORDER):
            return None
        suit = self.SUIT_ORDER[self.current_suit_index]
        rank = RANKS[self.current_rank_index]
        return Card(suit, rank)

    def find_player_with_card(self, card_to_find: Card) -> Player | None:
        """بازیکنی که کارت مورد نظر را دارد، پیدا می‌کند."""
        if not card_to_find: return None
        for player in self.players:
            if card_to_find in player.hand:
                return player
        return None

    def _advance_to_next_card(self):
        """وضعیت را برای مشخص کردن کارت بعدی به‌روز می‌کند."""
        self.current_rank_index += 1
        if self.current_rank_index >= len(RANKS):
            self.current_rank_index = 0
            self.current_suit_index += 1
            # Wrap around from K to A
            if self.current_rank_index == 0:
                self.current_rank_index = RANKS.index('A')

    def _handle_salam_penalty(self, player_who_played_q: Player, human_was_slow=False):
        """رویداد 'بی‌بی سلام' و جریمه را مدیریت می‌کند."""
        if human_was_slow:
            loser = self.players[0]
        else:
            potential_losers = [p for p in self.players if p != player_who_played_q]
            if not potential_losers: return
            loser = random.choice(potential_losers)
        
        print(f"{loser.name} در سلام کردن کند بود و جریمه شد!")
        loser.hand.extend(self.center_pile)
        self.center_pile = []

    def play_next_card(self) -> Player:
        """
        یک حرکت در بازی را اجرا می‌کند و بازیکنی که بازی کرده را برمی‌گرداند.
        """
        if self.is_game_over:
            return None

        card_needed = self.get_card_to_play()
        if not card_needed:
            self.is_game_over = True
            return None

        player_with_card = self.find_player_with_card(card_needed)

        if player_with_card:
            player_with_card.hand.remove(card_needed)
            self.center_pile.append(card_needed)
            
            if not player_with_card.hand:
                self.is_game_over = True
                self.winner = player_with_card
                return player_with_card

            self._advance_to_next_card()
            return player_with_card
        else:
            # This case shouldn't happen if all cards are in play
            self._advance_to_next_card()
            return None
