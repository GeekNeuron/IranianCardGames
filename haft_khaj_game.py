import random
from game_basics import Card, Player, Deck, SUITS

class HaftKhajGame:
    """
    موتور و منطق اصلی بازی هفت خاج (هفت کثیف).
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
        self.declared_suit = None
        self.draw_penalty_stack = 0

        self._initial_setup()

    def _initial_setup(self):
        """کارت‌های اولیه را پخش کرده و بازی را آماده می‌کند."""
        for player in self.players:
            for _ in range(7):
                player.add_card(self.draw_pile.deal())
        
        self.discard_pile.append(self.draw_pile.deal())
        # To simplify, we don't apply the effect of the first card

    def top_card(self) -> Card:
        """کارت رویی دسته بازی‌شده را برمی‌گرداند."""
        return self.discard_pile[-1] if self.discard_pile else None

    def _is_move_valid(self, card: Card) -> bool:
        """بررسی می‌کند آیا بازی کردن یک کارت مجاز است یا خیر."""
        top = self.top_card()
        if not top: return True

        if self.declared_suit:
            return card.suit == self.declared_suit or card.rank == '7'
        
        if card.rank == '7':
            return True
        
        # Stacking rule for 2s
        if top.rank == '2' and self.draw_penalty_stack > 0:
            return card.rank == '2'

        return card.rank == top.rank or card.suit == top.suit

    def _advance_turn(self):
        """نوبت را بر اساس جهت فعلی بازی به بازیکن بعدی منتقل می‌کند."""
        self.current_player_index = (self.current_player_index + self.play_direction) % len(self.players)
    
    def _get_next_player(self):
        next_player_index = (self.current_player_index + self.play_direction) % len(self.players)
        return self.players[next_player_index]

    def _apply_draw_penalty(self):
        """بازیکن بعدی را مجبور به کشیدن کارت‌های جریمه انباشته شده می‌کند."""
        if self.draw_penalty_stack == 0: return

        target_player = self._get_next_player()
        print(f"{target_player.name} باید {self.draw_penalty_stack} کارت بکشد!")
        for _ in range(self.draw_penalty_stack):
            if len(self.draw_pile) == 0: self._refill_draw_pile()
            if len(self.draw_pile) > 0:
                target_player.add_card(self.draw_pile.deal())
        
        self.draw_penalty_stack = 0

    def play_turn(self, player: Player, card: Card, declared_suit: str = None):
        """یک نوبت بازی را اجرا می‌کند: کارت را بازی کرده و اثر آن را اعمال می‌کند."""
        if player != self.players[self.current_player_index] or not self._is_move_valid(card):
            return # Move is invalid

        player.hand.remove(card)
        self.discard_pile.append(card)
        self.declared_suit = None

        if not player.hand:
            self.is_game_over = True
            return

        if card.rank == '2':
            self.draw_penalty_stack += 2
            self._advance_turn()
        elif card.rank == 'K' and card.suit == '♠️':
            self.draw_penalty_stack += 5
            self._advance_turn()
        else:
            if self.draw_penalty_stack > 0:
                self._apply_draw_penalty()
            
            if card.rank == '7':
                self.declared_suit = declared_suit
                self._advance_turn()
            elif card.rank == 'A':
                self._advance_turn() # Skip one player
                self._advance_turn()
            elif card.rank == '8':
                self.play_direction *= -1
                self._advance_turn()
            elif card.rank == '10':
                pass # Do not advance turn, player plays again
            else:
                self._advance_turn()

    def player_must_draw(self, player: Player):
        """وقتی بازیکن کارتی برای بازی ندارد، او را مجبور به کشیدن کارت می‌کند."""
        if self.draw_penalty_stack > 0:
            self._apply_draw_penalty()
            self._advance_turn()
            return
            
        print(f"{player.name} کارتی برای بازی ندارد و باید کارت بکشد...")
        drawn_cards = []
        while True:
            if len(self.draw_pile) == 0: self._refill_draw_pile()
            if len(self.draw_pile) == 0:
                self.is_game_over = True
                break
            
            drawn_card = self.draw_pile.deal()
            player.add_card(drawn_card)
            drawn_cards.append(drawn_card)
            if self._is_move_valid(drawn_card):
                break
        
        self._advance_turn()
        return drawn_cards

    def _refill_draw_pile(self):
        """دسته دور ریخته شده را بُر زده و به دسته کشیدنی اضافه می‌کند."""
        if not self.discard_pile or len(self.discard_pile) <= 1:
            return
        
        top = self.discard_pile.pop()
        cards_to_shuffle = self.discard_pile
        self.discard_pile = [top]
        random.shuffle(cards_to_shuffle)
        self.draw_pile.cards.extend(cards_to_shuffle)

    def ai_choose_card(self, player: Player) -> dict:
        """مغز AI برای انتخاب بهترین حرکت در هفت خاج."""
        valid_moves = [c for c in player.hand if self._is_move_valid(c)]
        if not valid_moves:
            return None # Must draw

        if self.difficulty == 'easy':
            return {'card': random.choice(valid_moves), 'suit': None}
        
        elif self.difficulty == 'medium' or self.difficulty == 'hard':
            # استراتژی متوسط: کارت‌های ویژه را نگه می‌دارد مگر مجبور شود
            # و سعی می‌کند از کارت‌های غیر ویژه خلاص شود.
            non_special_cards = [c for c in valid_moves if c.rank not in ['A', '2', '7', '8', '10', 'K']]
            if non_special_cards:
                card_to_play = random.choice(non_special_cards)
            else:
                card_to_play = random.choice(valid_moves)

            declared_suit = None
            if card_to_play.rank == '7':
                suit_counts = Counter(c.suit for c in player.hand if c.rank != '7')
                if suit_counts:
                    declared_suit = suit_counts.most_common(1)[0][0]
                else:
                    declared_suit = random.choice(SUITS)
            
            return {'card': card_to_play, 'suit': declared_suit}
        
        return {'card': random.choice(valid_moves), 'suit': None}
