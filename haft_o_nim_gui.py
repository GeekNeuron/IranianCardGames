from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from haft_o_nim_game import HaftONimGame
from audio_manager import AudioManager

class HaftONimGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی هفت و نیم، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید هفت و نیم")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)

        self.dealer_hand_layout = QHBoxLayout()
        self.dealer_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.dealer_hand_layout)
        
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)
        
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.controls_layout)

    def start_new_game(self):
        self.game = HaftONimGame(num_players=2) # 1 player vs dealer
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.update_displays()
        self.set_player_controls_enabled(True)

    def on_hit_clicked(self):
        self.audio_manager.play("play")
        player = self.game.players[0]
        score = self.game.player_hits(player)
        
        if self.game.player_status[player.name] == 'bust':
            self.status_label.setText(f"سوختی! با امتیاز {score}. شما باختید.")
            self.set_player_controls_enabled(False)
            self.start_button.show()
        
        self.update_displays()

    def on_stand_clicked(self):
        player = self.game.players[0]
        self.game.player_stands(player)
        self.set_player_controls_enabled(False)
        self.status_label.setText("شما ماندید. نوبت بانکدار...")
        
        QTimer.singleShot(1000, self.play_dealer_turn)

    def play_dealer_turn(self):
        self.game.dealer_plays()
        self.audio_manager.play("play")
        self.game.determine_winners()
        
        player_result = self.game.final_results[self.game.players[0].name]
        self.status_label.setText(f"بازی تمام شد! نتیجه شما: {player_result}")
        self.start_button.show()
        self.update_displays(show_all_dealer_cards=True)

    def update_displays(self, show_all_dealer_cards=False):
        player = self.game.players[0]
        player_score = self.game._calculate_hand_value(player.hand)
        
        if self.game.player_status[player.name] == 'playing':
             self.status_label.setText(f"نوبت شما. امتیاز: {player_score}")

        self.clear_layout(self.dealer_hand_layout)
        self.dealer_hand_layout.addWidget(QLabel("دست بانکدار:"))
        for i, card in enumerate(self.game.dealer.hand):
            lbl = QLabel()
            if i == 0 or show_all_dealer_cards:
                pixmap = QIcon(f"resources/images/themes/default/cards/{card.image_filename}").pixmap(QSize(80, 110))
            else:
                pixmap = QIcon("resources/images/themes/default/back.png").pixmap(QSize(80, 110))
            lbl.setPixmap(pixmap)
            self.dealer_hand_layout.addWidget(lbl)

        self.clear_layout(self.player_hand_layout)
        self.player_hand_layout.addWidget(QLabel("دست شما:"))
        for card in player.hand:
            lbl = QLabel()
            pixmap = QIcon(f"resources/images/themes/default/cards/{card.image_filename}").pixmap(QSize(80, 110))
            lbl.setPixmap(pixmap)
            self.player_hand_layout.addWidget(lbl)

        self.clear_layout(self.controls_layout)
        self.hit_button = QPushButton("بزن (Hit)")
        self.stand_button = QPushButton("بمان (Stand)")
        self.hit_button.clicked.connect(self.on_hit_clicked)
        self.stand_button.clicked.connect(self.on_stand_clicked)
        self.controls_layout.addWidget(self.hit_button)
        self.controls_layout.addWidget(self.stand_button)
        
        is_player_turn_over = self.game.player_status[player.name] != 'playing'
        self.set_player_controls_enabled(not is_player_turn_over)

    def set_player_controls_enabled(self, enabled: bool):
        self.hit_button.setEnabled(enabled)
        self.stand_button.setEnabled(enabled)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
