import sys
import random
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSpinBox, QFrame, QGridLayout, QInputDialog
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon
from shelem_game import ShelemGame, SUITS
from game_basics import RANK_VALUES
from audio_manager import AudioManager

class ShelemGameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.game = None
        self.audio_manager = AudioManager()
        self.turn_phase = None  # 'bidding', 'discarding', 'hokm_selection', 'playing'
        self.selected_cards_for_discard = []
        self.hand_card_widgets = {}
        self.trick_card_widgets = {}
        self.setup_initial_ui()

    def setup_initial_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        top_layout = QHBoxLayout()
        self.status_label = QLabel("برای شروع بازی شلم، روی دکمه کلیک کنید.")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white; background-color: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px;")
        self.start_button = QPushButton("شروع بازی جدید شلم")
        self.start_button.clicked.connect(self.start_new_game)
        top_layout.addWidget(self.status_label)
        top_layout.addStretch()
        top_layout.addWidget(self.start_button)
        self.main_layout.addLayout(top_layout)
        
        self.controls_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls_layout)

        self.game_board_layout = QGridLayout()
        self.main_layout.addLayout(self.game_board_layout)
        self.main_layout.addStretch()

        self.player_hand_layout = QHBoxLayout()
        self.player_hand_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addLayout(self.player_hand_layout)

    def start_new_game(self):
        self.game = ShelemGame()
        self.start_button.hide()
        self.audio_manager.play("shuffle")
        self.game._deal_initial_cards()
        self.setup_bidding_ui()
        self.turn_phase = 'bidding'
        self.process_bidding_turn()

    def setup_bidding_ui(self):
        self.clear_layout(self.controls_layout)
        self.bid_label = QLabel(f"بالاترین پیشنهاد: {self.game.highest_bid}")
        self.bid_spinbox = QSpinBox()
        self.bid_spinbox.setRange(100, 165)
        self.bid_spinbox.setSingleStep(5)
        self.bid_button = QPushButton("بخوان (Bid)")
        self.pass_button = QPushButton("پاس (Pass)")
        self.bid_button.clicked.connect(self.player_bids)
        self.pass_button.clicked.connect(self.player_passes)
        self.controls_layout.addWidget(self.bid_label)
        self.controls_layout.addWidget(self.bid_spinbox)
        self.controls_layout.addWidget(self.bid_button)
        self.controls_layout.addWidget(self.pass_button)
        self.update_player_hand_display()

    def process_bidding_turn(self):
        if len(self.game.players_in_bid) <= 1 and self.game.bid_winner is not None:
            self.end_bidding_phase()
            return

        current_bidder = self.game.players[self.game.bidding_turn_index]
        if current_bidder not in self.game.players_in_bid:
            self.game.bidding_turn_index = (self.game.bidding_turn_index + 1) % 4
            self.process_bidding_turn()
            return
            
        self.status_label.setText(f"نوبت خواندن: {current_bidder.name}")
        if self.game.bidding_turn_index == 0:
            self.bid_spinbox.setMinimum(self.game.highest_bid + 5)
            self.bid_spinbox.setValue(self.game.highest_bid + 5)
            self.set_bidding_controls_enabled(True)
        else:
            self.set_bidding_controls_enabled(False)
            QTimer.singleShot(1500, self.play_ai_bid_turn)

    def play_ai_bid_turn(self):
        player = self.game.players[self.game.bidding_turn_index]
        hand_value = self.game._estimate_hand_value(player)
        if hand_value >= self.game.highest_bid + 5:
            self.game.highest_bid += 5
            self.game.bid_winner = player
            self.game.bids[player] = self.game.highest_bid
            self.bid_label.setText(f"بالاترین پیشنهاد: {self.game.highest_bid} ({player.name})")
        else:
            self.game.players_in_bid.remove(player)
        self.game.bidding_turn_index = (self.game.bidding_turn_index + 1) % 4
        self.process_bidding_turn()
        
    def player_bids(self):
        bid_value = self.bid_spinbox.value()
        self.game.highest_bid = bid_value
        self.game.bid_winner = self.game.players[0]
        self.game.bids[self.game.players[0]] = bid_value
        self.bid_label.setText(f"بالاترین پیشنهاد: {self.game.highest_bid} (شما)")
        self.game.bidding_turn_index = (self.game.bidding_turn_index + 1) % 4
        self.process_bidding_turn()
        
    def player_passes(self):
        self.game.players_in_bid.remove(self.game.players[0])
        self.game.bidding_turn_index = (self.game.bidding_turn_index + 1) % 4
        self.process_bidding_turn()

    def end_bidding_phase(self):
        self.clear_layout(self.controls_layout)
        self.game.hakem = self.game.bid_winner
        result_text = f"مزایده تمام شد. حاکم: {self.game.hakem.name} با خواندن {self.game.highest_bid}"
        self.status_label.setText(result_text)
        self.start_hakem_turn()

    def start_hakem_turn(self):
        for card in self.game.kitty:
            self.game.hakem.add_card(card)

        if self.game.hakem == self.game.players[0]:
            self.turn_phase = 'discarding'
            self.status_label.setText("زمین را برداشتید. لطفا ۴ کارت برای رد کردن انتخاب کنید.")
            self.setup_discard_ui()
        else:
            self.status_label.setText(f"{self.game.hakem.name} در حال مدیریت کارت‌ها و انتخاب حکم است...")
            QTimer.singleShot(2000, self.play_ai_hakem_turn)

    def setup_discard_ui(self):
        self.update_player_hand_display()
        self.discard_button = QPushButton("رد کردن ۴ کارت انتخاب شده")
        self.discard_button.setEnabled(False)
        self.discard_button.clicked.connect(self.on_discard_clicked)
        self.controls_layout.addWidget(self.discard_button)

    def on_card_toggled_for_discard(self, card, is_checked):
        if is_checked:
            self.selected_cards_for_discard.append(card)
        else:
            self.selected_cards_for_discard.remove(card)
        self.discard_button.setEnabled(len(self.selected_cards_for_discard) == 4)

    def on_discard_clicked(self):
        for card in self.selected_cards_for_discard:
            self.game.hakem.hand.remove(card)
        self.selected_cards_for_discard = []
        self.clear_layout(self.controls_layout)
        self.turn_phase = 'hokm_selection'
        self.prompt_for_hokm_ui()

    def prompt_for_hokm_ui(self):
        self.status_label.setText("حکم را انتخاب کنید:")
        self.hokm_buttons_layout = QHBoxLayout()
        for suit in SUITS:
            btn = QPushButton(suit)
            btn.setStyleSheet("font-size: 24px; font-weight: bold;")
            btn.clicked.connect(lambda _, s=suit: self.finalize_game_start(s))
            self.hokm_buttons_layout.addWidget(btn)
        self.main_layout.insertLayout(1, self.hokm_buttons_layout)
        self.update_player_hand_display()

    def play_ai_hakem_turn(self):
        self.game._hakem_manages_kitty()
        self.game.set_hokm()
        self.finalize_game_start(self.game.hokm_suit)

    def finalize_game_start(self, hokm_suit):
        self.game.hokm_suit = hokm_suit
        if hasattr(self, 'hokm_buttons_layout'):
            self.clear_layout(self.hokm_buttons_layout)
            self.main_layout.removeItem(self.hokm_buttons_layout)
        self.turn_phase = 'playing'
        self.game.current_player_index = self.players.index(self.game.hakem)
        self.process_trick_turn()

    def process_trick_turn(self):
        # This is the trick-taking logic, similar to Hokm
        if len(self.game.players[0].hand) == 0:
            # End of round logic
            return
        if not self.game.trick_cards:
            self.clear_trick_widgets()
        self.update_displays()
        # ... and so on
    
    def update_displays(self):
        self.status_label.setText(f"حکم: {self.game.hokm_suit or '?'} | نوبت: {self.game.players[self.game.current_player_index].name}")
        self.update_player_hand_display()
        # self.update_trick_display()

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
            btn.setStyleSheet("QPushButton { border: none; background-color: transparent; } QPushButton:checked { border: 2px solid #007bff; border-radius: 5px; }")
            if self.turn_phase == 'discarding':
                btn.setCheckable(True)
                btn.toggled.connect(lambda checked, c=card: self.on_card_toggled_for_discard(c, checked))
            else:
                btn.setCheckable(False)
                # btn.clicked.connect(...)
            self.player_hand_layout.addWidget(btn)
            self.hand_card_widgets[card] = btn

    def set_bidding_controls_enabled(self, enabled):
        self.bid_spinbox.setEnabled(enabled)
        self.bid_button.setEnabled(enabled)
        self.pass_button.setEnabled(enabled)
        
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
