import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="文体さん",
    page_icon="📝",
    layout="wide"
)

# タイトル
st.title("📝 文体さん")
st.markdown("入力された文章を指定した文体に変換します。")

# サイドバーで文体の選択
with st.sidebar:
    st.header("設定")
    
    # セッション状態の初期化
    if 'styles' not in st.session_state:
        st.session_state.styles = ["起業家", "Webエンジニア", "JTC部長", "AWS公式サイト", "限界オタク"]
    if 'show_edit_style' not in st.session_state:
        st.session_state.show_edit_style = False
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = st.session_state.styles[0]
    
    # 文体の選択
    style = st.selectbox(
        "変換後の文体を選択してください",
        st.session_state.styles,
        key="style_selector"
    )
    
    # 文体編集の折りたたみ
    st.markdown("---")
    if st.button("✏️ 文体を編集する", use_container_width=True):
        st.session_state.show_edit_style = not st.session_state.show_edit_style
    
    if st.session_state.show_edit_style:
        st.markdown("### 文体の編集")
        
        # 新しい文体の追加
        st.markdown("#### 新しい文体を追加")
        new_style = st.text_input("追加する文体名を入力")
        if st.button("追加", use_container_width=True):
            if not new_style:
                st.warning("文体名を入力してください。")
            elif new_style in st.session_state.styles:
                st.warning("この文体は既に存在します。")
            else:
                st.session_state.styles.append(new_style)
                st.session_state.selected_style = new_style
                st.success(f"「{new_style}」を追加しました！")
                st.rerun()
        
        # 文体の削除
        if len(st.session_state.styles) > 1:  # 最低1つは残す
            st.markdown("#### 文体の削除")
            style_to_remove = st.selectbox("削除する文体を選択", st.session_state.styles)
            if st.button("削除", use_container_width=True):
                st.session_state.styles.remove(style_to_remove)
                if st.session_state.selected_style == style_to_remove:
                    st.session_state.selected_style = st.session_state.styles[0]
                st.success(f"「{style_to_remove}」を削除しました。")
                st.rerun()

# 入力エリア
input_text = st.text_area("変換したい文章を入力してください", height=200)

# 変換ボタン
if st.button("変換開始"):
    if not input_text:
        st.warning("文章を入力してください。")
    else:
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"あなたは文章の文体を{style}風に変換する専門家です。入力された文章を指定された文体に変換してください。変換結果だけを出力してください。"),
            ("user", "{input}")
        ])

        # モデルの設定
        model = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.7,
            streaming=True
        )

        # チェーンの構築
        chain = (
            {"input": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
        )

        # 出力エリア
        output_container = st.empty()
        output_text = ""

        # ストリーミング出力
        for chunk in chain.stream(input_text):
            output_text += chunk
            output_container.markdown(output_text) 