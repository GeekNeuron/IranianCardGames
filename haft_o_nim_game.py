from game_basics import Card, Player, Deck

class HaftONimGame:
    """
    موتور و منطق اصلی بازی هفت و نیم.
    """
    CARD_VALUES = {
        'A': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 0.5, 'Q': 0.5, 'K': 0.5
    }

    def __init__(self, num_players=3, difficulty='medium'):
        self.difficulty = difficulty
        self.players = [Player(f"بازیکن {i+1}") for i in range(num_players - 1)]
        self.dealer = Player("بانکدار")
        
        self.deck = Deck()
        self.deck.shuffle()
        
        self.is_game_over = False
        self.current_player_index = 0
        self.player_status = {p.name: 'playing' for p in self.players} # 'playing', 'stand', 'bust'
        self.final_results = {}
        
        self._initial_deal()

    def _calculate_hand_value(self, hand: list[Card]) -> float:
        """امتیاز یک دست را محاسبه می‌کند."""
        return sum(self.CARD_VALUES[card.rank] for card in hand)

    def _initial_deal(self):
        """به هر بازیکن و بانکدار یک کارت اولیه می‌دهد."""
        for player in self.players:
            player.add_card(self.deck.deal())
        
        self.dealer.add_card(self.deck.deal())

    def player_hits(self, player: Player) -> float:
        """به بازیکن یک کارت جدید می‌دهد و وضعیت او را بررسی می‌کند."""
        if self.player_status.get(player.name) != 'playing':
            return self._calculate_hand_value(player.hand)

        new_card = self.deck.deal()
        player.add_card(new_card)
        score = self._calculate_hand_value(player.hand)

        if score > 7.5:
            self.player_status[player.name] = 'bust'
        
        return score

    def player_stands(self, player: Player):
        """وضعیت بازیکن را به 'ماندن' تغییر می‌دهد."""
        self.player_status[player.name] = 'stand'

    def dealer_plays(self) -> float:
        """منطق کامل بازی بانکدار را اجرا می‌کند."""
        dealer_score = self._calculate_hand_value(self.dealer.hand)
        
        # قانون ساده: بانکدار تا زمانی که امتیازش کمتر از ۶ باشد، کارت می‌کشد
        while dealer_score < 6:
            if not self.deck: break
            new_card = self.deck.deal()
            self.dealer.add_card(new_card)
            dealer_score = self._calculate_hand_value(self.dealer.hand)
        
        return dealer_score

    def determine_winners(self):
        """نتایج را در پایان دور مشخص می‌کند."""
        dealer_score = self._calculate_hand_value(self.dealer.hand)
        is_dealer_bust = dealer_score > 7.5

        for player in self.players:
            player_score = self._calculate_hand_value(player.hand)
            status = self.player_status[player.name]
            
            result = ""
            if status == 'bust':
                result = f"باخت (سوخت با امتیاز {player_score})"
            elif is_dealer_bust:
                result = f"برد! (بانکدار سوخت)"
            elif player_score > dealer_score:
                result = f"برد! ({player_score} > {dealer_score})"
            elif player_score < dealer_score:
                result = f"باخت. ({player_score} < {dealer_score})"
            else:
                result = f"مساوی. (امتیاز {player_score})"

            self.final_results[player.name] = result
        
        self.is_game_over = True
