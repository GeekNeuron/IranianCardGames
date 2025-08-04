from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from ganjifeh_game import GanjifehGame, GanjifehCard, Player
from audio_manager import AudioManager

class GanjifehGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.hand_card_widgets = {}
        self.trick_card_widgets = {}
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی گنجفه، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید گنجفه")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.game_board_layout = QGridLayout()
        self.main_layout.addLayout(self.game_board_layout)
        self.main_layout.addStretch()
        
        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)

    def start_new_game(self):
        self.game = GanjifehGame()
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.process_trick_turn()

    def process_trick_turn(self):
        if len(self.game.players[0].hand) == 0:
            winner_team = max(self.game.team_trick_wins, key=self.game.team_trick_wins.get)
            self.status_label.setText(f"دور تمام شد! برنده: {winner_team}")
            self.start_button.show()
            self.audio_manager.play("win")
            return
            
        if not self.game.trick_cards:
            self.clear_trick_widgets()

        self.update_displays()
        
        current_player = self.game.players[self.game.current_player_index]
        if current_player == self.game.players[0]:
            self.set_hand_buttons_enabled(True)
        else:
            self.set_hand_buttons_enabled(False)
            QTimer.singleShot(1000, self.play_ai_turn)

    def play_ai_turn(self):
        player = self.game.players[self.game.current_player_index]
        card_to_play = self.game.ai_choose_card(player)
        self.on_card_clicked(card_to_play, is_human=False)

    def on_card_clicked(self, card: GanjifehCard, is_human=True):
        player = self.game.players[self.game.current_player_index]
        if is_human and player != self.game.players[0]:
            return
        
        self.audio_manager.play("play")
        self.game.trick_cards.append((player, card))
        player.hand.remove(card)

        if len(self.game.trick_cards) == len(self.game.players):
            self.update_displays()
            winner = self.game._determine_trick_winner()
            winner_team_name = "تیم ۱" if winner in self.game.teams["تیم ۱"] else "تیم ۲"
            self.game.team_trick_wins[winner_team_name] += 1
            
            self.status_label.setText(f"برنده دست: {winner.name}")
            self.game.current_player_index = self.game.players.index(winner)
            self.game.trick_cards = [] # Clear for next trick
            self.audio_manager.play("win")
            QTimer.singleShot(2500, self.process_trick_turn)
        else:
            self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
            self.process_trick_turn()
            
    def update_displays(self):
        scores_text = "دست‌های برده: " + " | ".join([f"{name}: {score}" for name, score in self.game.team_trick_wins.items()])
        self.status_label.setText(f"حکم: {self.game.hokm_suit} | نوبت: {self.game.players[self.game.current_player_index].name} | {scores_text}")
        self.update_player_hand_display()
        self.update_trick_display()

    def update_player_hand_display(self):
        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, self.game.RANK_VALUES[c.rank])):
            btn = QPushButton(str(card))
            btn.setFixedSize(100, 50)
            btn.clicked.connect(lambda _, c=card: self.on_card_clicked(c))
            self.player_hand_layout.addWidget(btn)
            
    def update_trick_display(self):
        positions = {0: (2, 1), 1: (1, 2), 2: (0, 1), 3: (1, 0)}
        for player, card in self.game.trick_cards:
            if card not in self.trick_card_widgets:
                player_idx = self.game.players.index(player)
                lbl = QLabel(str(card))
                lbl.setStyleSheet("font-size: 14px; font-weight: bold; border: 1px solid black; padding: 10px; background-color: white;")
                row, col = positions[player_idx]
                self.game_board_layout.addWidget(lbl, row, col, Qt.AlignCenter)
                self.trick_card_widgets[card] = lbl

    def set_hand_buttons_enabled(self, enabled):
        player = self.game.players[0]
        valid_moves = self.game._get_valid_moves(player)
        for i in range(self.player_hand_layout.count()):
            widget = self.player_hand_layout.itemAt(i).widget()
            # A simple text-based check for validity
            is_valid = any(widget.text() == str(card) for card in valid_moves)
            widget.setEnabled(enabled and is_valid)
    
    def clear_layout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                
    def clear_trick_widgets(self):
        self.clear_layout(self.game_board_layout)
        self.trick_card_widgets.clear()
