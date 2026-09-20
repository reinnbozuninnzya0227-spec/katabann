import streamlit as st
import pandas as pd
import os

# データ保存用のCSVファイル名
DATA_FILE = "model_manual_data.csv"

# データの読み込み関数
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # 初期データがない場合は空のDataFrameを作成
        return pd.DataFrame(columns=["型番", "製品番号", "説明書URL"])

# データの保存関数
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

st.title("型番・説明書 管理アプリ")

# メニューの選択
menu = st.sidebar.selectbox("メニュー", ["検索・一覧", "新規登録", "登録情報の編集・削除"])

df = load_data()

if menu == "検索・一覧":
    st.header("🔍 型番・説明書 検索")
    
    search_query = st.text_input("キーワード検索（型番や製品番号の一部を入力）", "")
    
    if not df.empty:
        if search_query:
            # 大文字小文字を区別せず、型番または製品番号にヒットするものを抽出
            filtered_df = df[
                df["型番"].astype(str).str.contains(search_query, case=False, na=False) |
                df["製品番号"].astype(str).str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_df = df
        
        st.write(f"検索結果: {len(filtered_df)} 件")
        
        for index, row in filtered_df.iterrows():
            with st.expander(f"型番: {row['型番']} (製品番号: {row['製品番号']})"):
                st.write(f"**製品番号:** {row['製品番号']}")
                url = row['説明書URL']
                if pd.notna(url) and str(url).startswith("http"):
                    st.markdown(f"**説明書リンク:** [{url}]({url})")
                else:
                    st.write(f"**説明書URL:** {url}")
    else:
        st.info("登録されているデータがまだありません。「新規登録」から追加してください。")

elif menu == "新規登録":
    st.header("➕ 新規データ登録")
    
    with st.form("add_form"):
        kataban = st.text_input("型番")
        seihin_no = st.text_input("製品番号")
        url = st.text_input("説明書URL")
        
        submitted = st.form_submit_button("登録する")
        
        if submitted:
            if kataban:
                new_data = pd.DataFrame([[kataban, seihin_no, url]], columns=["型番", "製品番号", "説明書URL"])
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"型番「{kataban}」を登録しました！")
            else:
                st.error("「型番」は必須入力です。")

elif menu == "登録情報の編集・削除":
    st.header("ペン 登録情報の編集・削除")
    
    if not df.empty:
        selected_index = st.selectbox("編集・削除するデータを選択", df.index, format_func=lambda x: f"型番: {df.loc[x, '型番']} (製品番号: {df.loc[x, '製品番号']})")
        
        if selected_index is not None:
            current_kataban = df.loc[selected_index, "型番"]
            current_seihin = df.loc[selected_index, "製品番号"]
            current_url = df.loc[selected_index, "説明書URL"]
            
            with st.form("edit_form"):
                new_kataban = st.text_input("型番", value=str(current_kataban))
                new_seihin = st.text_input("製品番号", value=str(current_seihin))
                new_url = st.text_input("説明書URL", value=str(current_url))
                
                col1, col2 = st.columns(2)
                with col1:
                    update_btn = st.form_submit_button("更新する")
                with col2:
                    delete_btn = st.form_submit_button("削除する")
                
                if update_btn:
                    df.loc[selected_index, "型番"] = new_kataban
                    df.loc[selected_index, "製品番号"] = new_seihin
                    df.loc[selected_index, "説明書URL"] = new_url
                    save_data(df)
                    st.success("データを更新しました！")
                    st.rerun()
                
                if delete_btn:
                    df = df.drop(selected_index).reset_index(drop=True)
                    save_data(df)
                    st.success("データを削除しました！")
                    st.rerun()
    else:
        st.info("編集・削除できるデータがありません。")