import os
import subprocess
import pandas as pd
import streamlit as st

# CSVファイルの保存名
CSV_FILE = "katabann_data.csv"

st.title("型番管理アプリ（GitHub自動保存版）")

# CSVの読み込み
if os.path.exists(CSV_FILE):
  df = pd.read_csv(CSV_FILE)
else:
  df = pd.DataFrame(columns=["型番", "品名", "数量"])

# データの編集画面
edited_df = st.data_editor(df, num_rows="dynamic")

if st.button("変更を保存する"):
  # ローカルのCSVを更新
  edited_df.to_csv(CSV_FILE, index=False)
  st.success("CSVファイルを更新しました！")