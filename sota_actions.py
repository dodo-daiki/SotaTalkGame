# sota_actions.py
"""
Sota の動き・発話をまとめて扱うモジュール。

現時点では実機 SDK が不明なため、
代わりにコンソールへのテキスト出力で動作をエミュレートする。
"""

from dataclasses import dataclass


@dataclass
class SotaAction:
    """Sota にさせたい 1 セットの動作と発話"""
    motion: str  # 例: "右手を上げる"
    speech: str  # 例: "リンゴを投げるよ"


class SotaController:
    """
    Sota の動作と発話をまとめて実行するクラス。
    将来、実機 SDK が分かったらこの中身だけ差し替えればよい。
    """

    def __init__(self, debug_print: bool = True):
        """
        debug_print:
            True のとき、実際の動きの代わりに print で表示する。
        """
        self.debug_print = debug_print

        # TODO: 実機を使うときは、ここで Sota への接続初期化などを行う
        # 例) self.robot = SotaSDK.connect(...)

    # =========================================================
    # 個別動作
    # =========================================================

    def move(self, motion: str) -> None:
        """
        Sota の体を動かす（今は print で代用）
        """
        if self.debug_print:
            print("---- Sota 動作 ----")
            print(f"[動き] {motion}")
            print("-------------------\n")
        else:
            # TODO: 実機制御（例: self.robot.play_motion(motion_id)）
            pass

    def speak(self, speech: str) -> None:
        """
        Sota に喋らせる（今は print で代用）
        """
        if self.debug_print:
            print("---- Sota 発話 ----")
            print(f"[発話] {speech}")
            print("-------------------\n")
        else:
            # TODO: 実機制御（例: self.robot.speak(speech)）
            pass

    # =========================================================
    # 複合動作（動作＋発話）
    # =========================================================

    def perform_action(self, action: SotaAction) -> None:
        """
        指定された動き＋発話を順に実行する。
        """
        self.move(action.motion)
        self.speak(action.speech)

    def perform(self, motion: str, speech: str) -> None:
        """
        motion, speech を直接指定して実行。
        """
        self.move(motion)
        self.speak(speech)
