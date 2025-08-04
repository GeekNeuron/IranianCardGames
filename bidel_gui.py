import sys, random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from bidel_game import BidelGame, Card, RANK_VALUES
from audio_manager import AudioManager

class BidelGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.game_phase = None
        self.selected_cards_for_pass = []
        self.hand_card_widgets = {}
        self.trick_card_widgets = {}
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی بیدل، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید بیدل")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.scores_layout = QHBoxLayout()
        self.main_layout.addLayout(self.scores_layout)
        
        self.game_board_layout = QGridLayout()
        self.main_layout.addLayout(self.game_board_layout)
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)
        
        self.pass_button = QPushButton("پاس بده")
        self.pass_button.hide()
        self.main_layout.addWidget(self.pass_button, 0, Qt.AlignCenter)

    def start_new_game(self):
        self.game = BidelGame()
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.game.start_new_round()
        self.game_phase = 'passing'
        self.setup_passing_ui()

    def setup_passing_ui(self):
        self.status_label.setText("۳ کارت برای پاس دادن انتخاب کنید.")
        self.update_player_hand_display()
        self.pass_button.show()
        self.pass_button.setEnabled(False)
        self.pass_button.clicked.connect(self.finalize_passing)

    def on_card_toggled_for_pass(self, card: Card, is_checked: bool):
        if is_checked:
            if card not in self.selected_cards_for_pass: self.selected_cards_for_pass.append(card)
        else:
            if card in self.selected_cards_for_pass: self.selected_cards_for_pass.remove(card)
        self.pass_button.setEnabled(len(self.selected_cards_for_pass) == 3)

    def finalize_passing(self):
        pass_data = {}
        pass_data[self.game.players[0].name] = self.selected_cards_for_pass
        for i in range(1, 4):
            player = self.game.players[i]
            pass_data[player.name] = self.game.ai_choose_cards_to_pass(player)
            
        self.game.pass_cards(pass_data)
        
        self.pass_button.hide()
        self.selected_cards_for_pass = []
        self.game_phase = 'playing'
        self.game.current_player_index = self.game._find_starter()
        self.process_trick_turn()

    def process_trick_turn(self):
        trick_count = len(self.game.players[0].collected_cards) + len(self.game.players[1].collected_cards) + len(self.game.players[2].collected_cards) + len(self.game.players[3].collected_cards)
        if trick_count == 52: # 13 tricks * 4 cards
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
        if is_human and player != self.game.players[0]: return

        self.audio_manager.play("play")
        self.game.trick_cards.append((player, card))
        player.hand.remove(card)
        if card.suit == '♥️': self.game.hearts_broken = True

        if len(self.game.trick_cards) == 4:
            self.update_displays()
            # Determine winner and points
            lead_suit = self.game.trick_cards[0][1].suit
            lead_suit_cards = [(p,c) for p,c in self.game.trick_cards if c.suit == lead_suit]
            winner, _ = max(lead_suit_cards, key=lambda item: RANK_VALUES[item[1].rank])
            
            points = self.game._calculate_trick_points(self.game.trick_cards)
            winner.score += points # Using generic score attribute
            winner.collected_cards.extend([c for _,c in self.game.trick_cards])
            
            self.status_label.setText(f"دست را {winner.name} با {points} امتیاز منفی گرفت.")
            self.game.current_player_index = self.players.index(winner)
            self.game.trick_cards = []
            self.audio_manager.play("win")
            QTimer.singleShot(2500, self.process_trick_turn)
        else:
            self.game.current_player_index = (self.game.current_player_index + 1) % 4
            self.process_trick_turn()
            
    def update_displays(self):
        self.status_label.setText(f"نوبت: {self.game.players[self.game.current_player_index].name}")
        self.update_player_hand_display()
        self.update_trick_display()
        self.update_scores_display()

    def update_player_hand_display(self):
        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, RANK_VALUES[c.rank])):
            btn = QPushButton("")
            btn.setIcon(QIcon(f"resources/images/themes/default/cards/{card.image_filename}"))
            btn.setIconSize(QSize(80, 110))
            btn.setFixedSize(QSize(85, 115))
            btn.setStyleSheet("QPushButton { border: none; background-color: transparent; } QPushButton:checked { border: 2px solid #007bff; border-radius: 5px; }")
            
            if self.game_phase == 'passing':
                btn.setCheckable(True)
                btn.toggled.connect(lambda checked, c=card: self.on_card_toggled_for_pass(c, checked))
            else:
                btn.setCheckable(False)
                btn.clicked.connect(lambda _, c=card: self.on_card_clicked(c))
            self.player_hand_layout.addWidget(btn)

    def update_trick_display(self):
        positions = {0: (2, 1), 1: (1, 2), 2: (0, 1), 3: (1, 0)}
        for player, card in self.game.trick_cards:
            if card not in self.trick_card_widgets:
                player_idx = self.players.index(player)
                lbl = QLabel()
                pixmap = QIcon(f"resources/images/themes/default/cards/{card.image_filename}").pixmap(QSize(80, 110))
                lbl.setPixmap(pixmap)
                row, col = positions[player_idx]
                self.game_board_layout.addWidget(lbl, row, col, Qt.AlignCenter)
                self.trick_card_widgets[card] = lbl
                
    def update_scores_display(self):
        self.clear_layout(self.scores_layout)
        scores_text = "امتیازات منفی: " + " | ".join([f"{p.name}: {p.score}" for p in self.game.players])
        self.scores_layout.addWidget(QLabel(scores_text))

    def set_hand_buttons_enabled(self, enabled):
        player = self.game.players[0]
        for i in range(self.player_hand_layout.count()):
            widget = self.player_hand_layout.itemAt(i).widget()
            # A bit tricky to get the card from the widget; this is a simplification
            # A better way is to store a map of widget to card
            widget.setEnabled(enabled)

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
