import random
from game_basics import Card, Player, Deck, RANKS

class ChosEFilGame:
    """
    موتور و منطق اصلی بازی چُس فیل.
    """
    def __init__(self, num_players=4, difficulty='medium'):
        if num_players < 2:
            raise ValueError("تعداد بازیکنان باید حداقل ۲ نفر باشد.")
        
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        self.game_deck = self._create_game_deck(num_players)
        random.shuffle(self.game_deck)

        self.active_players = list(self.players)
        self.loser = None
        self.is_game_over = False
        self.current_player_index = 0

        self._deal_cards()

    def _create_game_deck(self, num_players: int) -> list[Card]:
        """دسته کارت مخصوص بازی را می‌سازد (N-1 جفت + 1 تک کارت)."""
        deck = []
        chos_fil_card = Card('♠️', 'A') # The odd one out
        deck.append(chos_fil_card)

        available_ranks = [r for r in RANKS if r != 'A']
        random.shuffle(available_ranks)
        
        num_pairs = (num_players * 2 - 1) // 2 if num_players > 4 else num_players - 1
        
        for i in range(num_pairs):
            rank = available_ranks.pop()
            suits = random.sample(['♠️', '♥️', '♦️', '♣️'], 2)
            deck.append(Card(suits[0], rank))
            deck.append(Card(suits[1], rank))
            
        return deck

    def _deal_cards(self):
        """کارت‌ها را بین بازیکنان پخش می‌کند."""
        # This game variant deals all cards out.
        player_index = 0
        while self.game_deck:
            player = self.players[player_index]
            player.add_card(self.game_deck.pop())
            player_index = (player_index + 1) % len(self.players)

    def check_and_remove_pairs(self, player: Player):
        """
        جفت‌های موجود در دست بازیکن را پیدا کرده، حذف می‌کند و وضعیت بازیکن را بررسی می‌کند.
        """
        while True:
            ranks_in_hand = [card.rank for card in player.hand]
            rank_counts = {rank: ranks_in_hand.count(rank) for rank in set(ranks_in_hand)}
            
            found_pair = False
            for rank, count in rank_counts.items():
                if count >= 2:
                    # Remove one pair of this rank
                    cards_of_rank = [c for c in player.hand if c.rank == rank]
                    player.hand.remove(cards_of_rank[0])
                    player.hand.remove(cards_of_rank[1])
                    found_pair = True
                    break # Restart check after modifying the list
            
            if not found_pair:
                break

    def play_turn(self):
        """
        یک نوبت کامل بازی را اجرا می‌کند.
        """
        if len(self.active_players) <= 1:
            if self.active_players:
                self.loser = self.active_players[0]
            self.is_game_over = True
            return

        current_player = self.active_players[self.current_player_index]
        
        next_player_index_in_active = (self.current_player_index + 1) % len(self.active_players)
        next_player = self.active_players[next_player_index_in_active]

        if not next_player.hand:
            # This player is out, find the next one with cards
            original_next_idx = next_player_index_in_active
            while not next_player.hand:
                next_player_index_in_active = (next_player_index_in_active + 1) % len(self.active_players)
                next_player = self.active_players[next_player_index_in_active]
                if next_player_index_in_active == original_next_idx: return # All others are out

        drawn_card = random.choice(next_player.hand)
        next_player.hand.remove(drawn_card)
        current_player.add_card(drawn_card)

        self.check_and_remove_pairs(current_player)

        # Update active players list
        self.active_players = [p for p in self.active_players if p.hand]

        # Advance turn
        try:
            current_player_new_index = self.active_players.index(current_player)
            self.current_player_index = (current_player_new_index + 1) % len(self.active_players)
        except ValueError:
            # Current player was removed, index might stay the same or need adjustment
            self.current_player_index %= len(self.active_players) if self.active_players else 0
