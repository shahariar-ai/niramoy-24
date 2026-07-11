import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# .env ফাইল থেকে API key লোড করা
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# পেজ সেটআপ
st.set_page_config(page_title="NIRAMOY-24", page_icon="🩺")

# ==============================
# কাস্টম ডিজাইন (CSS + হেডার)
# ==============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Hind Siliguri', sans-serif;
}

.niramoy-header {
    background: linear-gradient(135deg, #0E5F56, #0A3F3B);
    padding: 24px 20px;
    border-radius: 16px;
    margin-bottom: 8px;
}
.niramoy-header h1 {
    color: #F2FBF9 !important;
    margin: 0;
    font-size: 28px;
}
.niramoy-header p {
    color: #8FF0D6;
    margin: 4px 0 0 0;
    font-size: 14px;
}

.pulse-divider {
    height: 3px;
    background: linear-gradient(90deg, #4FD9B3, #0E9E82, #4FD9B3);
    border-radius: 3px;
    margin: 20px 0;
    opacity: 0.6;
}

[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 4px 8px;
}

.stButton button {
    border-radius: 10px;
    font-weight: 600;
}

[data-testid="stFileUploader"] {
    border-radius: 12px;
    border: 2px dashed #0E9E82;
    padding: 10px;
}
</style>

<div class="niramoy-header">
    <h1>🩺 NIRAMOY-24</h1>
    <p>আপনার ২৪/৭ স্বাস্থ্য সহায়ক — এটি ডাক্তারের বিকল্প নয়</p>
</div>
""", unsafe_allow_html=True)

# Gemini কানেক্ট করা
genai.configure(api_key=api_key)

# ==============================
# চ্যাটের জন্য system prompt
# ==============================
SYSTEM_PROMPT = """
তুমি NIRAMOY-24, একটি বাংলা ভাষার স্বাস্থ্য বিষয়ক সহায়ক চ্যাটবট। 
তোমার কাজ ও নিয়মাবলী:

1. সবসময় বাংলায় উত্তর দেবে, সহজ ভাষায় (মেডিকেল জার্গন এড়িয়ে)।

2. কোনো লক্ষণ/সমস্যা নিয়ে প্রশ্ন এলে এই কাঠামো অনুসরণ করবে:
   - সম্ভাব্য কারণসমূহ (তালিকা আকারে, "হতে পারে" ভাষায় — নিশ্চিত ভাষায় না)
   - এখন যা করা যায় (সাধারণ self-care পরামর্শ)
   - 🚩 কখন সাথে সাথে ডাক্তার/হাসপাতালে যাবেন (red flag লক্ষণ)

3. কখনো নির্দিষ্ট রোগ নির্ণয় (diagnosis) করবে না। কখনো বলবে না "আপনার এই রোগ হয়েছে"।

4. কখনো ওষুধের নাম, dosage, বা কোনো medication সুপারিশ করবে না।

5. জরুরি উপসর্গের ক্ষেত্রে (বুকে ব্যথা, শ্বাসকষ্ট, প্রচণ্ড রক্তক্ষরণ, 
   জ্ঞান হারানো, স্ট্রোকের লক্ষণ, আত্মহত্যার চিন্তা ইত্যাদি) — অন্য কিছু আলোচনা না করে 
   সাথে সাথে স্পষ্টভাবে বলবে "এখনই হাসপাতালে যান বা জরুরি সেবায় (৯৯৯) কল করুন"।

6. প্রতিটি উত্তরের শেষে মনে করিয়ে দেবে যে এটি ডাক্তারের বিকল্প নয়।

7. তুমি বন্ধুত্বপূর্ণ, সহানুভূতিশীল, কিন্তু পেশাদার থাকবে।
"""

# প্রেসক্রিপশন পড়ার জন্য আলাদা, কড়াকড়ি নিয়মের prompt
PRESCRIPTION_PROMPT = """
তুমি একজন সহায়ক যে প্রেসক্রিপশনের ছবি পড়ে সহজ বাংলায় ব্যাখ্যা করো।

কড়াকড়ি নিয়ম:
1. ছবিতে যা লেখা আছে শুধু তাই পরিষ্কার করে বাংলায় লিখবে — ওষুধের নাম, 
   dosage/মাত্রা, কতদিন খেতে হবে, কখন খেতে হবে (যদি লেখা থাকে)।
2. একটা তালিকা আকারে প্রতিটা ওষুধ আলাদা করে দেখাবে।
3. তুমি নিজে থেকে কোনো মন্তব্য করবে না যে এই ওষুধ ঠিক আছে কিনা, 
   কোনো পরামর্শ দেবে না, কোনো বিকল্প সাজেস্ট করবে না।
4. যদি কোনো অংশ অস্পষ্ট/পড়া না যায়, স্পষ্টভাবে বলবে "এই অংশটি পড়া যাচ্ছে না, 
   দয়া করে ফার্মাসিস্ট বা ডাক্তারের সাথে যাচাই করুন"।
5. শেষে অবশ্যই লিখবে: "⚠️ এটি শুধু প্রেসক্রিপশন পড়ার সহায়তা। ওষুধ খাওয়ার আগে 
   ডাক্তার বা ফার্মাসিস্টের সাথে নিশ্চিত হয়ে নিন।"
"""

# ==============================
# সেকশন ১: প্রেসক্রিপশন আপলোড
# ==============================
st.subheader("📄 প্রেসক্রিপশন পড়ুন")

uploaded_file = st.file_uploader(
    "প্রেসক্রিপশনের ছবি আপলোড করুন",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="আপলোড করা প্রেসক্রিপশন", width=300)

    if st.button("প্রেসক্রিপশন পড়ে দেখাও"):
        with st.spinner("প্রেসক্রিপশন পড়া হচ্ছে..."):
            vision_model = genai.GenerativeModel("gemini-flash-latest")
            response = vision_model.generate_content([PRESCRIPTION_PROMPT, image])
            st.markdown("### 📋 প্রেসক্রিপশনে যা লেখা আছে:")
            st.markdown(response.text)

st.markdown('<div class="pulse-divider"></div>', unsafe_allow_html=True)

# ==============================
# সেকশন ২: চ্যাট
# ==============================
st.subheader("💬 স্বাস্থ্য বিষয়ক প্রশ্ন করুন")

if "chat" not in st.session_state:
    model = genai.GenerativeModel(
        "gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("আপনার স্বাস্থ্য বিষয়ক প্রশ্ন লিখুন...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("ভাবছি..."):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)

    st.session_state.messages.append({"role": "assistant", "content": response.text})