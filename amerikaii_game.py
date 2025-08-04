import random
from game_basics import Card, Player, Deck, SUITS

class AmerikaiiGame:
    """
    موتور و منطق اصلی بازی آمریکایی (Crazy Eights).
    """
    def __init__(self, num_players=3, difficulty='medium'):
        if num_players < 2:
            raise ValueError("تعداد بازیکنان باید حداقل ۲ نفر باشد.")
        
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        self.draw_pile = Deck()
        self.draw_pile.shuffle()
        self.discard_pile = []

        self.current_player_index = 0
        self.play_direction = 1
        self.is_game_over = False
        self.winner = None
        self.declared_suit = None

        self._initial_setup()

    def _initial_setup(self):
        """کارت‌های اولیه را پخش کرده و بازی را آماده می‌کند."""
        for player in self.players:
            for _ in range(7):
                player.add_card(self.draw_pile.deal())
        
        start_card = self.draw_pile.deal()
        while start_card.rank == '8': # The first card cannot be a wild card
             self.draw_pile.cards.append(start_card)
             self.draw_pile.shuffle()
             start_card = self.draw_pile.deal()
        self.discard_pile.append(start_card)

    def top_card(self) -> Card:
        """کارت رویی دسته بازی‌شده را برمی‌گرداند."""
        return self.discard_pile[-1] if self.discard_pile else None

    def _is_move_valid(self, card: Card) -> bool:
        """بررسی می‌کند آیا بازی کردن یک کارت مجاز است یا خیر."""
        top = self.top_card()
        if not top: return True

        if self.declared_suit:
            return card.suit == self.declared_suit or card.rank == '8'
        
        if card.rank == '8':
            return True
        
        return card.rank == top.rank or card.suit == top.suit

    def _advance_turn(self):
        """نوبت را بر اساس جهت فعلی بازی به بازیکن بعدی منتقل می‌کند."""
        self.current_player_index = (self.current_player_index + self.play_direction) % len(self.players)
    
    def _apply_draw_penalty(self, num_cards: int):
        """بازیکن بعدی را مجبور به کشیدن تعدادی کارت جریمه می‌کند."""
        target_player_index = (self.current_player_index + self.play_direction) % len(self.players)
        target_player = self.players[target_player_index]
        for _ in range(num_cards):
            if len(self.draw_pile) == 0: self._refill_draw_pile()
            if len(self.draw_pile) > 0:
                target_player.add_card(self.draw_pile.deal())

    def play_turn(self, player: Player, card: Card, declared_suit: str = None):
        """یک نوبت بازی را اجرا می‌کند: کارت را بازی کرده و اثر آن را اعمال می‌کند."""
        if player != self.players[self.current_player_index] or not self._is_move_valid(card):
            return

        player.hand.remove(card)
        self.discard_pile.append(card)
        self.declared_suit = None

        if not player.hand:
            self.is_game_over = True
            self.winner = player
            return

        if card.rank == '8':
            self.declared_suit = declared_suit
            self._advance_turn()
        elif card.rank == 'Q':
            self._advance_turn()
            self._advance_turn()
        elif card.rank == 'A':
            self.play_direction *= -1
            self._advance_turn()
        elif card.rank == '2':
            self._apply_draw_penalty(2)
            self._advance_turn()
        else:
            self._advance_turn()

    def player_must_draw(self, player: Player) -> Card:
        """وقتی بازیکن کارتی برای بازی ندارد، یک کارت می‌کشد."""
        if len(self.draw_pile) == 0:
            self._refill_draw_pile()
            if len(self.draw_pile) == 0:
                self._advance_turn()
                return None
            
        drawn_card = self.draw_pile.deal()
        player.add_card(drawn_card)
        
        if not self._is_move_valid(drawn_card):
            self._advance_turn()
        
        return drawn_card

    def _refill_draw_pile(self):
        """دسته دور ریخته شده را بُر زده و به دسته کشیدنی اضافه می‌کند."""
        if not self.discard_pile or len(self.discard_pile) <= 1:
            return
        
        top = self.discard_pile.pop()
        cards_to_shuffle = self.discard_pile[:]
        self.discard_pile = [top]
        random.shuffle(cards_to_shuffle)
        self.draw_pile.cards.extend(cards_to_shuffle)

    def ai_choose_card(self, player: Player) -> dict:
        """مغز AI برای انتخاب بهترین حرکت در بازی آمریکایی."""
        valid_moves = [c for c in player.hand if self._is_move_valid(c)]
        if not valid_moves:
            return None

        card_to_play = random.choice(valid_moves)
        declared_suit = None
        if card_to_play.rank == '8':
            from collections import Counter
            suit_counts = Counter(c.suit for c in player.hand if c.rank != '8')
            declared_suit = suit_counts.most_common(1)[0][0] if suit_counts else random.choice(SUITS)
        
        return {'card': card_to_play, 'suit': declared_suit}
