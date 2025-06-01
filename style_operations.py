from typing import List, Optional, Tuple

from models import Example, Style


def create_style(name: str) -> Style:
    """新しい文体を作成する"""
    return Style(name=name, examples=[])

def add_example(style: Style, input_text: str, output_text: str) -> Style:
    """文体に例文を追加する"""
    return Style(
        name=style.name,
        examples=style.examples + [Example(input=input_text, output=output_text)]
    )

def remove_example(style: Style, index: int) -> Style:
    """文体から例文を削除する"""
    new_examples = [ex for i, ex in enumerate(style.examples) if i != index]
    return Style(name=style.name, examples=new_examples)

def rename_style(style: Style, new_name: str) -> Style:
    """文体の名前を変更する"""
    return Style(name=new_name, examples=style.examples)

def validate_style_name(name: str, existing_styles: List[Style]) -> Tuple[bool, Optional[str]]:
    """文体名のバリデーション"""
    if not name:
        return False, "文体の名称を入力してください。"
    if any(style.name == name for style in existing_styles):
        return False, "この名称はすでに存在します。"
    return True, None

def validate_example(input_text: str, output_text: str) -> Tuple[bool, Optional[str]]:
    """例文のバリデーション"""
    if not input_text or not output_text:
        return False, "変換前と変換後の例文を両方入力してください。"
    return True, None
