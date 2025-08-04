import random
from game_basics import Card, Player, Deck, RANK_VALUES

class BidelGame:
    """
    موتور و منطق اصلی بازی بیدل (Hearts).
    """
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(4)]
        
        self.total_scores = {p.name: 0 for p in self.players}
        self.is_game_over = False
        
        self.passing_offset = 1 # 1=left, 2=right, 3=across, 0=hold

    def start_new_round(self):
        """یک دور جدید را با پخش کارت و ریست کردن متغیرها شروع می‌کند."""
        deck = Deck()
        deck.shuffle()
        for p in self.players: p.hand = []
        self._deal_cards(deck)
        
        self.round_scores = {p.name: 0 for p in self.players}
        self.hearts_broken = False
        self.current_player_index = self._find_starter()
        self.trick_cards = []
        
        # چرخش جهت پاس دادن
        self.passing_offset = (self.passing_offset + 1) % 4

    def _deal_cards(self, deck: Deck):
        """کارت‌ها را بین ۴ بازیکن پخش می‌کند."""
        player_idx = 0
        while len(deck) > 0:
            self.players[player_idx].add_card(deck.deal())
            player_idx = (player_idx + 1) % 4

    def _find_starter(self) -> int:
        """بازیکنی که ۲ خاج دارد را برای شروع پیدا می‌کند."""
        for i, player in enumerate(self.players):
            for card in player.hand:
                if card.suit == '♣️' and card.rank == '2':
                    return i
        return 0

    def get_pass_recipient(self, player_index: int) -> int:
        """مقصد پاس دادن کارت را مشخص می‌کند."""
        if self.passing_offset == 1: # Left
            return (player_index + 1) % 4
        if self.passing_offset == 2: # Right
            return (player_index - 1 + 4) % 4
        if self.passing_offset == 3: # Across
            return (player_index + 2) % 4
        return player_index # No pass

    def pass_cards(self, pass_data: dict):
        """کارت‌های پاس داده شده را بین بازیکنان جابجا می‌کند."""
        if self.passing_offset == 0: return

        for i, player in enumerate(self.players):
            recipient_index = self.get_pass_recipient(i)
            recipient = self.players[recipient_index]
            
            cards_to_give = pass_data[player.name]
            for card in cards_to_give:
                if card in player.hand:
                    player.hand.remove(card)
                recipient.hand.append(card)

    def _is_move_valid(self, card: Card, player: Player) -> bool:
        """بررسی می‌کند آیا حرکت بازیکن مجاز است یا خیر."""
        is_first_trick = sum(len(p.collected_cards) for p in self.players) == 0

        # دست اول: باید با ۲ خاج شروع شود
        if is_first_trick and not self.trick_cards:
            return card.suit == '♣️' and card.rank == '2'

        # اگر اولین کارت دست نیست، باید از خال زمینه پیروی کند
        if self.trick_cards:
            lead_suit = self.trick_cards[0][1].suit
            if card.suit != lead_suit and any(c.suit == lead_suit for c in player.hand):
                return False
        
        # اگر اولین کارت دست است، نمی‌تواند با دل شروع کند مگر اینکه دل زده شده باشد
        else: 
            if card.suit == '♥️' and not self.hearts_broken:
                return not any(c.suit != '♥️' for c in player.hand)
        
        return True

    def _calculate_trick_points(self, trick: list) -> int:
        """امتیازات منفی یک دست را محاسبه می‌کند."""
        points = 0
        for _, card in trick:
            if card.suit == '♥️':
                points += 1
            if card.suit == '♠️' and card.rank == 'Q':
                points += 13
        return points

    def ai_choose_cards_to_pass(self, player: Player) -> list[Card]:
        """AI سه کارت را برای پاس دادن انتخاب می‌کند."""
        # Hard: High cards, especially in Spades and Hearts
        player.hand.sort(key=lambda c: RANK_VALUES[c.rank], reverse=True)
        # Avoid passing low clubs/diamonds if possible
        return player.hand[:3]

    def ai_choose_card(self, player: Player) -> Card:
        """مغز AI برای انتخاب کارت در حین بازی."""
        valid_moves = [c for c in player.hand if self._is_move_valid(c, player)]
        
        if not valid_moves: return None

        # Easy: random valid card
        if self.difficulty == 'easy':
            return random.choice(valid_moves)
        
        # Medium/Hard: more strategic
        # Try to discard high cards (Q♠️, A♠️, K♠️) if not following suit
        lead_suit = self.trick_cards[0][1].suit if self.trick_cards else None
        if lead_suit and not any(c.suit == lead_suit for c in player.hand):
            queen_spades = Card('♠️', 'Q')
            if queen_spades in valid_moves: return queen_spades
            high_spades = sorted([c for c in valid_moves if c.suit == '♠️'], key=lambda c: RANK_VALUES[c.rank], reverse=True)
            if high_spades: return high_spades[0]
            high_hearts = sorted([c for c in valid_moves if c.suit == '♥️'], key=lambda c: RANK_VALUES[c.rank], reverse=True)
            if high_hearts: return high_hearts[0]

        # Otherwise, play the lowest possible card
        return min(valid_moves, key=lambda c: RANK_VALUES[c.rank])
