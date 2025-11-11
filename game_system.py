# game_system.py

import json
import random
import unicodedata

from fugashi import Tagger
import jaconv

from sota_actions import SotaController, SotaAction

# 形態素解析器
tagger = Tagger()


def normalize_noun_key(text: str) -> str:
    """
    名詞照合用のキーに正規化する関数。
    - Unicode NFKC 正規化
    - カタカナ → ひらがな
    """
    text = unicodedata.normalize("NFKC", text)
    text = jaconv.kata2hira(text)
    return text


def display_noun_for_speech(display: str) -> str:
    """
    発話用に名詞を整形する関数。
    ここでは「ひらがな → カタカナ」に変換して、
    「りんご」 → 「リンゴ」のようにする。
    """
    return jaconv.hira2kata(display)


class CommandInterpreter:
    """
    ユーザーの日本語コマンドを解析し、
    (名詞, 動詞) の組み合わせから「動き＋発話テキスト」を決めるクラス。

    - 名詞・動詞・動作は JSON から読み込む。
    - (名詞ID × 動詞ID) → action_id の対応は起動時にランダム生成する。
    """

    def __init__(self, nouns_path: str, verbs_path: str, actions_path: str, seed: int | None = None):
        if seed is not None:
            random.seed(seed)

        self._load_nouns(nouns_path)
        self._load_verbs(verbs_path)
        self._load_actions(actions_path)
        self._generate_random_mappings()

    # ===== JSON読み込み =====

    def _load_nouns(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            nouns = json.load(f)

        # 正規化名詞キー → noun_id
        self.noun_id_by_key: dict[str, str] = {}
        # noun_id → 表示用文字列
        self.noun_display_by_id: dict[str, str] = {}

        for noun in nouns:
            nid = noun["id"]
            self.noun_display_by_id[nid] = noun["display"]
            for alias in noun.get("aliases", []):
                key = normalize_noun_key(alias)
                self.noun_id_by_key[key] = nid

        self.noun_ids = list(self.noun_display_by_id.keys())

    def _load_verbs(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            verbs = json.load(f)

        # 動詞の辞書形 → verb_id
        self.verb_id_by_dict: dict[str, str] = {}
        # verb_id → 辞書形
        self.verb_dict_by_id: dict[str, str] = {}

        for verb in verbs:
            vid = verb["id"]
            dict_form = verb["dict"]  # 例: "投げる"
            self.verb_id_by_dict[dict_form] = vid
            self.verb_dict_by_id[vid] = dict_form

        self.verb_ids = list(self.verb_dict_by_id.keys())

    def _load_actions(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            actions = json.load(f)

        # action_id → { "motion": ..., "speech_template": ... }
        self.action_by_id: dict[str, dict] = {a["id"]: a for a in actions}
        self.action_ids = list(self.action_by_id.keys())

    # ===== ランダム対応の生成 =====

    def _generate_random_mappings(self) -> None:
        """
        (名詞ID × 動詞ID) の全組み合わせに対して、
        ランダムに action_id を割り当てる。
        """
        self.action_id_by_pair: dict[tuple[str, str], str] = {}
        for noun_id in self.noun_ids:
            for verb_id in self.verb_ids:
                action_id = random.choice(self.action_ids)
                self.action_id_by_pair[(noun_id, verb_id)] = action_id

    def show_mapping_sample(self, sample: int = 10) -> None:
        """
        ランダム対応の一部をコンソールに表示（デバッグ用）。
        """
        print("=== ランダム対応（サンプル）===")
        pairs = list(self.action_id_by_pair.items())
        random.shuffle(pairs)
        for (noun_id, verb_id), action_id in pairs[:sample]:
            noun = self.noun_display_by_id[noun_id]
            verb = self.verb_dict_by_id[verb_id]
            motion = self.action_by_id[action_id]["motion"]
            print(f"「{noun}を{verb}」 → {motion}")
        print("================================\n")

    # ===== 入力解析 =====

    def parse_command(self, text: str) -> tuple[str | None, str | None]:
        """
        入力文から (noun_id, verb_id) を取り出す。
        例: 「りんごを投げてください」→ ("apple", "throw") など。
        """
        text = unicodedata.normalize("NFKC", text)
        tokens = list(tagger(text))

        noun_id = None
        verb_id = None

        # 名詞を探す
        for w in tokens:
            if w.pos.startswith("名詞"):
                key = normalize_noun_key(w.surface)
                if key in self.noun_id_by_key:
                    noun_id = self.noun_id_by_key[key]
                    break

        # 動詞を探す（lemma = 辞書形）
        for w in tokens:
            if w.pos.startswith("動詞"):
                lemma = getattr(w.feature, "lemma", None)
                if lemma is None or lemma == "*":
                    lemma = w.surface
                if lemma in self.verb_id_by_dict:
                    verb_id = self.verb_id_by_dict[lemma]
                    break

        return noun_id, verb_id

    # ===== SotaAction の構築 =====

    def build_action_from_text(self, text: str) -> SotaAction | str:
        """
        ユーザー入力（日本語文）から SotaAction を構成して返す。

        戻り値:
          - 成功時: SotaAction インスタンス
          - 失敗時: エラーメッセージ（str）
        """
        noun_id, verb_id = self.parse_command(text)

        if noun_id is None:
            return "対応する名詞が見つかりません。"
        if verb_id is None:
            return "対応する動詞が見つかりません。"

        pair = (noun_id, verb_id)
        if pair not in self.action_id_by_pair:
            return "この組み合わせには動作が登録されていません。"

        action_id = self.action_id_by_pair[pair]
        action_def = self.action_by_id[action_id]

        noun_display = self.noun_display_by_id[noun_id]         # 例: "りんご"
        noun_for_speech = display_noun_for_speech(noun_display)  # 例: "リンゴ"
        verb_dict = self.verb_dict_by_id[verb_id]                # 例: "投げる"

        speech = action_def["speech_template"].format(
            noun_disp=noun_for_speech,
            verb=verb_dict,
        )

        return SotaAction(
            motion=action_def["motion"],
            speech=speech,
        )


class GameSystem:
    """
    ゲーム全体の管理クラス。

    - CommandInterpreter: 入力解析 & SotaAction生成
    - SotaController: 実際の「動き」と「発話」を担当
    """

    def __init__(self, nouns: str, verbs: str, actions: str, seed: int | None = 42):
        self.interpreter = CommandInterpreter(
            nouns_path=nouns,
            verbs_path=verbs,
            actions_path=actions,
            seed=seed,
        )
        self.sota = SotaController(debug_print=True)

    def show_mapping_sample(self, sample: int = 10) -> None:
        """対応表サンプルを表示（game_run から呼ぶ用のラッパ）"""
        self.interpreter.show_mapping_sample(sample=sample)

    def run_command(self, text: str) -> None:
        """
        ユーザー入力を解析し、Sota の動作＋発話を実行する。
        """
        result = self.interpreter.build_action_from_text(text)

        if isinstance(result, str):
            # エラーメッセージ
            print(result)
            return

        action: SotaAction = result

        # ここで「動き」と「発話」を分けて呼び出す
        self.sota.move(action.motion)
        self.sota.speak(action.speech)
        # まとめてやりたければ:
        # self.sota.perform_action(action)
