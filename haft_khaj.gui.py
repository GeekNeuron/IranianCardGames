from collections import Counter
import random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QInputDialog
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from haft_khaj_game import HaftKhajGame, Card, SUITS
from audio_manager import AudioManager

class HaftKhajGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی هفت خاج، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید هفت خاج")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.discard_pile_layout = QHBoxLayout()
        self.discard_pile_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.discard_pile_layout)
        
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)

    def start_new_game(self):
        self.game = HaftKhajGame(num_players=3)
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.process_turn()

    def process_turn(self):
        if self.game.is_game_over:
            winner = next((p for p in self.game.players if not p.hand), None)
            self.status_label.setText(f"بازی تمام شد! برنده: {winner.name if winner else 'نامشخص'}")
            self.start_button.show()
            self.audio_manager.play("win")
            return
            
        self.update_displays()
        
        current_player = self.game.players[self.game.current_player_index]
        if self.game.current_player_index == 0:
            self.set_player_controls_enabled(True)
        else:
            self.set_player_controls_enabled(False)
            QTimer.singleShot(1500, self.play_ai_turn)

    def on_card_clicked(self, card: Card):
        self.audio_manager.play("play")
        if card.rank == '7':
            self.prompt_for_suit(card)
        else:
            self.game.play_turn(self.game.players[0], card)
            self.process_turn()
    
    def on_draw_clicked(self):
        self.audio_manager.play("play")
        self.game.player_must_draw(self.game.players[0])
        self.process_turn()

    def prompt_for_suit(self, card_seven: Card):
        suit, ok = QInputDialog.getItem(self, "انتخاب خال", "خال بعدی را انتخاب کنید:", SUITS, 0, False)
        if ok and suit:
            self.game.play_turn(self.game.players[0], card_seven, suit)
        self.process_turn()

    def play_ai_turn(self):
        player = self.game.players[self.game.current_player_index]
        move = self.game.ai_choose_card(player)
        
        if move:
            self.audio_manager.play("play")
            self.game.play_turn(player, move['card'], move['suit'])
        else:
            self.game.player_must_draw(player)
            
        self.process_turn()

    def update_displays(self):
        player_name = self.game.players[self.game.current_player_index].name
        status_text = f"نوبت: {player_name}"
        if self.game.declared_suit:
            status_text += f" | خال اعلام شده: {self.game.declared_suit}"
        self.status_label.setText(status_text)

        self.clear_layout(self.discard_pile_layout)
        top_card = self.game.top_card()
        if top_card:
            lbl = QLabel()
            pixmap = QIcon(f"resources/images/themes/default/cards/{top_card.image_filename}").pixmap(QSize(100, 140))
            lbl.setPixmap(pixmap)
            self.discard_pile_layout.addWidget(lbl)

        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        self.playable_cards_in_hand = [c for c in player.hand if self.game._is_move_valid(c)]
        
        for card in sorted(player.hand, key=lambda c: (c.suit, c.rank)):
            btn = QPushButton("")
            btn.setIcon(QIcon(f"resources/images/themes/default/cards/{card.image_filename}"))
            btn.setIconSize(QSize(80, 110))
            btn.setFixedSize(QSize(85, 115))
            btn.setStyleSheet("QPushButton { border: none; background-color: transparent; }")
            btn.clicked.connect(lambda _, c=card: self.on_card_clicked(c))
            self.player_hand_layout.addWidget(btn)

        self.draw_button = QPushButton("کارت بکش")
        self.draw_button.clicked.connect(self.on_draw_clicked)
        self.player_hand_layout.addWidget(self.draw_button)
        
    def set_player_controls_enabled(self, enabled: bool):
        is_any_card_playable = bool(self.playable_cards_in_hand)
        self.draw_button.setVisible(enabled and not is_any_card_playable)

        for i in range(self.player_hand_layout.count() - 1):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget:
                # This is tricky because the widget text is empty. We need a better way to map widget to card.
                # For now, we enable all and rely on the logic to prevent illegal moves.
                widget.setEnabled(enabled and is_any_card_playable)
    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
