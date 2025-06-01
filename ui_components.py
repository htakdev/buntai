import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain_openai import ChatOpenAI

from firebase_operations import save_styles
from prompt_operations import create_prompt
from style_operations import (
    add_example,
    create_style,
    remove_example,
    rename_style,
    validate_example,
    validate_style_name,
)


@st.dialog("文体の編集")
def render_style_editor(style_to_edit: str, on_example_modified: bool = False):
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
        selected_style = next((style for style in st.session_state.styles if style.name == style_to_edit))
        valid_examples = [example for example in selected_style.examples if example.input and example.output]

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
                        style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit))
                        st.session_state.styles[style_index] = new_style
                        save_styles(st.session_state.styles)
                        st.session_state.success_message_in_modal = "例文を削除しました。"
                        st.session_state.on_example_modified = True
                        st.rerun()

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
        if st.button("削除", key="delete_style", use_container_width=True, type="primary"):
            style_index = next((i for i, style in enumerate(st.session_state.styles) if style.name == style_to_edit))
            st.session_state.styles.pop(style_index)
            st.session_state.editing_style = None
            save_styles(st.session_state.styles)
            st.session_state.success_message = f"「{style_to_edit}」を削除しました。"
            st.rerun()

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
            selected_style = next((style for style in st.session_state.styles if style.name == st.session_state.selected_style))

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
