import sys, random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QInputDialog, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, QPropertyAnimation, QRect, QEasingCurve, QTimer, Qt
from hokm_game import HokmGame, Card, SUITS
from audio_manager import AudioManager

class HokmGameWidget(QWidget):
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
        self.status_label = QLabel("برای شروع بازی حکم، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید")
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
        items = ("بازی ۴ نفره", "بازی ۲ نفره")
        player_choice, ok1 = QInputDialog.getItem(self, "انتخاب نوع بازی", "نوع بازی را انتخاب کنید:", items, 0, False)
        if not ok1: return

        items_diff = ("آسان", "متوسط", "سخت")
        difficulty_choice, ok2 = QInputDialog.getItem(self, "انتخاب سطح سختی", "سطح سختی ربات‌ها را انتخاب کنید:", items_diff, 1, False)
        if not ok2: return

        num_players = 4 if "۴" in player_choice else 2
        difficulty = 'easy'
        if "متوسط" in difficulty_choice: difficulty = 'medium'
        if "سخت" in difficulty_choice: difficulty = 'hard'
        
        self.game = HokmGame(num_players=num_players, difficulty=difficulty)
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.prompt_for_hokm()

    def prompt_for_hokm(self):
        self.update_displays()
        hakem = self.game.hakem
        self.status_label.setText(f"حاکم: {hakem.name}. منتظر انتخاب حکم...")

        if hakem == self.game.players[0]:
            self.hokm_buttons_layout = QHBoxLayout()
            for suit in SUITS:
                btn = QPushButton(suit)
                btn.setStyleSheet("font-size: 24px; font-weight: bold;")
                btn.clicked.connect(lambda _, s=suit: self.set_hokm_and_start(s))
                self.hokm_buttons_layout.addWidget(btn)
            self.main_layout.insertLayout(1, self.hokm_buttons_layout)
        else:
            QTimer.singleShot(1000, self.ai_sets_hokm)

    def ai_sets_hokm(self):
        suit_counts = {suit: 0 for suit in SUITS}
        for card in self.game.hakem.hand:
            suit_counts[card.suit] += 1
        chosen_hokm = max(suit_counts, key=suit_counts.get)
        self.set_hokm_and_start(chosen_hokm)

    def set_hokm_and_start(self, suit):
        if hasattr(self, 'hokm_buttons_layout'):
            self.clear_layout(self.hokm_buttons_layout)
            self.main_layout.removeItem(self.hokm_buttons_layout)
            del self.hokm_buttons_layout

        self.game.set_hokm(suit)
        self.process_trick_turn()

    def process_trick_turn(self):
        if len(self.game.players[0].hand) == 0:
            self.status_label.setText("دور تمام شد!")
            self.start_button.show()
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

    def on_card_clicked(self, card, is_human=True):
        player = self.game.players[self.game.current_player_index]
        if is_human and player != self.game.players[0]:
            return
        
        self.audio_manager.play("play")
        self.game.trick_cards.append((player, card))
        player.hand.remove(card)

        if len(self.game.trick_cards) == self.game.num_players:
            self.update_displays()
            winner = self.game._determine_trick_winner()
            winner_team_name = "تیم ۱" if winner in self.game.teams["تیم ۱"] else "تیم ۲"
            self.game.trick_scores[winner_team_name] += 1
            self.status_label.setText(f"برنده دست: {winner.name}")
            self.game.current_player_index = self.players.index(winner)
            self.audio_manager.play("win")
            QTimer.singleShot(2000, self.process_trick_turn)
        else:
            self.game.current_player_index = (self.game.current_player_index + 1) % self.game.num_players
            self.process_trick_turn()
            
    def update_displays(self):
        self.status_label.setText(f"حکم: {self.game.hokm_suit or '?'} | نوبت: {self.game.players[self.game.current_player_index].name}")
        self.update_player_hand_display()
        self.update_trick_display()

    def update_player_hand_display(self):
        self.clear_layout(self.player_hand_layout)
        self.hand_card_widgets.clear()
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, RANK_VALUES[c.rank])):
            btn = QPushButton("")
            icon_path = f"resources/images/themes/default/cards/{card.image_filename}"
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(80, 110))
            btn.setFixedSize(QSize(85, 115))
            btn.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
            btn.clicked.connect(lambda _, c=card: self.on_card_clicked(c))
            self.player_hand_layout.addWidget(btn)
            self.hand_card_widgets[card] = btn
            
    def update_trick_display(self):
        positions = {
            0: (2, 1), # Bottom (Player 1)
            1: (1, 2), # Right (Player 2)
            2: (0, 1), # Top (Player 3)
            3: (1, 0)  # Left (Player 4)
        }
        if self.game.num_players == 2:
            positions = {0: (2, 1), 1: (0, 1)}

        for player, card in self.game.trick_cards:
            if card not in self.trick_card_widgets:
                player_idx = self.players.index(player)
                lbl = QLabel()
                pixmap = QIcon(f"resources/images/themes/default/cards/{card.image_filename}").pixmap(QSize(80, 110))
                lbl.setPixmap(pixmap)
                row, col = positions[player_idx]
                self.game_board_layout.addWidget(lbl, row, col, Qt.AlignCenter)
                self.trick_card_widgets[card] = lbl

    def set_hand_buttons_enabled(self, enabled):
        valid_moves = self.game._get_valid_moves(self.game.players[0])
        for card, widget in self.hand_card_widgets.items():
            widget.setEnabled(enabled and card in valid_moves)

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
