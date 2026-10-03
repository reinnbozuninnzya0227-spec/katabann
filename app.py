import os
import pandas as pd
import streamlit as st

# CSVファイルの保存名
CSV_FILE = "katabann_data.csv"

st.title("🏠 型番・説明書管理アプリ（CSV・GitHub保存版）")


# データの読み込み関数（安全版）
def load_data():
  if os.path.exists(CSV_FILE):
    try:
      df = pd.read_csv(CSV_FILE)
      if not df.empty:
        return df
    except Exception:
      pass
  # 初期データの列定義
  return pd.DataFrame(
      columns=[
          "家",
          "名前",
          "型番",
          "製品番号",
          "製造年",
          "メーカー",
          "説明書URL",
          "メモ",
      ]
  )


# データの保存関数
def save_data(df):
  df.to_csv(CSV_FILE, index=False)


df = load_data()

# サイドメニュー
menu = st.sidebar.selectbox("メニュー", ["新規登録", "データ一覧・検索"])

if menu == "新規登録":
  st.subheader("➕ 新規データ登録")

  with st.form("entry_form"):
    house = st.text_input("家（例: 自宅、実家 など）", value="自宅")
    name = st.text_input("名前（例: エアコン、テレビ など）")
    model_no = st.text_input("型番（例: RAS-2810D など）")
    serial_no = st.text_input("製品番号 / シリアル番号")
    year = st.text_input("製造年（例: 2023年製 など）")
    maker = st.text_input("メーカー")
    url = st.text_input("説明書URL（https://...から始まるリンク）")
    memo = st.text_area("メモ")

    submitted = st.form_submit_button("登録する")

    if submitted:
      if name == "":
        st.warning("「名前」を入力してください。")
      else:
        new_data = pd.DataFrame([{
            "家": house,
            "名前": name,
            "型番": model_no,
            "製品番号": serial_no,
            "製造年": year,
            "メーカー": maker,
            "説明書URL": url,
            "メモ": memo,
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success(f"「{name}」を登録しました！")

elif menu == "データ一覧・検索":
  st.subheader("📋 登録されているデータの確認・編集・保存")

  if len(df) == 0:
    st.info("まだデータが登録されていません。「新規登録」から追加してください。")
  else:
    st.write(
        "下の表で直接データを書き換えて、**「変更を保存する」ボタン**を押すとセーブされます。"
    )

    # 表形式で直接編集できるようにする（ここでデータの修正が可能）
    edited_df = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="data_table_editor"
    )

    # 🌟 待望のセーブボタン！
    if st.button("💾 変更を保存する", type="primary"):
      save_data(edited_df)
      st.success("変更を保存しました！")
      st.rerun()