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
  # 初期データの列定義（設置場所と商品名を追加）
  return pd.DataFrame(
      columns=[
          "家",
          "設置場所",
          "商品名",
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
    room = st.text_input("設置場所（例: リビング、寝室、キッチン など）")
    product_name = st.text_input("商品名（例: エアコン、液晶テレビ など）")
    model_no = st.text_input("型番（例: RAS-2810D など）")
    serial_no = st.text_input("製品番号 / シリアル番号")
    year = st.text_input("製造年（例: 2023年製 など）")
    maker = st.text_input("メーカー")
    url = st.text_input("説明書URL（https://...から始まるリンク）")
    memo = st.text_area("メモ")

    submitted = st.form_submit_button("登録する")

    if submitted:
      if product_name == "":
        st.warning("「商品名」を入力してください。")
      else:
        new_data = pd.DataFrame([{
            "家": house,
            "設置場所": room,
            "商品名": product_name,
            "型番": model_no,
            "製品番号": serial_no,
            "製造年": year,
            "メーカー": maker,
            "説明書URL": url,
            "メモ": memo,
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        save_data(df)
        st.success(f"「{product_name}」を登録しました！")

elif menu == "データ一覧・検索":
  st.subheader("📋 登録されているデータの一覧・検索")

  if len(df) == 0:
    st.info("まだデータが登録されていません。「新規登録」から追加してください。")
  else:
    st.markdown("### 🔍 絞り込み検索")

    house_options = ["すべて"] + list(df["家"].dropna().unique())
    selected_house = st.selectbox("家で絞り込み", house_options)

    keyword = st.text_input(
        "キーワード検索（商品名・設置場所・型番・メーカーなどから探す）", ""
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

    updated_df = df.copy()

    for idx, row in filtered_df.iterrows():
      with st.container(border=True):
        # カードのタイトルに商品名と設置場所を表示
        loc_str = f"（設置場所: {row['設置場所']}）" if pd.notna(row['設置場所']) and row['設置場所'] != "" else ""
        st.markdown(f"### 🏷️ {row['商品名']} {loc_str}")

        st.write(
            f"**家:** {row.get('家', '')} ／ "
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
          updated_df = updated_df.drop(idx).reset_index(drop=True)
          save_data(updated_df)
          st.success("データを削除しました。")
          st.rerun()

    st.write("---")
    if st.button("💾 データを保存・更新する", type="primary"):
      save_data(updated_df)
      st.success("データを保存しました！")
      st.rerun()