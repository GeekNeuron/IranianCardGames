from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, QTimer
from chahar_barg_game import ChaharBargGame, Card
from audio_manager import AudioManager
from game_basics import Player

class ChaharBargGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.selected_hand_card = None
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی چهاربرگ، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید چهاربرگ")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)
        
        self.scores_layout = QHBoxLayout()
        self.main_layout.addLayout(self.scores_layout)

        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.StyledPanel)
        self.table_cards_layout = QHBoxLayout()
        table_frame.setLayout(self.table_cards_layout)
        self.main_layout.addWidget(table_frame)
        
        self.capture_options_layout = QVBoxLayout()
        self.main_layout.addLayout(self.capture_options_layout)
        
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)

    def start_new_game(self):
        self.game = ChaharBargGame()
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.process_turn()

    def process_turn(self):
        if len(self.game.deck) == 0 and all(len(p.hand) == 0 for p in self.game.players):
            self.end_round()
            return
            
        if all(len(p.hand) == 0 for p in self.game.players):
            self.game._deal_cards_to_players()

        self.update_displays()
        
        current_player = self.game.players[self.game.current_player_index]
        if self.game.current_player_index == 0:
            self.status_label.setText("نوبت شماست: یک کارت از دستتان انتخاب کنید.")
            self.set_hand_buttons_enabled(True)
        else:
            self.status_label.setText(f"نوبت حریف: {current_player.name}")
            self.set_hand_buttons_enabled(False)
            QTimer.singleShot(1500, self.play_ai_turn)

    def on_hand_card_selected(self, card: Card):
        self.selected_hand_card = card
        self.set_hand_buttons_enabled(False)
        
        possible_captures = self.game.get_possible_captures(card)
        self.clear_layout(self.capture_options_layout)
        
        if not possible_captures:
            self.status_label.setText(f"با {card} حرکتی ممکن نیست. کارت روی زمین گذاشته می‌شود.")
            QTimer.singleShot(1000, lambda: self.finalize_turn([]))
        else:
            self.status_label.setText("یک حرکت را انتخاب کنید:")
            for capture_group in possible_captures:
                capture_text = " + ".join(str(c) for c in capture_group)
                btn = QPushButton(f"جمع‌آوری: {capture_text}")
                btn.clicked.connect(lambda _, cg=capture_group: self.finalize_turn(cg))
                self.capture_options_layout.addWidget(btn)

    def finalize_turn(self, chosen_capture: list):
        player = self.game.players[0]
        self.game.play_turn(player, self.selected_hand_card, chosen_capture)
        if chosen_capture: self.audio_manager.play("win")
        else: self.audio_manager.play("play")
        
        self.selected_hand_card = None
        self.clear_layout(self.capture_options_layout)
        self.process_turn()

    def play_ai_turn(self):
        player = self.game.players[self.game.current_player_index]
        move = self.game.ai_choose_move(player)
        
        if move and move['card']:
            self.game.play_turn(player, move['card'], move['capture'])
            if move['capture']: self.audio_manager.play("win")
            else: self.audio_manager.play("play")

        self.process_turn()

    def end_round(self):
        self.game.end_round()
        self.update_displays()
        final_scores_text = " | ".join([f"{name}: {score}" for name, score in self.game.total_scores.items()])
        self.status_label.setText(f"دور تمام شد! امتیازات نهایی: {final_scores_text}")
        self.start_button.show()

    def update_displays(self):
        self.clear_layout(self.table_cards_layout)
        self.table_cards_layout.addWidget(QLabel("کارت‌های زمین:"))
        for card in self.game.table_cards:
            lbl = QLabel(str(card))
            lbl.setStyleSheet("font-size: 18px; font-weight: bold; border: 1px solid black; padding: 10px; background-color: white;")
            self.table_cards_layout.addWidget(lbl)

        self.clear_layout(self.player_hand_layout)
        player = self.game.players[0]
        for card in player.hand:
            btn = QPushButton(str(card))
            btn.setStyleSheet("font-size: 16px; padding: 10px 5px;")
            btn.clicked.connect(lambda _, c=card: self.on_hand_card_selected(c))
            self.player_hand_layout.addWidget(btn)
            
        self.clear_layout(self.scores_layout)
        scores_text = "امتیازات: " + " | ".join([f"{name}: {score}" for name, score in self.game.total_scores.items()])
        self.scores_layout.addWidget(QLabel(scores_text))

    def set_hand_buttons_enabled(self, enabled):
        for i in range(self.player_hand_layout.count()):
            widget = self.player_hand_layout.itemAt(i).widget()
            if widget: widget.setEnabled(enabled)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
