from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from bluff_game import BluffGame, Card, RANKS
from audio_manager import AudioManager
import random

class BluffGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.selected_cards = []
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی بلوف، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید بلوف")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.game_board_layout = QHBoxLayout()
        self.game_board_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.game_board_layout)
        
        self.controls_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls_layout)
        
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)

    def start_new_game(self):
        self.game = BluffGame(num_players=3)
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.setup_controls()
        self.process_turn()

    def setup_controls(self):
        self.clear_layout(self.controls_layout)
        self.rank_selector = QComboBox()
        self.rank_selector.addItems(RANKS)
        self.play_button = QPushButton("بازی کن")
        self.call_bluff_button = QPushButton("بلوف!")
        self.play_button.clicked.connect(self.on_play_clicked)
        self.call_bluff_button.clicked.connect(self.on_bluff_called)
        self.controls_layout.addWidget(QLabel("اعلام رتبه:"))
        self.controls_layout.addWidget(self.rank_selector)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.call_bluff_button)

    def process_turn(self):
        if self.game.is_game_over:
            self.status_label.setText(f"بازی تمام شد! برنده: {self.game.winner.name}")
            self.start_button.show()
            self.set_player_controls_enabled(False)
            self.audio_manager.play("win")
            return

        self.update_displays()
        current_player = self.game.players[self.game.current_player_index]
        if self.game.current_player_index == 0:
            self.status_label.setText("نوبت شماست.")
            self.set_player_controls_enabled(True)
        else:
            self.status_label.setText(f"نوبت حریف: {current_player.name}")
            self.set_player_controls_enabled(False)
            QTimer.singleShot(2000, self.play_ai_turn)

    def on_card_toggled(self, card: Card, is_checked: bool):
        if is_checked:
            if card not in self.selected_cards: self.selected_cards.append(card)
        else:
            if card in self.selected_cards: self.selected_cards.remove(card)
        self.play_button.setEnabled(len(self.selected_cards) > 0)

    def on_play_clicked(self):
        declared_rank = self.rank_selector.currentText()
        self.game.play_cards(self.game.players[0], self.selected_cards, declared_rank)
        self.selected_cards = []
        self.audio_manager.play("play")
        self.process_turn()

    def on_bluff_called(self):
        loser = self.game.call_bluff(self.game.players[0])
        self.status_label.setText(f"چالش تمام شد! {loser.name} کارت‌ها را برداشت.")
        self.audio_manager.play("win")
        QTimer.singleShot(2000, self.process_turn)

    def play_ai_turn(self):
        player = self.game.players[self.game.current_player_index]
        move = self.game.ai_choose_move(player)
        
        if move['action'] == 'call_bluff':
            loser = self.game.call_bluff(player)
            self.status_label.setText(f"{player.name} بلوف را صدا زد! {loser.name} کارت‌ها را برداشت.")
            self.audio_manager.play("win")
        elif move['action'] == 'play':
            self.game.play_cards(player, move['cards'], move['declared_rank'])
            self.audio_manager.play("play")

        QTimer.singleShot(2000, self.process_turn)

    def update_displays(self):
        if self.game.current_declared_rank:
            status_text = f"رتبه اعلام شده: {self.game.current_declared_rank}"
        else:
            status_text = "منتظر اعلام رتبه توسط بازیکن اول..."
        self.status_label.setText(status_text)
        
        self.clear_layout(self.game_board_layout)
        center_pile_lbl = QLabel(f"تعداد کارت در وسط: {len(self.game.center_pile)}")
        center_pile_lbl.setStyleSheet("font-size: 18px; color: white;")
        self.game_board_layout.addWidget(center_pile_lbl)
        
        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, c.rank)):
            btn = QPushButton(str(card)) # Show card text for selection
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, c=card: self.on_card_toggled(c, checked))
            self.player_hand_layout.addWidget(btn)

    def set_player_controls_enabled(self, enabled: bool):
        self.play_button.setEnabled(enabled and len(self.selected_cards) > 0)
        self.call_bluff_button.setEnabled(enabled and self.game.last_play is not None)
        
        is_rank_declaration_turn = self.game.current_declared_rank is None
        self.rank_selector.setEnabled(enabled and is_rank_declaration_turn)
        
        for i in range(self.player_hand_layout.count()):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget: widget.setEnabled(enabled)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
