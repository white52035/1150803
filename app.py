import streamlit as st
import random
import json
import os
import re
import io

# 🛡️ 嘗試匯入 gTTS (注意：模組名稱必須是小寫 gtts)
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

# 🚀 全域系統版本號 - 海洋風格版
APP_VERSION = "v2.2.0-Ocean (Build 20260803 - Ocean Breeze Edition)"

# ==========================================
# 🛡️ 防腐層：保留指定的原始結構與函數
# ==========================================
VOCABULARY = []
SENTENCES = []

def init_quiz(): 
    pass

def play_audio(): 
    pass

def show_learning_mode(): 
    pass

def show_quiz_mode(): 
    pass

def show_debug_info(): 
    pass

# 原始聽力題庫 (15題標準數據庫，完全保留，更新路徑為 audio/ 並改為 .m4a)
QUIZ_DATA = [
    {"id": 1, "audio_path": "audio/word_001.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["riyar", "'alo", "fanaw", "sa'owac"], "correct_text": "riyar"},
    {"id": 2, "audio_path": "audio/word_002.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["korkor", "rohayan", "romakat", "rotarot"], "correct_text": "romakat"},
    {"id": 3, "audio_path": "audio/word_003.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["hadhad", "hakhak", "hawan", "hafay"], "correct_text": "hafay"},
    {"id": 4, "audio_path": "audio/word_004.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["tefo'", "'okoy", "tafokod", "tafolod"], "correct_text": "tafokod"},
    {"id": 5, "audio_path": "audio/word_005.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["fakar", "tayhi", "pitaw", "tarakar"], "correct_text": "pitaw"},
    {"id": 6, "audio_path": "audio/word_006.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["sariri'", "riri'", "siri", "riyar"], "correct_text": "siri"},
    {"id": 7, "audio_path": "audio/word_007.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["koleto", "lokot", "kewaw", "kakorot"], "correct_text": "koleto"},
    {"id": 8, "audio_path": "audio/word_008.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["siwoy", "kodasing", "konga", "damay"], "correct_text": "konga"},
    {"id": 9, "audio_path": "audio/word_009.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["mali'", "tikami", "tilifi", "pawli"], "correct_text": "tilifi"},
    {"id": 10, "audio_path": "audio/word_010.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["picakay", "pitangtang", "picaliw", "pafeli'"], "correct_text": "picakay"},
    {"id": 11, "audio_path": "audio/word_011.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["'olaw", "'alo", "fao", "tao"], "correct_text": "tao"},
    {"id": 12, "audio_path": "audio/word_012.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["rorang", "kolong", "lotong", "ekong"], "correct_text": "lotong"},
    {"id": 13, "audio_path": "audio/word_013.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["Halitamako", "Haliradiw", "Haliepah", "Hali'ecaw"], "correct_text": "Haliepah"},
    {"id": 14, "audio_path": "audio/word_014.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["dafak", "a'ayad", "dadaya", "kamaya"], "correct_text": "dadaya"},
    {"id": 15, "audio_path": "audio/word_015.m4a", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["sioy", "simal", "sinafel", "simico"], "correct_text": "sinafel"}
]

# ==========================================
# 🎵 發音引擎：優先讀取實體錄音檔，找不到才用 TTS 備援
# ==========================================
def get_audio_filename(prefix):
    """根據題型與索引產生對應的錄音檔名"""
    try:
        parts = prefix.split("_")
        section = parts[0]
        idx = int(parts[-1]) + 1 
        
        # 統一去 audio/ 資料夾抓取 .m4a 檔案
        base_dir = "audio"
        filename = ""
        
        # 聽力測驗
        if "聽音選詞" in section:
            filename = f"word_{idx:03d}.m4a"
        elif "對話理解" in section:
            filename = f"dialog_{idx:03d}.m4a"
        
        # 口說測驗
        elif "段落朗讀" in section:
            filename = f"read_{idx:03d}.m4a"
        elif "情境問答" in section:
            filename = f"qa_q_{idx:03d}.m4a" # 預設播放題目
        elif "看圖表達" in section:
            filename = f"pic_a_{idx:03d}.m4a" # 預設播放解答
        
        # 閱讀測驗
        elif "詞彙語意" in section:
            filename = f"vocab_{idx:03d}.m4a"
        elif "語言結構" in section:
            filename = f"grammar_{idx:03d}.m4a"
            
        # 寫作測驗
        elif "句子聽寫" in section:
            filename = f"dict_{idx:03d}.m4a"
        elif "問答" == section:
            filename = f"write_qa_q_{idx:03d}.m4a" # 預設播放題目
        
        return os.path.join(base_dir, filename) if filename else None
    except:
        return None

def play_tts(text, prefix=None, is_ans=False):
    """
    發音邏輯：
    1. 若有傳入 prefix，先嘗試到 audio/ 目錄尋找對應的 .m4a 實體檔案
    2. 若找不到檔案，再退回使用 gTTS 動態發音 (印尼語備援)
    """
    audio_path = None
    if prefix:
        # 特殊處理：情境問答、看圖表達與問答的解答發音
        if is_ans and "情境問答" in prefix:
            idx = int(prefix.split('_')[-1]) + 1
            audio_path = os.path.join("audio", f"qa_a_{idx:03d}.m4a")
        elif is_ans and "看圖表達" in prefix:
            idx = int(prefix.split('_')[-1]) + 1
            audio_path = os.path.join("audio", f"pic_a_{idx:03d}.m4a")
        elif is_ans and prefix.startswith("問答"):
            idx = int(prefix.split('_')[-1]) + 1
            audio_path = os.path.join("audio", f"write_qa_a_{idx:03d}.m4a")
        else:
            audio_path = get_audio_filename(prefix)
            
    if audio_path and os.path.exists(audio_path):
        try:
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/m4a", autoplay=True)
            return
        except Exception as e:
            st.warning(f"⚠️ 讀取實體音檔失敗: {audio_path}，將使用系統模擬發音。（錯誤細節：{e}）")

    # ----- 退回 TTS 備援邏輯 -----
    if not HAS_GTTS:
        st.warning(f"⚠️ 找不到實體音檔且系統未成功載入 gTTS 套件，無法發音。請確認錄音檔是否已上傳。預期路徑: {audio_path}")
        return

    match = re.search(r'「(.*?)」', text)
    if match:
        target_text = match.group(1)
    else:
        target_text = re.sub(r'請問.*?中文意思是什麼|的阿美語是哪一個|聆聽音檔.*?|題目：|阿美語：|中文：.*', '', text)
        target_text = re.sub(r'[\u4e00-\u9fa5]', '', target_text)
        target_text = re.sub(r'^\d+[\.、]\s*', '', target_text)
    
    target_text = target_text.strip()
    if not target_text:
        target_text = text 
        
    try:
        tts = gTTS(text=target_text, lang='id')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
        if audio_path:
             st.info(f"💡 系統提示：目前使用 TTS 模擬發音。若要使用真實錄音，請上傳檔案至：`{audio_path}`")
    except Exception as e:
        st.error(f"⚠️ 語音生成失敗，請檢查網路連線。（錯誤細節：{e}）")

# ==========================================
# 🧠 動態解析引擎：跨行讀取與穩定分割版
# ==========================================
def load_question_bank():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cwd_dir = os.getcwd()

    db = {
        "聽音選詞": [], "對話理解": [], "段落朗讀": [], "情境問答": [],
        "看圖表達": [], "詞彙語意": [], "語言結構": [], "句子聽寫": [], "問答": []
    }
    
    scanned_files = []
    for d in [base_dir, cwd_dir]:
        if not os.path.exists(d): continue
        try:
            for f in os.listdir(d):
                if f.lower().endswith(".txt") and f.lower() not in ["app.txt", "requirements.txt", "提示詞.txt"]:
                    scanned_files.append(os.path.join(d, f))
        except:
            pass

    target_content = ""
    file_loaded = False
    encodings_to_try = ["utf-8", "utf-8-sig", "big5", "cp950"]

    for filepath in set(scanned_files):
        for enc in encodings_to_try:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    text_data = f.read()
                    if "聽音選詞" in text_data and "對話理解" in text_data:
                        target_content = text_data
                        file_loaded = True
                        break
            except:
                continue
        if file_loaded:
            break

    if not file_loaded:
        return db

    current_section = None
    current_question = []

    def save_question():
        if current_section and current_question:
            q_text = " ".join(current_question).strip()
            if re.match(r'^\d+[\.、]', q_text):
                db[current_section].append(q_text)
            current_question.clear()

    for line in target_content.split("\n"):
        line = line.strip()
        if not line:
            save_question()
            continue
            
        if "一、選擇題（聽音選詞）" in line: save_question(); current_section = "聽音選詞"
        elif "二、選擇題（對話理解）" in line: save_question(); current_section = "對話理解"
        elif "三、段落朗讀" in line: save_question(); current_section = "段落朗讀"
        elif "四、情境問答" in line: save_question(); current_section = "情境問答"
        elif "五、看圖表達" in line: save_question(); current_section = "看圖表達"
        elif "六、選擇題（詞彙語意）" in line: save_question(); current_section = "詞彙語意"
        elif "七、選擇題（語言結構）" in line: save_question(); current_section = "語言結構"
        elif "八、句子聽寫" in line: save_question(); current_section = "句子聽寫"
        elif "九、問答" in line: save_question(); current_section = "問答"
        
        elif re.match(r'^\d+[\.、]', line):
            save_question()
            current_question.append(line)
        else:
            if current_question:
                current_question.append(line)
                
    save_question()
            
    return db

# ==========================================
# 🎨 UI 渲染邏輯 (結合海洋風格與動態發音)
# ==========================================
def render_mcq(line, prefix):
    """渲染選擇題 (海洋風格動態語音按鈕與卡片)"""
    try:
        if "(A)" not in line:
            st.info(line)
            return

        parts = line.split("(A)", 1)
        q_part = parts[0].strip()
        rest = "(A)" + parts[1]
        
        opts_str = rest
        ans_str = ""
        ana_str = ""
        
        if "答案：" in rest:
            ans_parts = rest.split("答案：", 1)
            opts_str = ans_parts[0].strip()
            ans_ana = ans_parts[1]
            
            if "分析：" in ans_ana:
                final_parts = ans_ana.split("分析：", 1)
                ans_str = final_parts[0].strip("。 ")
                ana_str = final_parts[1].strip()
            else:
                ans_str = ans_ana.strip("。 ")

        is_listening = "聽音選詞" in prefix or "對話理解" in prefix
        col_q, col_btn = st.columns([4, 1.5])
        
        with col_q:
            if is_listening:
                if st.toggle("👁️ 顯示題目文字", key=f"t_show_q_{prefix}"):
                    st.markdown(f"**{q_part}**")
                else:
                    st.markdown("**[文字隱藏中，請點擊右方播放錄音]**")
            else:
                st.markdown(f"**{q_part}**")
                
        with col_btn:
            if st.button("🔊 播放發音", key=f"tts_btn_{prefix}"):
                play_tts(q_part, prefix=prefix)
        
        opts = []
        for tag in ["(A)", "(B)", "(C)", "(D)"]:
            if tag in opts_str:
                opt_text = opts_str.split(tag, 1)[1]
                for next_tag in ["(B)", "(C)", "(D)"]:
                    if next_tag > tag and next_tag in opt_text:
                        opt_text = opt_text.split(next_tag, 1)[0]
                opts.append(tag + " " + opt_text.strip())

        user_ans = st.radio("請選擇：", opts, index=None, key=prefix)
        
        if st.toggle("💡 顯示解答與分析", key=f"t_ans_{prefix}"):
            if ans_str:
                msg = f"**正確答案：** {ans_str}"
                if ana_str: msg += f"\n\n**分析：** {ana_str}"
                st.success(msg)
            else:
                st.warning("無標準答案。")
        elif user_ans and ans_str:
            if ans_str in user_ans:
                st.success(f"✅ 正確！" + (f"分析：{ana_str}" if ana_str else ""))
            else:
                st.error(f"❌ 錯誤。正確答案：{ans_str}。" + (f"分析：{ana_str}" if ana_str else ""))
    except Exception as e:
        st.info(line) 

def render_reading(line, prefix):
    """渲染段落朗讀"""
    try:
        q_part = line
        ch_part = ""
        if "(中文：" in line:
            parts = line.split("(中文：", 1)
            q_part = parts[0].strip()
            ch_part = parts[1].strip(")")
        elif "(中文大意：" in line:
            parts = line.split("(中文大意：", 1)
            q_part = parts[0].strip()
            ch_part = parts[1].strip(")")
        
        col_q, col_btn = st.columns([4, 1.5])
        with col_q:
            st.markdown(f"📖 **{q_part}**")
        with col_btn:
            if st.button("🔊 播放朗讀", key=f"tts_btn_{prefix}"):
                play_tts(q_part, prefix=prefix)
                
        if ch_part:
            if st.toggle("💡 顯示中文翻譯", key=f"t_{prefix}"):
                st.success(ch_part)
    except:
        st.info(line)

def render_qa(line, prefix):
    """渲染問答與情境問答"""
    try:
        text = line
        q_am = text
        ch_hint = ""
        ans = ""
        ana = ""
        
        if "中文：" in text:
            parts = text.split("中文：", 1)
            q_am = parts[0].strip()
            text = parts[1]
            
        if "參考回答：" in text:
            parts = text.split("參考回答：", 1)
            ch_hint = parts[0].strip()
            text = parts[1]
        elif "作答參考：" in text:
            parts = text.split("作答參考：", 1)
            ch_hint = parts[0].strip()
            text = parts[1]
            
        if "分析：" in text:
            parts = text.split("分析：", 1)
            ans = parts[0].strip()
            ana = parts[1].strip()
        else:
            if not ans: 
                ans = text.strip()
        
        q_am = q_am.replace("題目：", " 題目：")
        
        col_q, col_btn = st.columns([4, 1.5])
        with col_q:
            is_situational = "情境問答" in prefix
            if is_situational:
                if st.toggle("👁️ 顯示題目與提示", key=f"t_show_q_{prefix}"):
                    st.markdown(f"🗣️ **{q_am}**")
                    if ch_hint:
                        st.caption(f"中文提示：{ch_hint}")
                else:
                    st.markdown("**[提示文字隱藏中]**")
            else:
                st.markdown(f"🗣️ **{q_am}**")
                if ch_hint:
                    st.caption(f"中文提示：{ch_hint}")
                    
        with col_btn:
            if st.button("🔊 聽取問句", key=f"tts_btn_{prefix}"):
                play_tts(q_am, prefix=prefix)
            
        if ans or ana:
            if st.toggle("💡 顯示參考解答", key=f"t_{prefix}"):
                msg = ""
                if ans: msg += f"參考解答：{ans}"
                if ana: msg += f"\n\n分析：{ana}"
                st.success(msg)
                if ans:
                    if st.button("🔊 播放解答發音", key=f"tts_ans_{prefix}"):
                        play_tts(ans, prefix=prefix, is_ans=True)
    except:
        st.info(line)

def render_picture(line, prefix):
    """渲染看圖表達，並支援動態載入對應題號圖片"""
    try:
        text = line
        pic = text
        hint = ""
        ans = ""
        ana = ""
        
        if "圖片情境：" in text:
            parts = text.split("圖片情境：", 1)
            pic = parts[1]
            
        if "中文提示：" in pic:
            parts = pic.split("中文提示：", 1)
            pic = parts[0].strip()
            hint_part = parts[1]
            
            if "作答參考：" in hint_part:
                h_parts = hint_part.split("作答參考：", 1)
                hint = h_parts[0].strip()
                ans_part = h_parts[1]
                
                if "重點分析：" in ans_part:
                    a_parts = ans_part.split("重點分析：", 1)
                    ans = a_parts[0].strip()
                    ana = a_parts[1].strip()
                elif "重點：" in ans_part:
                    a_parts = ans_part.split("重點：", 1)
                    ans = a_parts[0].strip()
                    ana = a_parts[1].strip()
                else:
                    ans = ans_part.strip()
            else:
                hint = hint_part.strip()
        
        try:
            idx = int(prefix.split('_')[-1]) + 1
            img_path_jpg = f"assets/images/picture_{idx}.jpg"
            img_path_png = f"assets/images/picture_{idx}.png"
            
            if os.path.exists(img_path_jpg):
                st.image(img_path_jpg, use_container_width=True)
            elif os.path.exists(img_path_png):
                st.image(img_path_png, use_container_width=True)
            else:
                st.info(f"🖼️ 圖片佔位區：若要顯示圖片，請將圖片命名為 `picture_{idx}.jpg` 或 `.png`，並放置於 `assets/images/` 資料夾中。")
        except:
            pass

        st.markdown(f"🖼️ **圖片情境：** {pic}")
        
        if hint:
            st.caption(f"中文提示：{hint}")
            
        st.text_area("請在此作答：", key=f"input_{prefix}", label_visibility="collapsed", placeholder="可以在此輸入您的口說草稿...")
            
        if ans or ana:
            if st.toggle("💡 顯示作答參考", key=f"t_{prefix}"):
                msg = ""
                if ans: msg += f"作答參考：{ans}"
                if ana: msg += f"\n\n重點：{ana}"
                st.success(msg)
                
                if ans:
                    if st.button("🔊 發音作答參考", key=f"tts_ans_{prefix}"):
                        play_tts(ans, prefix=prefix, is_ans=True)
    except:
        st.info(line)

def render_dictation(line, prefix):
    """渲染句子聽寫"""
    try:
        text = line
        am = text
        ch = ""
        ana = ""
        
        if "中文：" in text:
            parts = text.split("中文：", 1)
            am = parts[0].replace("阿美語：", "").strip()
            text = parts[1]
            
            if "分析：" in text:
                sub_parts = text.split("分析：", 1)
                ch = sub_parts[0].strip()
                ana = sub_parts[1].strip()
            else:
                ch = text.strip()
        
        st.text_area("請在此作答：", key=f"input_{prefix}", label_visibility="collapsed", placeholder="請在此輸入您聽寫的句子...")
        
        col_q, col_btn = st.columns([4, 1.5])
        
        with col_q:
            if st.toggle("👁️ 顯示聽寫原文", key=f"t_show_dict_{prefix}"):
                st.markdown(f"✍️ **{am}**")
            else:
                st.markdown("**[原文隱藏中，請點擊右側按鈕進行聽寫測試]**")
                
        with col_btn:
            if st.button("🔊 播放聽寫語音", key=f"tts_btn_{prefix}"):
                play_tts(am, prefix=prefix)
            
        if ch or ana:
            if st.toggle("💡 顯示翻譯與分析", key=f"t_{prefix}"):
                msg = ""
                if ch: msg += f"中文：{ch}"
                if ana: msg += f"\n\n分析：{ana}"
                st.success(msg)
    except:
        st.info(line)

def render_section(section_name, db):
    """通用區塊渲染器"""
    questions = db.get(section_name, [])
    if not questions:
        st.warning(f"⚠️ 系統抓不到【{section_name}】的資料。")
        return

    for i, line in enumerate(questions):
        with st.container():
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            if "聽音選詞" in section_name or "對話理解" in section_name or section_name in ["詞彙語意", "語言結構"]:
                render_mcq(line, f"{section_name}_{i}")
            elif section_name == "段落朗讀":
                render_reading(line, f"{section_name}_{i}")
            elif section_name in ["情境問答", "問答"]:
                render_qa(line, f"{section_name}_{i}")
            elif section_name == "看圖表達":
                render_picture(line, f"{section_name}_{i}")
            elif section_name == "句子聽寫":
                render_dictation(line, f"{section_name}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚀 應用程式主邏輯 (Main)
# ==========================================
def main():
    st.set_page_config(page_title="阿美語中高級認證 - 海洋風學習平台", page_icon="🌊", layout="centered", initial_sidebar_state="collapsed")

    # 🌊 太平洋湛藍海洋風格 (Ocean Breeze Theme) CSS
    st.markdown("""
    <style>
    /* 全局背景色與深海漸層 */
    .stApp {
        background: linear-gradient(180deg, #eef7fa 0%, #e0f2fe 100%);
        color: #0f172a;
    }
    
    /* 標題樣式 */
    h1 {
        color: #0369a1 !important;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0, 119, 182, 0.15);
    }
    h2, h3 {
        color: #0284c7 !important;
    }
    
    /* 海洋風題庫卡片 */
    .quiz-card {
        background: #ffffff;
        padding: 24px;
        border-radius: 16px;
        border-left: 6px solid #0284c7;
        border-top: 1px solid #bae6fd;
        border-right: 1px solid #bae6fd;
        border-bottom: 1px solid #bae6fd;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.08), 0 8px 10px -6px rgba(2, 132, 199, 0.04);
        margin-top: 18px;
        margin-bottom: 25px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .quiz-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px -5px rgba(2, 132, 199, 0.15);
    }
    
    /* 按鈕樣式（海浪漸層） */
    .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.3);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        box-shadow: 0 6px 12px -2px rgba(2, 132, 199, 0.4);
    }
    
    /* 分隔線 */
    hr { 
        border-top: 2px dashed #7dd3fc; 
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌊 阿美語中高級認證 (Riyar Ocean Edition)")
    st.caption("🌊 「’Aray to riyar」—— 感受太平洋海風的阿美族語學習之旅")

    main_options = ["📋 認證考試說明", "🎧 聽力 (Pitengil)", "🗣️ 口說 (Pisowal)", "📖 閱讀 (Piasip)", "✍️ 寫作 (Pitilid)"]
    current_tab = st.segmented_control("主選單導覽", main_options, default=None, label_visibility="collapsed")

    if "previous_tab" not in st.session_state:
        st.session_state.previous_tab = None

    if st.session_state.previous_tab != current_tab:
        st.session_state.submitted = False
        st.session_state.audio_triggered = False
        if "writing_submitted" in st.session_state:
            st.session_state.writing_submitted = False
        st.session_state.previous_tab = current_tab

    db = load_question_bank()

    if current_tab == "📋 認證考試說明":
        st.subheader("📋 [認證考試說明](https://lokahsu.ilrdf.org.tw/web_lokahsu/Files/Guide/1_20251211_162558.pdf)")
        st.divider()
        st.info("🌊 歡迎來到海洋風格學習平台！請透過上方導覽列選擇您要進行的測驗項目。系統將優先從 `audio/` 資料夾載入您的真實阿美語錄音，若無音檔則會自動退回使用模擬發音。")

    elif current_tab == "🎧 聽力 (Pitengil)":
        st.subheader("🎧 聽力測驗 (Pitengil)")
        st.divider()
        listening_sub = st.radio("題型選擇：", ["選擇題-聽音選詞", "選擇題-對話理解"], horizontal=True)
        if listening_sub == "選擇題-聽音選詞":
            render_section("聽音選詞", db)
        elif listening_sub == "選擇題-對話理解":
            render_section("對話理解", db)

    elif current_tab == "🗣️ 口說 (Pisowal)":
        st.subheader("🗣️ 口說測驗 (Pisowal)")
        st.divider()
        speaking_sub = st.radio("題型選擇：", ["段落朗讀", "情境問答", "看圖表達"], horizontal=True)
        if speaking_sub == "段落朗讀":
            render_section("段落朗讀", db)
        elif speaking_sub == "情境問答":
            render_section("情境問答", db)
        elif speaking_sub == "看圖表達":
            render_section("看圖表達", db)

    elif current_tab == "📖 閱讀 (Piasip)":
        st.subheader("📖 閱讀測驗 (Piasip)")
        st.divider()
        reading_sub = st.radio("閱讀題型選擇：", ["選擇題-詞彙語意", "選擇題-語言結構"], horizontal=True)
        if reading_sub == "選擇題-詞彙語意":
            render_section("詞彙語意", db)
        elif reading_sub == "選擇題-語言結構":
            render_section("語言結構", db)

    elif current_tab == "✍️ 寫作 (Pitilid)":
        st.subheader("✍️ 寫作測驗 (Pitilid)")
        st.divider()
        writing_sub = st.radio("寫作題型選擇：", ["句子聽寫", "問答"], horizontal=True)
        if writing_sub == "句子聽寫":
            render_section("句子聽寫", db)
        elif writing_sub == "問答":
            render_section("問答", db)

    st.write("---")
    st.caption(f"🌊 © 2026 阿美語中高級認證 App ｜ 太平洋海洋風格版 ： **{APP_VERSION}** ")

if __name__ == "__main__":
    main()
