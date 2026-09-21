import streamlit as st
import pandas as pd
import os

# CSVファイルの保存先
CSV_FILE = "data.csv"

# データの読み込み
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # 初期の列構成（「家」を追加）
        return pd.DataFrame(columns=["家", "名前", "型番", "メーカー", "説明書URL", "メモ"])

# データの保存
def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.title("🏠 型番・説明書管理アプリ（リンク対応版）")

df = load_data()

# サイドメニュー
menu = st.sidebar.selectbox("メニュー", ["新規登録", "データ一覧・検索"])

if menu == "新規登録":
    st.subheader("➕ 新規データ登録")
    
    with st.form("entry_form"):
        # 「家」の入力欄（よく使う家をサジェストできるようにテキスト入力）
        house = st.text_input("家（例: 花田家、実家 など）", value="花田家")
        name = st.text_input("名前（例: エアコン、テレビ など）")
        model = st.text_input("型番")
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
                    "型番": model,
                    "メーカー": maker,
                    "説明書URL": url,
                    "メモ": memo
                }])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"「{name}」を登録しました！")

elif menu == "データ一覧・検索":
    st.subheader("📋 登録されているデータの一覧・検索")
    
    if len(df) == 0:
        st.info("まだデータが登録されていません。「新規登録」から追加してください。")
    else:
        # --- 絞り込み検索エリア ---
        st.markdown("### 🔍 絞り込み検索")
        
        # 家の選択肢（「すべて」＋登録されている家の一覧）
        house_options = ["すべて"] + list(df["家"].dropna().unique())
        selected_house = st.selectbox("家で絞り込み", house_options)
        
        # キーワード検索
        keyword = st.text_input("キーワード検索（名前・型番・メーカー・メモから探す）", "")
        
        # 絞り込みの適用
        filtered_df = df.copy()
        
        # 家での絞り込み
        if selected_house != "すべて":
            filtered_df = filtered_df[filtered_df["家"] == selected_house]
            
        # キーワードでの絞り込み
        if keyword:
            # 大文字小文字を区別せず、各列からキーワードを探す
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(keyword, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]
            
        st.write(f"検索結果：**{len(filtered_df)}件** のデータが見つかりました")
        
        # 一覧をカード形式っぽく、または見やすく表示
        for idx, row in filtered_df.iterrows():
            with st.container(border=True):
                st.markdown(f"### 🏷️ {row['名前']} （家: **{row['家']}**）")
                st.write(f"**メーカー:** {row['maker'] if 'maker' in row else row['メーカー']} ／ **型番:** {row['型番']}")
                
                # 説明書URLがある場合は、ワンクリックで開けるボタンを表示
                url_val = str(row['説明書URL'])
                if url_val and url_val.startswith("http"):
                    st.link_button("📖 説明書を開く", url_val)
                elif url_val and url_val != "nan":
                    st.write(f"**説明書URL:** {url_val} (※ https:// から始まらないためリンクになりません)")
                
                if pd.notna(row['メモ']) and str(row['メモ']) != "":
                    st.write(f"**メモ:** {row['メモ']}")
                    
                # 削除ボタン
                if st.button("このデータを削除", key=f"del_{idx}"):
                    df = df.drop(idx).reset_index(drop=True)
                    save_data(df)
                    st.success("データを削除しました。画面を更新してください。")
                    st.rerun()