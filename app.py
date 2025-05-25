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
        st.session_state.styles = [
            {
                "name": "起業家",
                "examples": [
                    {
                        "input": "吾輩は猫である。名前はまだ無い。",
                        "output": "私は、革新的なビジョンと強いリーダーシップを持つ起業家です。まだ具体的な名前はありませんが、それは私の柔軟性と可能性の証です。"
                    }
                ]
            },
            {
                "name": "Webエンジニア",
                "examples": [
                    {
                        "input": "吾輩は猫である。名前はまだ無い。",
                        "output": "私は、HTMLとCSSで構築された猫です。まだ名前は未定義ですが、それは後で変数として定義できます。"
                    }
                ]
            },
            {
                "name": "JTC部長",
                "examples": [
                    {
                        "input": "吾輩は猫である。名前はまだ無い。",
                        "output": "我々は、効率的な猫の運用を目指しています。現時点では名前は未定ですが、これは適切なタイミングで決定される予定です。"
                    }
                ]
            },
            {
                "name": "AWS公式サイト",
                "examples": [
                    {
                        "input": "吾輩は猫である。名前はまだ無い。",
                        "output": "吾輩は優れた柔軟性、スケーラビリティ、および信頼性を備えた高度な猫である。名前はまだ無いが、これは将来の拡張性を考慮した設計である。"
                    }
                ]
            },
            {
                "name": "限界オタク",
                "examples": [
                    {
                        "input": "吾輩は猫である。名前はまだ無い。",
                        "output": "私、猫という生き物に命を捧げる者です！まだ名前はありませんが、それは私のキャラクター性をより際立たせるための伏線です！"
                    }
                ]
            }
        ]
    if 'show_edit_style' not in st.session_state:
        st.session_state.show_edit_style = False
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = st.session_state.styles[0]["name"] if st.session_state.styles else None
    if 'editing_style' not in st.session_state:
        st.session_state.editing_style = None
    
    # 文体の選択
    style = st.selectbox(
        "変換後の文体を選択してください",
        ["文体を選択してください"] + [style["name"] for style in st.session_state.styles],
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
            elif any(style["name"] == new_style for style in st.session_state.styles):
                add_warning_container.warning("この文体は既に存在します。")
            else:
                st.session_state.styles.append({
                    "name": new_style,
                    "examples": []
                })
                st.session_state.selected_style = new_style
                st.success(f"「{new_style}」を追加しました！")
                st.rerun()
        
        # 文体の削除
        st.markdown("#### 文体の編集・削除")
        style_to_edit = st.selectbox(
            "編集または削除する文体を選択",
            ["文体を選択してください"] + [style["name"] for style in st.session_state.styles],
            index=[style["name"] for style in st.session_state.styles].index(st.session_state.editing_style) + 1 if st.session_state.editing_style in [style["name"] for style in st.session_state.styles] else 0
        )
        
        if style_to_edit != "文体を選択してください":
            # タブの作成
            tab1, tab2, tab3 = st.tabs(["例文の編集", "文体の名称の変更", "文体の削除"])
            
            with tab1:
                st.markdown("##### 例文の編集")
                # 現在の例文の表示
                selected_style = next((s for s in st.session_state.styles if s["name"] == style_to_edit), None)
                if selected_style and selected_style["examples"]:
                    st.markdown("###### 現在の例文")
                    for i, example in enumerate(selected_style["examples"], 1):
                        with st.expander(f"例文 {i}"):
                            st.markdown(f"**入力：**\n{example['input']}")
                            st.markdown(f"**出力：**\n{example['output']}")
                            if st.button("削除", key=f"delete_example_{i}", type="primary"):
                                selected_style["examples"].pop(i-1)
                                st.success("例文を削除しました。")
                                st.rerun()
                
                # 新しい例文の追加
                st.markdown("###### 新しい例文の追加")
                new_example_input = st.text_area("変換前の例文", key="new_example_input")
                new_example_output = st.text_area("変換後の例文", key="new_example_output")
                
                if st.button("例文を追加", use_container_width=True):
                    if not new_example_input or not new_example_output:
                        st.warning("変換前と変換後の例文を両方入力してください。")
                    else:
                        selected_style["examples"].append({
                            "input": new_example_input,
                            "output": new_example_output
                        })
                        st.success("例文を追加しました。")
                        st.rerun()
            
            with tab2:
                st.markdown("##### 文体の名称の変更")
                new_style_name = st.text_input("変更後の名称")
                
                # 警告メッセージ用のコンテナ
                edit_warning_container = st.empty()
                
                if st.button("名称を変更", use_container_width=True):
                    if not new_style_name:
                        edit_warning_container.warning("新しい名称を入力してください。")
                    elif any(style["name"] == new_style_name for style in st.session_state.styles):
                        edit_warning_container.warning("この名称は既に存在します。")
                    else:
                        # 選択中の文体を更新
                        if st.session_state.selected_style == style_to_edit:
                            st.session_state.selected_style = new_style_name
                        # 文体リストを更新
                        for style in st.session_state.styles:
                            if style["name"] == style_to_edit:
                                style["name"] = new_style_name
                                break
                        st.session_state.editing_style = new_style_name  # 編集後の文体を保持
                        st.success(f"「{style_to_edit}」を「{new_style_name}」に変更しました。")
                        st.rerun()
            
            with tab3:
                st.markdown("##### 文体の削除")
                st.warning(f"「{style_to_edit}」を削除しますか？この操作は取り消せません。")
                if st.button("削除", use_container_width=True, type="primary"):
                    st.session_state.styles = [style for style in st.session_state.styles if style["name"] != style_to_edit]
                    if st.session_state.selected_style == style_to_edit:
                        st.session_state.selected_style = st.session_state.styles[0]["name"] if st.session_state.styles else None
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
        # 選択された文体の例文を取得
        selected_style_data = next((s for s in st.session_state.styles if s["name"] == style), None)
        examples = selected_style_data["examples"] if selected_style_data else []
        
        # プロンプトの作成
        system_message = f"あなたは文章の文体を{style}が用いる文体に変換する専門家です。"
        if examples:
            system_message += "\n\n以下の例を参考にしてください：\n"
            for example in examples:
                system_message += f"\n入力：{example['input']}\n出力：{example['output']}\n"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message + "\n\n入力された文章を指定された文体に変換してください。変換結果だけを出力してください。"),
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