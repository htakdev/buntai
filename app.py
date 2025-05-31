import streamlit as st
from dotenv import load_dotenv
from firebase_operations import initialize_firebase, load_styles
from ui_components import render_style_editor, render_text_converter

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
