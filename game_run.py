# game_run.py

from game_system import GameSystem

def main():
    game = GameSystem(
        nouns="nouns.json",
        verbs="verbs.json",
        actions="actions.json",
        seed=42
    )

    game.interpreter.show_mapping_sample(sample=8)

    print("Sotaコマンドゲーム開始！")
    print("例：「りんごを投げてください」「ボールを押して」など")
    print("終了するには「終了」と入力。\n")

    while True:
        user_input = input("あなた > ").strip()
        if user_input in ["終了", "exit", "quit"]:
            print("終了します。")
            break
        game.run_command(user_input)

if __name__ == "__main__":
    main()
