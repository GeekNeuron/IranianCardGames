import random

SUITS = ["♣️", "♦️", "♥️", "♠️"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
RANK_VALUES = {rank: i for i, rank in enumerate(RANKS, 2)}

class Card:
    """کلاسی برای نمایش یک کارت بازی."""
    def __init__(self, suit: str, rank: str):
        if suit not in SUITS:
            raise ValueError(f"خال نامعتبر: {suit}")
        if rank not in RANKS:
            raise ValueError(f"رتبه نامعتبر: {rank}")
            
        self.suit = suit
        self.rank = rank
        
        # ایجاد نام فایل تصویر بر اساس خال و رتبه
        rank_map = {'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'}
        suit_map = {"♣️": "C", "♦️": "D", "♥️": "H", "♠️": "S"}
        
        rank_char = rank_map.get(rank, rank) 
        suit_char = suit_map[suit]
        
        self.image_filename = f"{rank_char}{suit_char}.png"

    def __repr__(self) -> str:
        return f"{self.rank}{self.suit}"

    def __eq__(self, other):
        # این متد برای مقایسه دو کارت لازم است
        return isinstance(other, Card) and self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        # این متد برای استفاده از کارت‌ها در دیکشنری یا ست لازم است
        return hash((self.rank, self.suit))


class Deck:
    """کلاسی برای نمایش یک دسته کارت استاندارد ۵۲ تایی."""
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]

    def __repr__(self) -> str:
        return f"دسته کارت با {len(self.cards)} کارت"

    def __len__(self) -> int:
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self) -> Card | None:
        """یک کارت از روی دسته برمی‌دارد. اگر کارتی باقی نمانده باشد، None برمی‌گرداند."""
        if len(self.cards) == 0:
            return None
        return self.cards.pop()

class Player:
    """کلاسی برای نمایش یک بازیکن."""
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        # متغیرهای دیگر توسط هر بازی به صورت داینامیک اضافه می‌شوند
        self.collected_cards = []
        self.score = 0

    def __repr__(self) -> str:
        return self.name

    def add_card(self, card: Card):
        """یک کارت به دست بازیکن اضافه می‌کند."""
        if card:
            self.hand.append(card)
