import random
from itertools import combinations
from collections import defaultdict
from game_basics import Card, Player, Deck, RANK_VALUES

class RummyGame:
    """
    موتور و منطق اصلی بازی ریم (Rummy).
    """
    def __init__(self, num_players=2, hand_size=10, difficulty='medium'):
        if num_players < 2:
            raise ValueError("تعداد بازیکنان باید حداقل ۲ نفر باشد.")

        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        self.hand_size = hand_size
        self.is_game_over = False
        self.winner = None
        self.current_player_index = 0

        self.stock_pile = Deck()
        self.stock_pile.shuffle()
        self.discard_pile = []
        
        self.melds_on_table = []

        self._initial_deal()

    def _initial_deal(self):
        """کارت‌های اولیه را پخش کرده و بازی را آماده می‌کند."""
        for player in self.players:
            for _ in range(self.hand_size):
                player.add_card(self.stock_pile.deal())
        
        self.discard_pile.append(self.stock_pile.deal())

    def top_discard_card(self):
        return self.discard_pile[-1] if self.discard_pile else None

    def _is_valid_set(self, cards: list[Card]) -> bool:
        """بررسی می‌کند آیا گروهی از کارت‌ها یک 'ست' مجاز است."""
        if len(cards) not in [3, 4]:
            return False
        
        first_rank = cards[0].rank
        if not all(c.rank == first_rank for c in cards):
            return False
            
        suits = [c.suit for c in cards]
        return len(suits) == len(set(suits))

    def _is_valid_run(self, cards: list[Card]) -> bool:
        """بررسی می‌کند آیا گروهی از کارت‌ها یک 'ران' مجاز است."""
        if len(cards) < 3:
            return False
            
        first_suit = cards[0].suit
        if not all(c.suit == first_suit for c in cards):
            return False
            
        sorted_cards = sorted(cards, key=lambda c: RANK_VALUES[c.rank])
        
        for i in range(len(sorted_cards) - 1):
            current_rank_value = RANK_VALUES[sorted_cards[i].rank]
            next_rank_value = RANK_VALUES[sorted_cards[i+1].rank]
            if next_rank_value != current_rank_value + 1:
                return False
                
        return True

    def find_possible_melds(self, hand: list[Card]) -> list:
        """تمام ملدهای (ست‌ها و ران‌های) ممکن در یک دست را پیدا می‌کند."""
        possible_melds = []
        
        for i in range(3, len(hand) + 1):
            for combo in combinations(hand, i):
                combo_list = list(combo)
                if self._is_valid_set(combo_list) or self._is_valid_run(combo_list):
                    # جلوگیری از افزودن زیرمجموعه‌ها
                    is_subset = False
                    for existing_meld in possible_melds:
                        if set(combo_list).issubset(set(existing_meld)):
                            is_subset = True
                            break
                    if not is_subset:
                        possible_melds.append(combo_list)
                    
        return possible_melds

    def draw_card(self, player: Player, source: str):
        """بازیکن یک کارت از منبع مشخص شده ('stock' یا 'discard') می‌کشد."""
        if source == 'stock':
            if self.stock_pile:
                card = self.stock_pile.deal()
                player.add_card(card)
        elif source == 'discard':
            if self.discard_pile:
                card = self.discard_pile.pop()
                player.add_card(card)
        
        if not self.stock_pile:
             self._refill_stock_pile()

    def play_melds(self, player: Player, melds_to_play: list[list[Card]]):
        """مجموعه‌های انتخاب شده توسط بازیکن را روی زمین می‌گذارد."""
        for meld in melds_to_play:
            if all(card in player.hand for card in meld):
                self.melds_on_table.append(meld)
                for card in meld:
                    player.hand.remove(card)

    def discard_card(self, player: Player, card_to_discard: Card):
        """بازیکن یک کارت را دور می‌اندازد تا نوبتش تمام شود."""
        if card_to_discard not in player.hand:
            # Player might have melded all cards, this is a valid win condition
            if not player.hand:
                 self.is_game_over = True
                 self.winner = player
                 return
            raise ValueError("کارت برای دور انداختن در دست بازیکن نیست.")
            
        player.hand.remove(card_to_discard)
        self.discard_pile.append(card_to_discard)

        if not player.hand:
            self.is_game_over = True
            self.winner = player
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def _refill_stock_pile(self):
        if not self.discard_pile or len(self.discard_pile) <= 1:
            self.is_game_over = True # No cards left to play
            return
        
        top = self.discard_pile.pop()
        cards_to_shuffle = self.discard_pile
        self.discard_pile = [top]
        random.shuffle(cards_to_shuffle)
        self.stock_pile.cards.extend(cards_to_shuffle)

    def ai_play_turn(self, player: Player):
        """یک نوبت کامل را برای بازیکن هوش مصنوعی شبیه‌سازی می‌کند."""
        # 1. Draw card
        # Medium/Hard AI: Check if discard card is useful
        top_discard = self.top_discard_card()
        potential_hand = player.hand + [top_discard]
        melds_with_discard = self.find_possible_melds(potential_hand)
        melds_without_discard = self.find_possible_melds(player.hand)
        
        if self.difficulty != 'easy' and len(melds_with_discard) > len(melds_without_discard):
            self.draw_card(player, 'discard')
        else:
            self.draw_card(player, 'stock')

        # 2. Meld cards
        melds_to_play = self.find_possible_melds(player.hand)
        if melds_to_play:
            self.play_melds(player, melds_to_play)

        # 3. Discard card
        if player.hand:
            # Medium/Hard AI: Discard a card that is not part of any potential meld
            all_meld_cards = set()
            for meld in melds_to_play:
                all_meld_cards.update(meld)
            
            non_meld_cards = [c for c in player.hand if c not in all_meld_cards]
            if non_meld_cards:
                # Discard the highest rank non-meld card
                card_to_discard = max(non_meld_cards, key=lambda c: RANK_VALUES[c.rank])
            else:
                card_to_discard = random.choice(player.hand)
            
            self.discard_card(player, card_to_discard)
