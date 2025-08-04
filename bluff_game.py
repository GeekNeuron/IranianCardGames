import random
from game_basics import Card, Player, Deck, RANKS

class BluffGame:
    """
    موتور و منطق اصلی بازی بلوف (چاخان).
    """
    def __init__(self, num_players=3, difficulty='medium'):
        if num_players < 2:
            raise ValueError("تعداد بازیکنان باید حداقل ۲ نفر باشد.")

        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        deck = Deck()
        deck.shuffle()
        self._deal_all_cards(deck)

        self.center_pile = [] # کارت‌های بازی شده در وسط (به پشت)
        self.current_declared_rank = None # رتبه‌ای که در این دور بازی می‌شود
        self.last_play = None # برای ذخیره آخرین حرکت {player, cards}
        self.current_player_index = 0
        self.is_game_over = False
        self.winner = None

    def _deal_all_cards(self, deck: Deck):
        """تمام کارت‌های دسته را بین بازیکنان پخش می‌کند."""
        player_index = 0
        while len(deck) > 0:
            player = self.players[player_index]
            player.add_card(deck.deal())
            player_index = (player_index + 1) % len(self.players)

    def play_cards(self, player: Player, cards_to_play: list[Card], declared_rank: str):
        """
        یک حرکت بازی را اجرا می‌کند: بازیکن کارت‌ها را به پشت بازی می‌کند.
        """
        if player != self.players[self.current_player_index]:
            raise ValueError("نوبت این بازیکن نیست.")
        if not cards_to_play:
            raise ValueError("حداقل یک کارت باید بازی شود.")

        if self.current_declared_rank is None:
            self.current_declared_rank = declared_rank

        for card in cards_to_play:
            if card in player.hand:
                player.hand.remove(card)
        
        self.center_pile.extend(cards_to_play)
        self.last_play = {'player': player, 'cards': cards_to_play}
        
        if not player.hand:
            self.is_game_over = True
            self.winner = player
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def call_bluff(self, challenger: Player) -> Player:
        """
        حرکت بازیکن قبلی را به چالش می‌کشد و بازنده چالش را برمی‌گرداند.
        """
        if not self.last_play:
            return None

        last_player = self.last_play['player']
        played_cards = self.last_play['cards']
        
        was_bluffing = any(card.rank != self.current_declared_rank for card in played_cards)

        loser = None
        if was_bluffing:
            loser = last_player
        else:
            loser = challenger

        loser.hand.extend(self.center_pile)
        
        self.center_pile = []
        self.current_declared_rank = None
        self.last_play = None
        self.current_player_index = self.players.index(loser)
        
        return loser
        
    def ai_choose_move(self, player: Player) -> dict:
        """مغز AI برای انتخاب حرکت در بازی بلوف."""
        # Call Bluff Logic
        if self.last_play:
            # Hard AI would track cards. Medium AI checks own hand.
            known_cards_of_rank = [c for c in player.hand if c.rank == self.current_declared_rank]
            # A simple probability check
            if len(known_cards_of_rank) >= 2 and self.difficulty != 'easy':
                 # If I have 2 or more of the declared rank, the chance of the opponent
                 # also having 2 or more is lower, so I'm more likely to call a bluff.
                 if random.random() < 0.6: # 60% chance to call bluff
                    return {'action': 'call_bluff'}
            elif random.random() < 0.2: # Low base chance to call bluff
                return {'action': 'call_bluff'}

        # Play Cards Logic
        declared_rank = self.current_declared_rank
        cards_of_rank_in_hand = []

        if declared_rank:
             cards_of_rank_in_hand = [c for c in player.hand if c.rank == declared_rank]

        if self.difficulty == 'easy':
            # Plays 1 random card and declares its rank if starting, or bluffs.
            card_to_play = random.choice(player.hand)
            return {
                'action': 'play',
                'cards': [card_to_play],
                'declared_rank': declared_rank or card_to_play.rank
            }
        else: # Medium / Hard
            if cards_of_rank_in_hand:
                # Play truthfully
                return {
                    'action': 'play',
                    'cards': cards_of_rank_in_hand,
                    'declared_rank': declared_rank
                }
            else:
                # Bluff: play 1 or 2 random cards
                card_to_play = random.choice(player.hand)
                return {
                    'action': 'play',
                    'cards': [card_to_play],
                    'declared_rank': declared_rank or card_to_play.rank # Must declare if starting
                }
