import random
from itertools import combinations
from collections import Counter
from game_basics import Card, Player, Deck

# ارزش عددی کارت‌ها برای محاسبه جمع
CARD_VALUES = {
    'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 11, 'Q': 12, 'K': 13
}

class ChaharBargGame:
    """موتور و منطق اصلی بازی چهاربرگ (یازده)."""
    def __init__(self, num_players=2, difficulty='medium'):
        if num_players not in [2, 4]:
            raise ValueError("تعداد بازیکنان باید ۲ یا ۴ باشد.")
        
        self.difficulty = difficulty
        self.num_players = num_players
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players)]
        
        self.deck = Deck()
        self.deck.shuffle()
        
        self.table_cards = []
        self.current_player_index = 0
        self.last_capturer = None

        self.total_scores = {p.name: 0 for p in self.players}
        for player in self.players:
            player.soor_count = 0
            player.collected_cards = []
        
        self._initial_deal()

    def _initial_deal(self):
        """۴ کارت روی زمین و ۴ کارت به هر بازیکن می‌دهد."""
        for _ in range(4):
            self.table_cards.append(self.deck.deal())
        
        # قانون خاص: اگر سرباز روی زمین بود، آن را تعویض کن
        for i, card in enumerate(self.table_cards):
            if card.rank == 'J':
                self.deck.cards.insert(0, self.table_cards.pop(i))
                self.deck.shuffle()
                self.table_cards.insert(i, self.deck.deal())

        self._deal_cards_to_players()

    def _deal_cards_to_players(self):
        """به هر بازیکن ۴ کارت جدید می‌دهد."""
        for player in self.players:
            player.hand = [] # Clear previous hand
            for _ in range(4):
                if len(self.deck) > 0:
                    player.add_card(self.deck.deal())

    def get_possible_captures(self, player_card: Card) -> list:
        """تمام راه‌های ممکن برای جمع‌آوری کارت از روی زمین با کارت داده شده را پیدا می‌کند."""
        possible_captures = []
        player_card_rank = player_card.rank
        
        if player_card_rank == 'J':
            capture = [card for card in self.table_cards if card.rank != 'Q' and card.rank != 'K']
            if capture:
                possible_captures.append(capture)
            return possible_captures

        if player_card_rank == 'Q':
            capture = [card for card in self.table_cards if card.rank == 'Q']
            if capture:
                possible_captures.append([capture[0]])
            return possible_captures
            
        if player_card_rank == 'K':
            capture = [card for card in self.table_cards if card.rank == 'K']
            if capture:
                possible_captures.append([capture[0]])
            return possible_captures

        target_sum = 11
        numeric_table_cards = [c for c in self.table_cards if c.rank in CARD_VALUES and c.rank not in ['J', 'Q', 'K']]

        for i in range(1, len(numeric_table_cards) + 1):
            for combo in combinations(numeric_table_cards, i):
                current_sum = sum(CARD_VALUES[card.rank] for card in combo)
                if current_sum + CARD_VALUES[player_card.rank] == target_sum:
                    possible_captures.append(list(combo))
                    
        return possible_captures

    def play_turn(self, player: Player, player_card: Card, chosen_capture: list):
        """حرکت بازیکن را نهایی می‌کند."""
        if player_card not in player.hand: return
        player.hand.remove(player_card)

        if not chosen_capture:
            self.table_cards.append(player_card)
        else:
            all_captured_cards = chosen_capture + [player_card]
            player.collected_cards.extend(all_captured_cards)
            
            for card in chosen_capture:
                self.table_cards.remove(card)
            
            self.last_capturer = player

            # بررسی وضعیت "سور"
            if not self.table_cards:
                if player_card.rank != 'J':
                    player.soor_count += 1

        self.current_player_index = (self.current_player_index + 1) % self.num_players
        
    def end_round(self):
        if self.last_capturer:
            self.last_capturer.collected_cards.extend(self.table_cards)
            self.table_cards = []
        self._calculate_round_scores()

    def _calculate_round_scores(self):
        """امتیازات را در پایان یک دور محاسبه و به امتیاز کل اضافه می‌کند."""
        round_scores = {p.name: 0 for p in self.players}
        club_counts = {p.name: 0 for p in self.players}

        for player in self.players:
            round_scores[player.name] += player.soor_count * 5
            for card in player.collected_cards:
                if card.suit == '♣️':
                    club_counts[player.name] += 1
                if card.rank == 'A':
                    round_scores[player.name] += 1
                elif card.rank == '10' and card.suit == '♦️':
                    round_scores[player.name] += 3
                elif card.rank == '2' and card.suit == '♣️':
                    round_scores[player.name] += 2
        
        max_clubs = -1
        if club_counts:
             max_clubs = max(club_counts.values())
        
        winners = [name for name, count in club_counts.items() if count == max_clubs]
        if max_clubs > 0 and len(winners) == 1:
            round_scores[winners[0]] += 7
        
        for name, score in round_scores.items():
            self.total_scores[name] += score

    def _score_capture(self, cards_to_capture: list, is_soor: bool) -> int:
        """به یک حرکت بر اساس ارزش کارت‌های جمع شده امتیاز می‌دهد."""
        score = 0
        if is_soor:
            score += 10

        for card in cards_to_capture:
            if card.suit == '♣️':
                score += 2
            if card.rank == 'A':
                score += 3
            if card.rank == '10' and card.suit == '♦️':
                score += 5
            if card.rank == '2' and card.suit == '♣️':
                score += 4
        return score

    def ai_choose_move(self, player: Player) -> dict:
        """مغز AI برای انتخاب بهترین حرکت در چهاربرگ."""
        possible_moves = []
        for card_in_hand in player.hand:
            captures = self.get_possible_captures(card_in_hand)
            if captures:
                for capture_group in captures:
                    is_soor = (len(capture_group) == len(self.table_cards))
                    score = self._score_capture(capture_group + [card_in_hand], is_soor)
                    possible_moves.append({'card': card_in_hand, 'capture': capture_group, 'score': score})
            else:
                score = -CARD_VALUES.get(card_in_hand.rank, 0)
                possible_moves.append({'card': card_in_hand, 'capture': [], 'score': score})

        if not possible_moves: return {'card': None, 'capture': [], 'score': 0}

        if self.difficulty == 'easy':
            return random.choice(possible_moves)

        elif self.difficulty == 'medium' or self.difficulty == 'hard':
            best_move = max(possible_moves, key=lambda move: move['score'])
            return best_move
