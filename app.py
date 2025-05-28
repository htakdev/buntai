import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# 環境変数の読み込み
load_dotenv()

# ページ設定
st.set_page_config(
    page_title="文体さん",
    page_icon="📝",
    layout="wide"
)

# Firebase初期化
if not firebase_admin._apps:
    try:
        # Streamlit Community Cloud環境の場合
        cred = credentials.Certificate(dict(st.secrets["firebase"]))
    except:
        # ローカル環境の場合
        cred = credentials.Certificate('firebase-credentials.json')
    
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
    })

@st.dialog("文体の編集")
def edit_style_dialog(style_to_edit):
    # 新しい文体の追加
    st.markdown("#### 新しい文体を追加")
    new_style = st.text_input("追加する文体の名称（名称も結果に影響します）")
    
    # 警告メッセージ用のコンテナ
    add_warning_container = st.empty()
    
    if st.button("追加", use_container_width=True):
        if not new_style:
            add_warning_container.warning("文体の名称を入力してください。")
        elif any(style["name"] == new_style for style in st.session_state.styles):
            add_warning_container.warning("この文体は既に存在します。")
        else:
            st.session_state.styles.append({
                "name": new_style,
                "examples": [
                    {
                        "input": "",
                        "output": ""
                    }
                ]
            })
            st.session_state.selected_style = new_style
            save_styles(st.session_state.styles)  # 変更を保存
            st.success(f"「{new_style}」を追加しました！")
            st.rerun()
    
    # 文体の削除
    st.markdown("#### 文体の編集・削除")
    
    if style_to_edit == "文体を選択してください":
        st.warning("先に文体を選択してください。")
        return
    else:
        # タブの作成
        tab1, tab2, tab3 = st.tabs(["例文の編集", "名称の変更", "文体の削除"])
        
        with tab1:
            st.markdown(f"##### 例文の編集：{style_to_edit}")
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
                            if len(selected_style["examples"]) == 0:
                                selected_style["examples"].append({
                                    "input": "",
                                    "output": ""
                                })

                            save_styles(st.session_state.styles)  # 変更を保存
                            st.rerun()
            
            # 新しい例文の追加
            st.markdown("###### 新しい例文の追加")
            if 'new_example_input' not in st.session_state:
                st.session_state.new_example_input = ""
            if 'new_example_output' not in st.session_state:
                st.session_state.new_example_output = ""
            
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
                    save_styles(st.session_state.styles)  # 変更を保存
                    st.success("例文を追加しました。")
                    # 入力欄をクリア
                    del st.session_state.new_example_input
                    del st.session_state.new_example_output
                    st.rerun()
        
        with tab2:
            st.markdown(f"##### 変更前の名称：{style_to_edit}")
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
                    save_styles(st.session_state.styles)  # 変更を保存
                    st.success(f"「{style_to_edit}」を「{new_style_name}」に変更しました。")
                    st.rerun()
        
        with tab3:
            st.markdown(f"##### 削除する文体：{style_to_edit}")
            st.warning(f"「{style_to_edit}」を削除しますか？ この操作は取り消せません。")
            if st.button("削除", use_container_width=True, type="primary"):
                st.session_state.styles = [style for style in st.session_state.styles if style["name"] != style_to_edit]
                if st.session_state.selected_style == style_to_edit:
                    st.session_state.selected_style = st.session_state.styles[0]["name"] if st.session_state.styles else None
                st.session_state.editing_style = None  # 削除時は編集状態をクリア
                save_styles(st.session_state.styles)  # 変更を保存
                st.success(f"「{style_to_edit}」を削除しました。")
                st.rerun()


def load_styles():
    """文体データをFirebaseから読み込む"""
    try:
        ref = db.reference('/styles')
        data = ref.get()
        if data:
            return data
        return []  # データが存在しない場合は空のリストを返す
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return []


def save_styles(styles):
    """文体データをFirebaseに保存"""
    try:
        ref = db.reference('/styles')
        ref.set(styles)
    except Exception as e:
        st.error(f"データの保存に失敗しました: {str(e)}")


# タイトル
st.title("📝 文体さん")
st.markdown("入力された文章を指定した文体に変換します。")

# セッション状態の初期化
if 'styles' not in st.session_state:
    st.session_state.styles = load_styles()
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = st.session_state.styles[0]["name"] if st.session_state.styles else None
if 'editing_style' not in st.session_state:
    st.session_state.editing_style = None

col1, col2 = st.columns([3, 1])
with col1:
    style = st.selectbox(
        "変換後の文体を選択してください", # label_visibility="collapsed"により非表示
        ["文体を選択してください"] + [style["name"] for style in st.session_state.styles],
        key="style_selector",
        label_visibility="collapsed"
    )
with col2:
    if st.button("✏️ 文体を編集する", use_container_width=True):
        edit_style_dialog(style)

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