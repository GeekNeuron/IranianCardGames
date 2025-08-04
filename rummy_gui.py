from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from rummy_game import RummyGame, Card, RANK_VALUES
from audio_manager import AudioManager

class RummyGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.turn_phase = None
        self.selected_cards = []
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی ریم، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید ریم")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)
        
        self.melds_layout = QHBoxLayout()
        self.main_layout.addLayout(self.melds_layout)
        
        self.game_board_layout = QHBoxLayout()
        self.main_layout.addLayout(self.game_board_layout)
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)
        
        self.action_layout = QHBoxLayout()
        self.main_layout.addLayout(self.action_layout)

    def start_new_game(self):
        self.game = RummyGame()
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.process_turn()

    def process_turn(self):
        if self.game.is_game_over:
            self.status_label.setText(f"بازی تمام شد! برنده: {self.game.winner.name}")
            self.start_button.show()
            self.audio_manager.play("win")
            return

        current_player = self.game.players[self.game.current_player_index]
        if self.game.current_player_index == 0:
            self.turn_phase = 'draw'
            self.status_label.setText("نوبت شما: یک کارت بکشید.")
        else:
            self.turn_phase = 'ai_turn'
            self.status_label.setText(f"نوبت حریف: {current_player.name}")
            QTimer.singleShot(2000, self.play_ai_turn)
            
        self.update_displays()

    def on_draw_clicked(self, source: str):
        if self.turn_phase != 'draw': return
        self.audio_manager.play("play")
        self.game.draw_card(self.game.players[0], source)
        self.selected_cards = []
        self.turn_phase = 'meld_discard'
        self.status_label.setText("کارت‌ها را بچینید (Meld) و یا یک کارت را برای دور انداختن انتخاب کنید.")
        self.update_displays()

    def on_hand_card_toggled(self, card: Card, is_checked: bool):
        if is_checked:
            if card not in self.selected_cards: self.selected_cards.append(card)
        else:
            if card in self.selected_cards: self.selected_cards.remove(card)
        self.update_action_buttons()

    def on_meld_clicked(self):
        is_valid = self.game._is_valid_set(self.selected_cards) or self.game._is_valid_run(self.selected_cards)
        if is_valid:
            self.game.play_melds(self.game.players[0], [self.selected_cards])
            self.audio_manager.play("win")
            self.selected_cards = []
            self.update_displays()
        else:
            self.status_label.setText("این یک مجموعه مجاز نیست!")
            QTimer.singleShot(2000, lambda: self.status_label.setText("کارت‌ها را بچینید یا یک کارت دور بیندازید."))

    def on_discard_clicked(self):
        if len(self.selected_cards) != 1: return
        self.audio_manager.play("play")
        self.game.discard_card(self.game.players[0], self.selected_cards[0])
        self.selected_cards = []
        self.process_turn()

    def play_ai_turn(self):
        self.game.ai_play_turn(self.game.players[self.game.current_player_index])
        self.process_turn()

    def update_displays(self):
        self.clear_layout(self.game_board_layout)
        self.clear_layout(self.player_hand_layout)
        self.clear_layout(self.action_layout)
        self.clear_layout(self.melds_layout)

        # Melds on table
        self.melds_layout.addWidget(QLabel("مجموعه‌های روی زمین:"))
        for meld in self.game.melds_on_table:
            meld_text = " ".join(str(c) for c in meld)
            self.melds_layout.addWidget(QLabel(f"[{meld_text}]"))

        # Stock and Discard piles
        stock_pile_btn = QPushButton(f"دسته اصلی\n({len(self.game.stock_pile)} کارت)")
        discard_card = self.game.top_discard_card()
        discard_pile_btn = QPushButton(f"برداشتن\n{discard_card}" if discard_card else "خالی")
        stock_pile_btn.clicked.connect(lambda: self.on_draw_clicked('stock'))
        discard_pile_btn.clicked.connect(lambda: self.on_draw_clicked('discard'))
        self.game_board_layout.addWidget(stock_pile_btn)
        self.game_board_layout.addWidget(discard_pile_btn)
        
        # Player hand
        player = self.game.players[0]
        for card in sorted(player.hand, key=lambda c: (c.suit, RANK_VALUES[c.rank])):
            btn = QPushButton(str(card))
            btn.setCheckable(True)
            btn.toggled.connect(lambda checked, c=card: self.on_hand_card_toggled(c, checked))
            self.player_hand_layout.addWidget(btn)

        # Action buttons
        self.meld_button = QPushButton("چیدن مجموعه (Meld)")
        self.discard_button = QPushButton("دور انداختن کارت")
        self.meld_button.clicked.connect(self.on_meld_clicked)
        self.discard_button.clicked.connect(self.on_discard_clicked)
        self.action_layout.addWidget(self.meld_button)
        self.action_layout.addWidget(self.discard_button)
        
        self.configure_ui_for_phase()

    def configure_ui_for_phase(self):
        is_my_turn = self.game.current_player_index == 0
        
        for i in range(self.game_board_layout.count()):
            widget = self.game_board_layout.itemAt(i).widget()
            if widget: widget.setEnabled(is_my_turn and self.turn_phase == 'draw')
            
        for i in range(self.player_hand_layout.count()):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget: widget.setEnabled(is_my_turn and self.turn_phase == 'meld_discard')
        
        self.meld_button.setVisible(is_my_turn and self.turn_phase == 'meld_discard')
        self.discard_button.setVisible(is_my_turn and self.turn_phase == 'meld_discard')
        self.update_action_buttons()

    def update_action_buttons(self):
        self.discard_button.setEnabled(len(self.selected_cards) == 1)
        is_valid_meld = self.game._is_valid_set(self.selected_cards) or self.game._is_valid_run(self.selected_cards)
        self.meld_button.setEnabled(is_valid_meld)
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
