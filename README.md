# 文体さん

## 目次
- [概要](#概要)
- [機能](#機能)
- [デプロイ先](#デプロイ先)
- [アプリケーションの操作方法](#アプリケーションの操作方法)
- [技術スタック](#技術スタック)
- [セットアップ手順 (ローカル環境)](#セットアップ手順-ローカル環境)
  - [環境変数の設定](#環境変数の設定)
- [セットアップ手順 (Streamlit Community Cloud)](#セットアップ手順-streamlit-community-cloud)
  - [Secretsの設定](#secretsの設定)

## 概要
「文体さん」は、入力された文章を指定した文体に変換することができるWebアプリケーションです。独自の文体を登録・管理し、様々なスタイルの文章生成を試すことができます。

## 機能
- 既存の文体を選択して文章を変換
- 新しい文体を登録
- 登録済みの文体の名称変更
- 登録済みの文体の削除
- 文体ごとに変換の例文を登録・編集・削除

## デプロイ先
このアプリケーションは以下のURLでお試しできます。このアプリケーションの所有者であるhtakが管理しています。

[https://buntai.streamlit.app/](https://buntai.streamlit.app/)

## アプリケーションの操作方法
デプロイ先のURLにアクセスし、表示されるインターフェースに従って操作してください。
1. 変換したい文体をセレクトボックスから選択します。
2. 変換したい文章を入力エリアに入力します。
3. 「変換開始」ボタンを押すと、指定した文体に変換された文章が表示されます。
4. 「文体を編集する」ボタンから、文体の追加や既存文体の編集・削除が行えます。

## 技術スタック
- Streamlit: アプリケーションのUI構築
- Python: バックエンドロジック
- Firebase Realtime Database: 文体データの保存・管理
- LangChain: 言語モデルとの連携
- OpenAI API: 文章の文体変換処理
- pytest: テストフレームワーク（デプロイには含まれません）
- Playwright: E2Eテスト用のブラウザ自動化ツール（デプロイには含まれません）

## セットアップ手順 (ローカル環境)

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/htakdev/buntai.git
    cd buntai
    ```
2.  必要なPythonライブラリをインストールします。
    ```bash
    pip install -r requirements.dev.txt
    ```
3.  下記の「[環境変数の設定](#環境変数の設定)」を参考に、必要な環境変数およびクレデンシャルを設定します。
4.  Streamlitアプリケーションを実行します。
    ```bash
    streamlit run app.py
    ```
5.  E2Eテストを実行したい場合は別のターミナルを開いて下記のコマンド実行します。
    ```bash
    # ヘッドレスモードで実行
    pytest tests/test_e2e.py -v

    # ブラウザを表示して実行
    pytest tests/test_e2e.py -v --headed
    ```

### 環境変数の設定
アプリケーションの実行には、以下の環境変数およびクレデンシャルが必要です。

1.  **Firebase Realtime Database の設定**:
    *   **クレデンシャル**: Firebaseプロジェクトのサービスアカウントキーが必要です。
        *   FirebaseからダウンロードしたサービスアカウントキーのJSONファイルをリポジトリのルートディレクトリに `firebase-credentials.json` とリネームして配置してください。**このファイルはGitHubなどにアップロードしないよう注意してください。**
    *   **Database URL**: Firebase Realtime DatabaseのURLを設定します。後述する `.env` ファイルを用意する方法がお勧めです。
        *   環境変数 `FIREBASE_DATABASE_URL` に、FirebaseプロジェクトのDatabase URL (例: `https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com`) を設定してください。

2.  **OpenAI API キーの設定**:
    *   環境変数 `OPENAI_API_KEY` に、OpenAIのAPIキーを設定してください。後述する `.env` ファイルを用意する方法がお勧めです。

3.  **実行環境を識別するための環境変数の設定**:
    *   環境変数 `APP_ENV` に `"local"` を設定してください。後述する `.env` ファイルを用意する方法がお勧めです。

プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の形式で環境変数を記述するのが便利です。**このファイルはGitHubなどにアップロードしないよう注意してください。**

```env
FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
APP_ENV=local
```

## セットアップ手順 (Streamlit Community Cloud)

下記のURLを参照してください。おそらくご自身のGitHubリポジトリにフォークして実施することになると思います。

[Quickstart - Streamlit Docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/quickstart)

注意点として、デプロイの設定画面の `Branch` にあらかじめ `master` と記入されていますが、 `main` に変更してください。同様に `Main file path` に `streamlit_app.py` と記入されていますが、 `app.py` に変更してください。

その他、セットアップに必要なSecretsの設定は次の項目を参照してください。

### Secretsの設定
アプリケーションの実行には、以下の環境変数およびクレデンシャルをSecretsに設定することが必要です。

1.  **Firebase Realtime Database の設定**:
    *   **クレデンシャル**: Firebaseプロジェクトのサービスアカウントキーが必要です。
        *   ソースコード上で `st.secrets["firebase"]` としてアクセスできるよう、Streamlit Community CloudのSecrets管理画面でサービスアカウントキーの内容を登録してください。TOMLの仕様により、末尾に記述することが必要なようです。下記の書式例を参照してください。
    *   **Database URL**: Firebase Realtime DatabaseのURLを設定します。
        *   環境変数 `FIREBASE_DATABASE_URL` に、FirebaseプロジェクトのDatabase URL (例: `https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com`) を設定してください。

2.  **OpenAI API キーの設定**:
    *   環境変数 `OPENAI_API_KEY` に、OpenAIのAPIキーを設定してください。

3.  **実行環境を識別するための環境変数の設定**:
    *   環境変数 `APP_ENV` に `"scc"` を設定してください。

環境変数とFirebaseクレデンシャルをSecrets管理画面で設定する書式例は下記です。Firebaseクレデンシャルは末尾の入力が必要なようですのでご注意ください。

```toml
# .streamlit/secrets.toml ファイルの内容例 (Streamlit Community Cloudの場合)
FIREBASE_DATABASE_URL = "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
APP_ENV = "scc"

# FirebaseクレデンシャルはJSONの内容をそのまま登録 (キー名は'firebase'とする)
[firebase]
type = "service_account"
project_id = "<YOUR-PROJECT-ID>"
private_key_id = "<YOUR-PRIVATE-KEY-ID>"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-...@<YOUR-PROJECT-ID>.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-...%40<YOUR-PROJECT-ID>.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```
