import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
from models import Styles, Style, Example

def initialize_firebase():
    """Firebaseの初期化"""
    if not firebase_admin._apps:
        app_env = os.getenv('APP_ENV', 'local')

        if app_env == 'scc':
            # Streamlit Community Cloud環境
            cred = credentials.Certificate(dict(st.secrets["firebase"]))
        else:
            # ローカル環境
            cred = credentials.Certificate('firebase-credentials.json')

        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL')
        })

def load_styles() -> Styles:
    """文体データをFirebaseから読み込む"""
    try:
        ref = db.reference('/styles')
        data = ref.get()
        if not data:
            return []

        styles = []
        for style in data:
            examples = []
            for example in style.get('examples', []):
                examples.append(Example(
                    input=example.get('input', ''),
                    output=example.get('output', '')
                ))
            styles.append(Style(
                name=style.get('name', ''),
                examples=examples
            ))
        return styles
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return []

def save_styles(styles: Styles):
    """文体データをFirebaseに保存"""
    try:
        ref = db.reference('/styles')
        # 既存のデータを削除
        ref.delete()
        # 新しいデータを保存
        for i, style in enumerate(styles):
            style_ref = ref.child(str(i))
            style_ref.set({
                'name': style.name,
                'examples': {
                    str(j): {
                        'input': example.input,
                        'output': example.output
                    } for j, example in enumerate(style.examples)
                }
            })
    except Exception as e:
        st.error(f"データの保存に失敗しました: {str(e)}")
