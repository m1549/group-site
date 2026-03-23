import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes

# Firebase Setup
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

TOKEN = '8589258891:AAFFrOHKAhFeLMftuicBV5GudyLgqvvfsaQ'
WEB_APP_URL = 'https://supermony-site.vercel.app/'
BOT_USERNAME = 'supermony1_bot' # এখানে আপনার বোটের ইউজারনেম দিন (@ ছাড়া)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # রেফার আইডি চেক করা
    referrer_id = context.args[0] if context.args else None

    # Firestore থেকে ডাটা নেওয়া (এটি সিনক্রোনাস তাই সাবধানে ব্যবহার করুন)
    user_ref = db.collection('users').document(str(user.id))
    doc = user_ref.get()

    if not doc.exists:
        # নতুন ইউজার ডাটা
        user_data = {
            'username': user.username,
            'name': user.first_name,
            'referred_by': referrer_id,
            'refer_count': 0,
            'balance': 0
        }
        user_ref.set(user_data)

        # রেফারারকে আপডেট করা
        if referrer_id:
            try:
                ref_owner_ref = db.collection('users').document(str(referrer_id))
                if ref_owner_ref.get().exists:
                    ref_owner_ref.update({'refer_count': firestore.Increment(1)})
                    await context.bot.send_message(
                        chat_id=referrer_id, 
                        text=f"অভিনন্দন! {user.first_name} আপনার লিঙ্কে যোগ দিয়েছে।"
                    )
            except Exception as e:
                print(f"Referral update error: {e}")

    # সঠিক রেফার লিঙ্ক ফরম্যাট
    refer_link = f"https://t.me/{BOT_USERNAME}?start={user.id}"
    
    keyboard = [
        [InlineKeyboardButton("Open Trade Battle", web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("Refer Friends", switch_inline_query=f"Join this bot to earn: {refer_link}")]
    ]
    
    await update.message.reply_text(
        f"স্বাগতম {user.first_name}!\nআপনার রেফার লিঙ্ক: {refer_link}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

if __name__ == '__main__':
    print("Bot is starting...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()