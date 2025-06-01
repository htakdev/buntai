from models import Style


def create_prompt(style: Style, input_text: str) -> str:
    """プロンプトを作成する"""
    system_message = f"あなたは文章の文体を{style.name}が用いる文体に変換する専門家です。"
    if not style.examples:
        return system_message

    system_message += "\n\n以下の例を参考にしてください：\n"
    for example in style.examples:
        if not example.input or not example.output:
            raise ValueError("例文の入力または出力が空です。")
        system_message += f"\n入力：{example.input}\n出力：{example.output}\n"
    return system_message
