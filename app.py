import os
import pandas as pd
import streamlit as st

# CSVファイルの保存名
CSV_FILE = "katabann_data.csv"

st.title("🏠 型番・説明書管理アプリ（CSV・GitHub保存版）")


# データの読み込み関数
def load_data():
  if os.path.exists(CSV_FILE):
    try:
      return pd.read_csv(CSV_FILE)
    except Exception:
      pass
  # 「型番」と「製品番号」を分けた初期の表
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
  st.subheader("📋 登録されているデータの一覧・検索")

  if len(df) == 0:
    st.info("まだデータが登録されていません。「新規登録」から追加してください。")
  else:
    st.markdown("### 🔍 絞り込み検索")

    house_options = ["すべて"] + list(df["家"].dropna().unique())
    selected_house = st.selectbox("家で絞り込み", house_options)

    keyword = st.text_input(
        "キーワード検索（名前・型番・製品番号・メーカーなどから探す）", ""
    )

    filtered_df = df.copy()

    if selected_house != "すべて":
      filtered_df = filtered_df[filtered_df["家"] == selected_house]

    if keyword:
      mask = (
          filtered_df.astype(str)
          .apply(lambda x: x.str.contains(keyword, case=False, na=False))
          .any(axis=1)
      )
      filtered_df = filtered_df[mask]

    st.write(f"検索結果：**{len(filtered_df)}件** のデータが見つかりました")

    for idx, row in filtered_df.iterrows():
      with st.container(border=True):
        st.markdown(f"### 🏷️ {row['名前']} （家: **{row['家']}**）")

        # メーカー、型番、製品番号、製造年をわかりやすく整理して表示
        st.write(
            f"**メーカー:** {row.get('メーカー', '')} ／ "
            f"**型番:** {row.get('型番', '')} ／ "
            f"**製品番号:** {row.get('製品番号', '')} ／ "
            f"**製造年:** {row.get('製造年', '')}"
        )

        url_val = str(row["説明書URL"])
        if url_val and url_val.startswith("http"):
          st.link_button("📖 説明書を開く", url_val)
        elif url_val and url_val != "nan":
          st.write(f"**説明書URL:** {url_val}")

        if pd.notna(row["メモ"]) and str(row["メモ"]) != "":
          st.write(f"**メモ:** {row['メモ']}")

        if st.button("このデータを削除", key=f"del_{idx}"):
          df = df.drop(idx).reset_index(drop=True)
          save_data(df)
          st.success("データを削除しました。")
          st.rerun()