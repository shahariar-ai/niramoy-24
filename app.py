import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env ফাইল থেকে API key লোড করা
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# পেজ সেটআপ
st.set_page_config(page_title="NIRAMOY-24", page_icon="🩺")
st.title("🩺 NIRAMOY-24")
st.caption("আপনার ২৪/৭ স্বাস্থ্য সহায়ক — এটি ডাক্তারের বিকল্প নয়")

# Gemini কানেক্ট করা
genai.configure(api_key=api_key)

# বটের ব্যক্তিত্ব ও নিয়ম ঠিক করে দেওয়া system prompt
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

# চ্যাট মডেল তৈরি করা (system prompt সহ)
if "chat" not in st.session_state:
    model = genai.GenerativeModel(
        "gemini-flash-latest",
        system_instruction=SYSTEM_PROMPT
    )
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []

# আগের সব মেসেজ দেখানো
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজারের নতুন ইনপুট নেওয়া
user_input = st.chat_input("আপনার স্বাস্থ্য বিষয়ক প্রশ্ন লিখুন...")

if user_input:
    # ইউজারের মেসেজ দেখানো ও সেভ করা
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Gemini থেকে উত্তর নেওয়া
    with st.chat_message("assistant"):
        with st.spinner("ভাবছি..."):
            response = st.session_state.chat.send_message(user_input)
            st.markdown(response.text)

    # বটের মেসেজ সেভ করা
    st.session_state.messages.append({"role": "assistant", "content": response.text})