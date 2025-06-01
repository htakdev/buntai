import os
from dataclasses import asdict
from typing import List

import firebase_admin
import streamlit as st
from firebase_admin import credentials, db

from models import Example, Style


def initialize_firebase():
    """Firebaseの初期化"""
    if firebase_admin._apps:
        return

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

def load_styles() -> List[Style]:
    """文体データをFirebaseから読み込む"""
    try:
        ref = db.reference('/styles')
        raw_styles_data = ref.get()
        if not raw_styles_data:
            return []

        styles = []
        for style in raw_styles_data:
            examples = [Example(**example) for example in style.get('examples', [])]
            styles.append(Style(
                name=style.get('name', ''),
                examples=examples
            ))
        return styles
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {str(e)}")
        return []

def save_styles(styles: List[Style]):
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
                    str(j): asdict(example) for j, example in enumerate(style.examples)
                }
            })
    except Exception as e:
        st.error(f"データの保存に失敗しました: {str(e)}")
