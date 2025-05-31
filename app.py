import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from typing import List, Dict, Optional, Tuple, TypeAlias
from dataclasses import dataclass
from functools import partial

@dataclass
class Example:
    input: str
    output: str

@dataclass
class Style:
    name: str
    examples: List[Example]

Styles: TypeAlias = List[Style]

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

def initialize_firebase():
    """Firebaseの初期化"""
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
        except:
            cred = credentials.Certificate('firebase-credentials.json')
        
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
        })

def load_styles() -> Styles:
    """文体データをFirebaseから読み込む"""
    try:
        ref = db.reference('/styles')
        data = ref.get()
        if not data:
            return []

        styles = []
        for style in data:
            examples = []
            for example in style.get('examples', []):
                examples.append(Example(
                    input=example.get('input', ''),
                    output=example.get('output', '')
                ))
            styles.append(Style(
                name=style.get('name', ''),
                examples=examples
            ))
        return styles
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return []

def save_styles(styles: Styles):
    """文体データをFirebaseに保存"""
    try:
        ref = db.reference('/styles')
        # 既存のデータを削除
        ref.delete()
        # 新しいデータを保存
        for i, style in enumerate(styles):
            style_ref = ref.child(str(i))
            style_ref.set({
                'name': style.name,
                'examples': {
                    str(j): {
                        'input': example.input,
                        'output': example.output
                    } for j, example in enumerate(style.examples)
                }
            })
    except Exception as e:
        st.error(f"データの保存に失敗しました: {str(e)}")

# UI関連の関数
@st.dialog("文体の編集")
def render_style_editor(style_to_edit, on_example_modified=False):
    """文体エディタのUIを描画"""
    st.markdown("#### 新しい文体を追加")
    new_style = st.text_input("追加する文体の名称（名称も結果に影響します）")
    
    add_warning_container = st.empty()
    
    if st.button("追加", use_container_width=True):
        is_valid, error_message = validate_style_name(new_style, st.session_state.styles)
        if not is_valid:
            add_warning_container.warning(error_message)
        else:
            st.session_state.styles.append(create_style(new_style))
            st.session_state.selected_style = new_style
            save_styles(st.session_state.styles)
            st.session_state.success_message = f"「{new_style}」を追加しました。"
            st.rerun()

    st.markdown("#### 文体の編集・削除")
    
    if style_to_edit == "文体を選択してください":
        st.warning("先に文体を選択してください。")
        return

    tab1, tab2, tab3 = st.tabs(["例文の編集", "名称の変更", "文体の削除"])
    
    with tab1:
        st.markdown(f"##### 例文の編集：{style_to_edit}")
        selected_style = next((style for style in st.session_state.styles if style.name == style_to_edit), None)
        valid_examples = [ex for ex in selected_style.examples if ex.input and ex.output]

        if not valid_examples:
            st.warning("例文は未登録です。")
        else:
            st.markdown("###### 現在の例文")
            for i, example in enumerate(valid_examples, 1):
                with st.expander(f"例文 {i}"):
                    st.markdown(f"**入力：**\n{example.input}")
                    st.markdown(f"**出力：**\n{example.output}")
                    if st.button("削除", key=f"delete_example_{i}", type="primary"):
                        new_style = remove_example(selected_style, i-1)
                        style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit), None)
                        if style_index is not None:
                            st.session_state.styles[style_index] = new_style
                            save_styles(st.session_state.styles)
                            st.session_state.success_message_in_modal = "例文を削除しました。"
                            st.session_state.on_example_modified = True
                            st.rerun()
                        else:
                            st.error("文体が見つかりませんでした。")

        if on_example_modified:
            st.success(st.session_state.success_message_in_modal)

        st.markdown("###### 新しい例文の追加")
        if 'new_example_input' not in st.session_state:
            st.session_state.new_example_input = ""
        if 'new_example_output' not in st.session_state:
            st.session_state.new_example_output = ""
        
        new_example_input = st.text_area("変換前の例文", key="new_example_input")
        new_example_output = st.text_area("変換後の例文", key="new_example_output")
        
        if st.button("例文を追加", use_container_width=True):
            is_valid, error_message = validate_example(new_example_input, new_example_output)
            if not is_valid:
                st.warning(error_message)
            else:
                # 選択された文体のインデックスを取得
                style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit), None)
                if style_index is not None:
                    new_style = add_example(selected_style, new_example_input, new_example_output)
                    st.session_state.styles[style_index] = new_style
                    save_styles(st.session_state.styles)
                    del st.session_state.new_example_input
                    del st.session_state.new_example_output
                    st.session_state.success_message_in_modal = "例文を追加しました。"
                    st.session_state.on_example_modified = True
                    st.rerun()
                else:
                    st.error("文体が見つかりませんでした。")
    
    with tab2:
        st.markdown(f"##### 変更前の名称：{style_to_edit}")
        new_style_name = st.text_input("変更後の名称")
        
        edit_warning_container = st.empty()
        
        if st.button("名称を変更", use_container_width=True):
            is_valid, error_message = validate_style_name(new_style_name, st.session_state.styles)
            if not is_valid:
                edit_warning_container.warning(error_message)
            else:
                style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit), None)
                if style_index is not None:
                    new_style = rename_style(selected_style, new_style_name)
                    st.session_state.styles[style_index] = new_style
                    st.session_state.editing_style = new_style_name
                    save_styles(st.session_state.styles)
                    st.session_state.success_message = f"「{style_to_edit}」を「{new_style_name}」に変更しました。"
                    st.rerun()
                else:
                    st.error("文体が見つかりませんでした。")
    
    with tab3:
        st.markdown(f"##### 削除する文体：{style_to_edit}")
        st.warning(f"「{style_to_edit}」を削除しますか？ この操作は取り消せません。")
        if st.button("削除", key=f"delete_style", use_container_width=True, type="primary"):
            style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit), None)
            if style_index is not None:
                st.session_state.styles.pop(style_index)
                if st.session_state.selected_style == style_to_edit:
                    st.session_state.selected_style = "文体を選択してください"
                st.session_state.editing_style = None
                save_styles(st.session_state.styles)
                st.session_state.success_message = f"「{style_to_edit}」を削除しました。"
                st.rerun()
            else:
                st.error("文体が見つかりませんでした。")

def render_text_converter():
    """テキスト変換UIを描画"""
    input_text = st.text_area("変換したい文章を入力してください", height=200)
    convert_warning_container = st.empty()

    convert_clicked = st.button("変換開始")
    if convert_clicked:
        if st.session_state.selected_style == "文体を選択してください":
            convert_warning_container.warning("文体を選択してください。")
        elif not input_text:
            convert_warning_container.warning("文章を入力してください。")
        else:
            selected_style = next((style for style in st.session_state.styles if style.name == st.session_state.selected_style), None)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", create_prompt(selected_style, input_text) + 
                          "\n\n入力された文章を指定された文体に変換してください。変換結果だけを出力してください。"),
                ("user", "{input}")
            ])

            model = ChatOpenAI(
                model="gpt-4.1",
                temperature=0.7,
                streaming=True
            )

            chain = (
                {"input": RunnablePassthrough()}
                | prompt
                | model
                | StrOutputParser()
            )

            output_container = st.empty()
            output_text = ""

            for chunk in chain.stream(input_text):
                output_text += chunk
                output_container.markdown(output_text)

# メインアプリケーション
def main():
    # 環境変数の読み込み
    load_dotenv()

    # ページ設定
    st.set_page_config(
        page_title="文体さん",
        page_icon="📝",
        layout="wide"
    )

    # Firebase初期化
    initialize_firebase()

    # タイトル
    st.title("📝 文体さん")
    st.markdown("入力された文章を指定した文体に変換します。")

    # セッション状態の初期化
    if 'styles' not in st.session_state:
        st.session_state.styles = load_styles()
    if 'editing_style' not in st.session_state:
        st.session_state.editing_style = None
    if 'on_example_modified' not in st.session_state:
        st.session_state.on_example_modified = False

    if st.session_state.on_example_modified:
        st.session_state.on_example_modified = False
        render_style_editor(st.session_state.selected_style, on_example_modified=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.session_state.selected_style = st.selectbox(
            "変換後の文体を選択してください",
            ["文体を選択してください"] + [style.name for style in st.session_state.styles],
            key="style_selector",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("✏️ 文体を編集する", use_container_width=True):
            render_style_editor(st.session_state.selected_style)

    if st.session_state.get("success_message", False):
        st.success(st.session_state.success_message)

    render_text_converter()

if __name__ == "__main__":
    main() 