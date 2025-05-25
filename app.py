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
        st.session_state.selected_style = st.session_state.styles[0] if st.session_state.styles else None
    if 'editing_style' not in st.session_state:
        st.session_state.editing_style = None
    
    # 文体の選択
    style = st.selectbox(
        "変換後の文体を選択してください",
        ["文体を選択してください"] + st.session_state.styles,
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
        
        # 警告メッセージ用のコンテナ
        add_warning_container = st.empty()
        
        if st.button("追加", use_container_width=True):
            if not new_style:
                add_warning_container.warning("文体名を入力してください。")
            elif new_style in st.session_state.styles:
                add_warning_container.warning("この文体は既に存在します。")
            else:
                st.session_state.styles.append(new_style)
                st.session_state.selected_style = new_style
                st.success(f"「{new_style}」を追加しました！")
                st.rerun()
        
        # 文体の削除
        st.markdown("#### 文体の編集・削除")
        style_to_edit = st.selectbox(
            "編集または削除する文体を選択",
            ["文体を選択してください"] + st.session_state.styles,
            index=st.session_state.styles.index(st.session_state.editing_style) + 1 if st.session_state.editing_style in st.session_state.styles else 0
        )
        new_style_name = st.text_input("変更後の名称")
        
        # 警告メッセージ用のコンテナ
        edit_warning_container = st.empty()
        
        # ボタンを横並びに配置
        col1, col2 = st.columns(2)
        with col1:
            if st.button("編集", use_container_width=True):
                if style_to_edit == "文体を選択してください":
                    edit_warning_container.warning("編集する文体を選択してください。")
                elif not new_style_name:
                    edit_warning_container.warning("新しい名称を入力してください。")
                elif new_style_name in st.session_state.styles:
                    edit_warning_container.warning("この名称は既に存在します。")
                else:
                    # 選択中の文体を更新
                    if st.session_state.selected_style == style_to_edit:
                        st.session_state.selected_style = new_style_name
                    # 文体リストを更新
                    idx = st.session_state.styles.index(style_to_edit)
                    st.session_state.styles[idx] = new_style_name
                    st.session_state.editing_style = new_style_name  # 編集後の文体を保持
                    st.success(f"「{style_to_edit}」を「{new_style_name}」に変更しました。")
                    st.rerun()
        
        with col2:
            if st.button("削除", use_container_width=True, type="primary"):
                if style_to_edit == "文体を選択してください":
                    edit_warning_container.warning("削除する文体を選択してください。")
                else:
                    st.session_state.styles.remove(style_to_edit)
                    if st.session_state.selected_style == style_to_edit:
                        st.session_state.selected_style = st.session_state.styles[0] if st.session_state.styles else None
                    st.session_state.editing_style = None  # 削除時は編集状態をクリア
                    st.success(f"「{style_to_edit}」を削除しました。")
                    st.rerun()

# 入力エリア
input_text = st.text_area("変換したい文章を入力してください", height=200)

# 警告メッセージ用のコンテナ
convert_warning_container = st.empty()

# 変換ボタン
if st.button("変換開始"):
    if style == "文体を選択してください":
        convert_warning_container.warning("文体を選択してください。")
    elif not input_text:
        convert_warning_container.warning("文章を入力してください。")
    else:
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"あなたは文章の文体を{style}が用いる文体に変換する専門家です。入力された文章を指定された文体に変換してください。変換結果だけを出力してください。"),
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