from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from chos_e_fil_game import ChosEFilGame
from audio_manager import AudioManager

class ChosEFilGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی چُس فیل، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید چُس فیل")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.players_layout = QVBoxLayout()
        self.main_layout.addLayout(self.players_layout)
        
        self.main_layout.addStretch()

        self.controls_layout = QHBoxLayout()
        self.controls_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.controls_layout)

    def start_new_game(self):
        self.game = ChosEFilGame(num_players=4)
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        
        # Initial pair check and removal
        for p in self.game.players:
            self.game.check_and_remove_pairs(p)
        self.game.active_players = [p for p in self.game.players if p.hand]
            
        self.setup_controls()
        self.process_turn()

    def setup_controls(self):
        self.clear_layout(self.controls_layout)
        self.play_turn_button = QPushButton("نوبت بعدی (کشیدن کارت)")
        self.play_turn_button.clicked.connect(self.play_turn)
        self.controls_layout.addWidget(self.play_turn_button)

    def play_turn(self):
        if self.game.is_game_over: return

        current_player = self.game.active_players[self.game.current_player_index]
        self.audio_manager.play("play")
        self.game.play_turn()
        self.update_displays()

        if self.game.is_game_over:
            self.status_label.setText(f"بازی تمام شد! بازنده: {self.game.loser.name}")
            self.play_turn_button.setEnabled(False)
            self.start_button.show()
            self.audio_manager.play("win")

    def process_turn(self):
        self.update_displays()
        current_player = self.game.active_players[self.game.current_player_index]
        if current_player == self.game.players[0]:
            self.play_turn_button.setEnabled(True)
            self.status_label.setText("نوبت شماست. از نفر بعدی کارت بکشید.")
        else:
            self.play_turn_button.setEnabled(False)
            self.status_label.setText(f"نوبت {current_player.name}...")
            QTimer.singleShot(1500, self.play_turn)


    def update_displays(self):
        self.clear_layout(self.players_layout)
        
        self.status_label.setText(f"{len(self.game.active_players)} بازیکن باقی مانده است.")

        for player in self.game.players:
            status = "✅" if not player.hand and player not in self.game.active_players else f"({len(player.hand)} کارت)"
            if player == self.game.loser:
                status = "❌ بازنده"

            player_lbl = QLabel(f"{player.name}: {status}")
            player_lbl.setStyleSheet("font-size: 14px; color: white;")
            if player == self.game.players[self.game.current_player_index] and not self.game.is_game_over:
                player_lbl.setStyleSheet("font-size: 14px; color: white; font-weight: bold; border: 1px solid yellow;")

            self.players_layout.addWidget(player_lbl)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
