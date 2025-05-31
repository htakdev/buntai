import pytest
from playwright.sync_api import Page, expect
import subprocess
import time
import os
import signal
import sys

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="module")
def streamlit_process():
    """Streamlitプロセスを起動するフィクスチャ"""
    # Streamlitプロセスを起動
    process = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # サーバーが起動するまで待機
    time.sleep(10)  # 待機時間を10秒に延長

    yield process

    # テスト終了後にプロセスを終了
    process.send_signal(signal.SIGTERM)
    process.wait()

@pytest.fixture(scope="function")
def page(browser):
    """新しいブラウザページを作成するフィクスチャ"""
    page = browser.new_page()
    page.set_default_timeout(5000)
    yield page
    page.close()

def test_add_new_style_successfully(page: Page, streamlit_process):
    """新しい文体を追加するテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 新しい文体の入力
    page.wait_for_selector("input[aria-label='追加する文体の名称（名称も結果に影響します）']")
    page.fill("input[aria-label='追加する文体の名称（名称も結果に影響します）']", "テスト文体")

    # 追加ボタンをクリック
    page.click("button:has-text('追加')")

    # 成功メッセージの確認
    expect(page.locator("text=「テスト文体」を追加しました。")).to_be_visible()

def test_show_error_when_adding_style_without_name(page: Page, streamlit_process):
    """文体名のバリデーションテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 空の文体名で追加を試みる
    page.click("button:has-text('追加')")

    # 警告メッセージの確認
    expect(page.locator("text=文体の名称を入力してください。")).to_be_visible()

def test_add_example_to_existing_style(page: Page, streamlit_process):
    """既存の文体の例文を追加するテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 例文の編集タブを選択
    page.wait_for_selector("text=例文の編集")
    page.click("text=例文の編集")

    # 例文を追加ボタンをクリック
    page.fill("textarea[aria-label='変換前の例文']", "さようなら")
    page.fill("textarea[aria-label='変換後の例文']", "さようならでございます")
    page.click("button:has-text('例文を追加')")

    # 成功メッセージの確認
    expect(page.locator("text=例文を追加しました。")).to_be_visible()

    # 例文が追加されているかの確認
    expect(page.locator("text=例文 1")).to_be_visible()

def test_show_error_when_adding_empty_example(page: Page, streamlit_process):
    """空の例文での追加試行のテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 例文の編集タブを選択
    page.wait_for_selector("text=例文の編集")
    page.click("text=例文の編集")

    # 両方の例文が未入力の状態で追加を試みる
    page.click("button:has-text('例文を追加')")

    # 警告メッセージの確認
    expect(page.locator("text=変換前と変換後の例文を両方入力してください。")).to_be_visible()

    # 変換前の例文のみ入力
    page.fill("textarea[aria-label='変換前の例文']", "こんにちは")
    page.click("button:has-text('例文を追加')")

    # 警告メッセージの確認
    expect(page.locator("text=変換前と変換後の例文を両方入力してください。")).to_be_visible()

    # 変換後の例文のみ入力
    page.fill("textarea[aria-label='変換前の例文']", "")
    page.fill("textarea[aria-label='変換後の例文']", "こんにちはでございます")
    page.click("button:has-text('例文を追加')")

    # 警告メッセージの確認
    expect(page.locator("text=変換前と変換後の例文を両方入力してください。")).to_be_visible()

def test_convert_text_using_selected_style(page: Page, streamlit_process):
    """テキスト変換機能のテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # テキストを入力
    page.fill("textarea[aria-label='変換したい文章を入力してください']", "こんにちは")

    # 変換ボタンをクリック
    page.click("button:has-text('変換開始')")

    # 変換結果の確認
    expect(page.locator("text=こんにちはでございます")).to_be_visible()

def test_show_error_when_converting_without_text(page: Page, streamlit_process):
    """文体と文章が入力されていない状態での変換試行のテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 変換ボタンをクリック
    page.click("button:has-text('変換開始')")

    # 警告メッセージの確認
    expect(page.locator("text=文体を選択してください。")).to_be_visible()

def test_show_error_when_converting_without_text_after_selecting_style(page: Page, streamlit_process):
    """文体は選択されているが文章が入力されていない状態での変換試行のテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # 変換ボタンをクリック
    page.click("button:has-text('変換開始')")

    # 警告メッセージの確認
    expect(page.locator("text=文章を入力してください。")).to_be_visible()

def test_show_error_when_converting_without_selecting_style(page: Page, streamlit_process):
    """文体が選択されていない状態での変換試行のテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # テキストを入力
    page.fill("textarea[aria-label='変換したい文章を入力してください']", "こんにちは")

    # 変換ボタンをクリック
    page.click("button:has-text('変換開始')")

    # 警告メッセージの確認
    expect(page.locator("text=文体を選択してください。")).to_be_visible()

def test_delete_all_examples_from_style(page: Page, streamlit_process):
    """既存の文体の例文を削除するテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 例文の編集タブを選択
    page.wait_for_selector("text=例文の編集")
    page.click("text=例文の編集")

    # 複数の例文を1つずつ削除できることを確認するため一旦追加する
    page.fill("textarea[aria-label='変換前の例文']", "すぐに削除")
    page.fill("textarea[aria-label='変換後の例文']", "すぐに削除でございます")
    page.click("button:has-text('例文を追加')")

    # 例文 2を削除
    # ラベルが「削除」のボタンが複数あるのでhas-textは使わない
    page.click("details:has-text('例文 2')")
    delete_example2_button = page.locator("div[class*='st-key-delete_example_2'] button")
    delete_example2_button.wait_for()
    delete_example2_button.click()

    # 成功メッセージの確認
    expect(page.locator("text=例文を削除しました。")).to_be_visible()

    # 例文 1を削除
    # ラベルが「削除」のボタンが複数あるのでhas-textは使わない
    page.click("details:has-text('例文 1')")
    delete_example1_button = page.locator("div[class*='st-key-delete_example_1'] button")
    delete_example1_button.wait_for()
    delete_example1_button.click()

    # 成功メッセージの確認
    expect(page.locator("text=例文は未登録です。")).to_be_visible()

def test_rename_style_successfully(page: Page, streamlit_process):
    """既存の文体の名称を編集するテスト（正常系）"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=テスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 名称の変更タブを選択
    page.wait_for_selector("text=名称の変更")
    page.click("text=名称の変更")

    # 新しい文体の入力
    page.wait_for_selector("input[aria-label='変更後の名称']")
    page.fill("input[aria-label='変更後の名称']", "名称変更後のテスト文体")

    # 名称を変更ボタンをクリック
    page.click("button:has-text('名称を変更')")

    # 成功メッセージの確認
    expect(page.locator("text=「テスト文体」を「名称変更後のテスト文体」に変更しました。")).to_be_visible()

def test_show_error_when_renaming_to_existing_style_name(page: Page, streamlit_process):
    """既存の文体の名称をすでにある名称に編集しようとするテスト（異常系）"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=名称変更後のテスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 名称の変更タブを選択
    page.wait_for_selector("text=名称の変更")
    page.click("text=名称の変更")

    # 新しい文体の入力
    page.wait_for_selector("input[aria-label='変更後の名称']")
    page.fill("input[aria-label='変更後の名称']", "名称変更後のテスト文体")

    # 名称を変更ボタンをクリック
    page.click("button:has-text('名称を変更')")

    # 警告メッセージの確認
    expect(page.locator("text=この名称はすでに存在します。")).to_be_visible()

def test_delete_style_successfully(page: Page, streamlit_process):
    """文体を削除するテスト"""
    # Streamlitアプリにアクセス
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")

    # 既存の文体を選択
    page.wait_for_selector("div.stSelectbox")
    page.click("div.stSelectbox")
    page.click("text=名称変更後のテスト文体")

    # 文体編集ボタンをクリック
    page.wait_for_selector("button:has-text('✏️ 文体を編集する')")
    page.click("button:has-text('✏️ 文体を編集する')")

    # 文体の削除タブを選択
    page.wait_for_selector("text=文体の削除")
    page.click("text=文体の削除")

    # 削除ボタンをクリック
    # ラベルに「削除」を含むボタンが他のコンポーネントにもあるのでhas-textは使わない
    delete_style_button = page.locator("div[class*='st-key-delete_style'] button")
    delete_style_button.wait_for()
    delete_style_button.click()

    # 成功メッセージの確認
    expect(page.locator("text=「名称変更後のテスト文体」を削除しました。")).to_be_visible()
