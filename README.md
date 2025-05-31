# 文体さん

## 概要
「文体さん」は、入力された文章を指定した文体に変換することができるWebアプリケーションです。独自の文体を登録・管理し、様々なスタイルの文章生成を試すことができます。

## 機能
- 既存の文体を選択して文章を変換
- 新しい文体を登録
- 登録済みの文体の名称変更
- 登録済みの文体の削除
- 文体ごとに変換の例文を登録・編集・削除

## デプロイ先
このアプリケーションは、以下のURLで利用可能です。

[https://buntai.streamlit.app/](https://buntai.streamlit.app/)

## 使い方
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

## 開発者向け情報

ローカル環境で開発を行う場合、およびStreamlit Community Cloudへデプロイする場合は、以下の設定が必要です。

### 環境変数の設定

アプリケーションの実行には、以下の環境変数およびクレデンシャルが必要です。

1.  **Firebase Realtime Database の設定**:
    *   **クレデンシャル**: Firebaseプロジェクトのサービスアカウントキーが必要です。
        *   ローカル開発の場合: FirebaseからダウンロードしたサービスアカウントキーのJSONファイルをリポジトリのルートディレクトリに `firebase-credentials.json` とリネームして配置してください。**このファイルはGitHubなどにアップロードしないよう注意してください。**
        *   Streamlit Community Cloudの場合: Streamlit Secrets を使用します。`st.secrets["firebase"]` としてアクセスできるよう、Streamlit Community CloudのSecrets管理画面でサービスアカウントキーの内容を登録してください。形式についてはStreamlitのドキュメントを参照してください。
    *   **Database URL**: Firebase Realtime DatabaseのURLを設定します。
        *   環境変数 `FIREBASE_DATABASE_URL` に、FirebaseプロジェクトのDatabase URL (例: `https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com`) を設定してください。

2.  **OpenAI API キーの設定**:
    *   環境変数 `OPENAI_API_KEY` に、OpenAIのAPIキーを設定してください。LangChainがこの環境変数から自動的にAPIキーを読み込みます。

3.  **実行環境を識別するための環境変数の設定**:
    *   環境変数 `APP_ENV` に、Streamlit Community Cloudであれば`"scc"`、ローカル環境であれば`"local"`を設定してください。

#### `.env` ファイルの使用 (ローカル開発)

ローカル開発時には、プロジェクトのルートディレクトリに `.env` ファイルを作成し、以下の形式で環境変数を記述するのが便利です。**このファイルはGitHubなどにアップロードしないよう注意してください。**

```env
FIREBASE_DATABASE_URL=https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
APP_ENV=local
```

`firebase-credentials.json` については、リポジトリのルート階層にファイル自体を配置してください。

#### Streamlit Community Cloud Secrets の使用 (デプロイ)

Streamlit Community Cloudにデプロイする場合、環境変数とFirebaseクレデンシャルはSecrets管理画面で設定します。

```toml
# .streamlit/secrets.toml ファイルの内容例 (Streamlit Community Cloudの場合)
# FIREBASE_DATABASE_URLは直接Secretsに登録
FIREBASE_DATABASE_URL = "https://YOUR-PROJECT-ID-default-rtdb.firebaseio.com"

# OpenAI API KeyもSecretsに登録
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# FirebaseクレデンシャルはJSONの内容をそのまま登録 (キー名は'firebase'とする)
[firebase]
type = "service_account"
project_id = "YOUR-PROJECT-ID"
private_key_id = "YOUR-PRIVATE-KEY-ID"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-...@YOUR-PROJECT-ID.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-...%40YOUR-PROJECT-ID.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
```

### セットアップ手順 (ローカル開発)

1.  リポジトリをクローンします。
    ```bash
    git clone https://github.com/htakdev/buntai.git
    cd buntai
    ```
2.  必要なPythonライブラリをインストールします。
    ```bash
    pip install -r requirements.dev.txt
    ```
3.  上記の「環境変数の設定」を参考に、必要な環境変数またはSecretsを設定します。
4.  Streamlitアプリケーションを実行します。
    ```bash
    streamlit run app.py
    ```
