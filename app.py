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
    style = st.selectbox(
        "変換後の文体を選択してください",
        ["起業家", "Webエンジニア", "JTC部長", "AWS公式サイト", "限界オタク"]
    )

# 入力エリア
input_text = st.text_area("変換したい文章を入力してください", height=200)

# 変換ボタン
if st.button("変換開始"):
    if not input_text:
        st.warning("文章を入力してください。")
    else:
        # プロンプトの作成
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"あなたは文章の文体を{style}に変換する専門家です。入力された文章を指定された文体に変換してください。変換結果だけを出力してください。"),
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