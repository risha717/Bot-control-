import os
import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler
)

# ===================== CONFIGURATION =====================
BOT_TOKEN = "8374737182:AAEpoD8dn_x4QPIKZO6zACbGfmCrBGx-ZxY"  # আপনার Main Promo Bot Token
MINI_APP_URL = "https://cinaflix-streaming.vercel.app/"
VIDEO_BOT_USERNAME = "Cinaflix_Streembot"  # আপনার Video Bot username
ADMIN_ID = 1858324638
DATABASE_FILE = "channels.json"

# ===================== LOGGING SETUP =====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== DATABASE FUNCTIONS =====================
def load_database():
    """Load database from JSON file"""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "force_join_channels": [],
            "promo_channels": [],
            "admin_id": ADMIN_ID,
            "promo_stats": {
                "total_users": [],
                "app_opens": 0,
                "referrals": 0
            }
        }

def save_database(db):
    """Save database to JSON file"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

# ===================== GLOBAL DATABASE =====================
db = load_database()

# ===================== START COMMAND =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - Beautiful welcome with Mini App"""
    user = update.effective_user
    
    # Add user to stats
    if user.id not in db['promo_stats']['total_users']:
        db['promo_stats']['total_users'].append(user.id)
        save_database(db)
    
    # Check if user needs to join channels
    not_joined = []
    for channel in db['force_join_channels']:
        try:
            member = await context.bot.get_chat_member(channel['id'], user.id)
            if member.status not in ['member', 'administrator', 'creator']:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    
    # If not joined, show force join
    if not_joined:
        await show_force_join(update, not_joined)
        return
    
    # Show main menu
    await show_main_menu(update, user)

async def show_force_join(update: Update, channels):
    """Show force join screen - Beautiful design matching Mini App"""
    keyboard = []
    
    # Add join buttons
    for ch in channels:
        keyboard.append([
            InlineKeyboardButton(
                f"📢 Join {ch['name']}", 
                url=f"https://t.me/{ch['username'].replace('@', '')}"
            )
        ])
    
    # Add verification button
    keyboard.append([
        InlineKeyboardButton(
            "✅ আমি সব চ্যানেল জয়েন করেছি",
            callback_data="verify_membership"
        )
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    channel_list = "\n".join([f"✦ {ch['name']}" for ch in channels])
    
    message = f"""
🎬 **Welcome to CINEFLIX!**

Premium Content এর জগতে স্বাগতম! 🌟

━━━━━━━━━━━━━━━━━━━━━

🔒 **Access Required**

নিচের চ্যানেলগুলো join করুন:

{channel_list}

━━━━━━━━━━━━━━━━━━━━━

**🎯 কেন Join করবেন?**
✦ Premium HD Videos
✦ Latest Updates
✦ Exclusive Content
✦ Fast Downloads

Join করার পর instant access! 🚀
    """
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_main_menu(update: Update, user):
    """Show main menu - Beautiful UI matching Mini App theme"""
    keyboard = [
        [InlineKeyboardButton(
            "🎬 Open CINEFLIX App", 
            web_app=WebAppInfo(url=MINI_APP_URL)
        )],
        [
            InlineKeyboardButton("📢 Channel", callback_data="channels"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("⭐ Rate Us", callback_data="rate"),
            InlineKeyboardButton("📤 Share", callback_data="share")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🎬 **CINEFLIX - Your Entertainment Hub**

Hey **{user.first_name}**! 👋

আপনার সব পছন্দের Movies, Series আর Exclusive Content এক জায়গায়!

━━━━━━━━━━━━━━━━━━━━━

**✨ Features:**
🎯 HD Quality Videos
🚀 Fast Streaming
📱 Mobile Optimized
🔄 Regular Updates

━━━━━━━━━━━━━━━━━━━━━

**🎮 Quick Start:**
নিচে "Open CINEFLIX App" ক্লিক করুন
এবং unlimited entertainment শুরু করুন!

Happy Watching! 🍿✨
    """
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ===================== CALLBACK HANDLERS =====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user = update.effective_user
    
    if data == "verify_membership":
        # Re-check membership
        not_joined = []
        for channel in db['force_join_channels']:
            try:
                member = await context.bot.get_chat_member(channel['id'], user.id)
                if member.status not in ['member', 'administrator', 'creator']:
                    not_joined.append(channel)
            except:
                not_joined.append(channel)
        
        if not_joined:
            channel_names = ", ".join([ch['name'] for ch in not_joined])
            await query.answer(
                f"❌ আপনি এখনো এই চ্যানেলগুলো join করেননি: {channel_names}",
                show_alert=True
            )
        else:
            await query.answer("✅ Verified! Welcome to CINEFLIX!", show_alert=True)
            # Delete old message and show main menu
            await query.message.delete()
            update.message = query.message
            await show_main_menu(update, user)
    
    elif data == "help":
        help_text = """
🎬 **CINEFLIX Help Guide**

**🚀 কিভাবে ব্যবহার করবেন:**

**Step 1:** "Open CINEFLIX App" ক্লিক করুন
**Step 2:** ভিডিও browse করুন
**Step 3:** পছন্দের ভিডিও select করুন
**Step 4:** "Watch Now" ক্লিক করুন
**Step 5:** ভিডিও পাবেন!

━━━━━━━━━━━━━━━━━━━━━

**❓ সমস্যা সমাধান:**

**Q: App load হচ্ছে না?**
A: Internet connection check করুন

**Q: Video আসছে না?**
A: সব required channels join করেছেন কিনা check করুন

**Q: অন্য সমস্যা?**
A: Admin এর সাথে যোগাযোগ করুন

━━━━━━━━━━━━━━━━━━━━━

**🎯 Tips:**
✦ নিয়মিত আমাদের চ্যানেল check করুন
✦ নতুন আপডেটের জন্য notifications on রাখুন
✦ বন্ধুদের সাথে share করুন!

Enjoy CINEFLIX! 🍿
        """
        await query.message.reply_text(help_text, parse_mode='Markdown')
    
    elif data == "channels":
        if not db['force_join_channels']:
            await query.answer("No channels added yet!", show_alert=True)
            return
        
        keyboard = []
        for ch in db['force_join_channels']:
            keyboard.append([
                InlineKeyboardButton(
                    f"📢 {ch['name']}", 
                    url=f"https://t.me/{ch['username'].replace('@', '')}"
                )
            ])
        
        channels_msg = "📢 **Our Channels:**\n\nJoin করে latest updates পান!\n\n"
        
        await query.message.reply_text(
            channels_msg,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "rate":
        rate_msg = """
⭐ **Rate CINEFLIX**

আপনার experience কেমন ছিল?

আমাদের improve করতে সাহায্য করুন!
Admin কে feedback পাঠান।

ধন্যবাদ! ❤️
        """
        await query.message.reply_text(rate_msg, parse_mode='Markdown')
    
    elif data == "share":
        share_text = f"""
📤 **Share CINEFLIX**

বন্ধুদের সাথে share করুন:

🔗 Bot Link:
`https://t.me/{context.bot.username}`

💬 Share Message:
"🎬 CINEFLIX দেখেছ? সব movies আর series এক জায়গায়! দারুণ app! তুমিও try করো!"

আপনার share করার জন্য ধন্যবাদ! 🙏
        """
        
        keyboard = [
            [InlineKeyboardButton(
                "📤 Share Now",
                url=f"https://t.me/share/url?url=https://t.me/{context.bot.username}&text=Check out CINEFLIX! 🎬"
            )]
        ]
        
        await query.message.reply_text(
            share_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

# ===================== ADMIN COMMANDS =====================
async def admin_promo_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel for promo bot"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Admin only!")
        return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Statistics", callback_data="promo_stats"),
            InlineKeyboardButton("📢 Broadcast", callback_data="promo_broadcast")
        ],
        [
            InlineKeyboardButton("📋 Channels", callback_data="promo_channels"),
            InlineKeyboardButton("👥 Users", callback_data="promo_users")
        ]
    ]
    
    stats_text = f"""
🎮 **CINEFLIX Promo Bot Admin Panel**

Welcome Boss! 👑

**Quick Stats:**
👥 Total Users: **{len(db['promo_stats']['total_users'])}**
🎬 App Opens: **{db['promo_stats']['app_opens']}**
📤 Referrals: **{db['promo_stats']['referrals']}**

**Status:** ✅ Active

What would you like to do?
    """
    
    await update.message.reply_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def broadcast_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast to all promo bot users"""
    if update.effective_user.id != ADMIN_ID:
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: `/broadcast Your message`",
            parse_mode='Markdown'
        )
        return
    
    message = ' '.join(context.args)
    success = 0
    failed = 0
    
    status = await update.message.reply_text("📤 Broadcasting...")
    
    for user_id in db['promo_stats']['total_users']:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 **CINEFLIX Announcement:**\n\n{message}",
                parse_mode='Markdown'
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed to {user_id}: {e}")
    
    await status.edit_text(
        f"✅ **Broadcast Complete!**\n\n"
        f"✔️ Sent: **{success}**\n"
        f"❌ Failed: **{failed}**",
        parse_mode='Markdown'
    )

# ===================== UTILITY COMMANDS =====================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🎬 **CINEFLIX Bot Help**

**Commands:**
/start - Start bot
/help - Show help

**Quick Guide:**
1. Click "Open CINEFLIX App"
2. Browse videos
3. Click "Watch Now"
4. Enjoy!

Need support? Contact admin!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ===================== ERROR HANDLER =====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Error handler"""
    logger.error(f"Update {update} caused error {context.error}")

# ===================== MAIN FUNCTION =====================
def main():
    """Start the promo bot"""
    logger.info("🚀 Starting CINEFLIX Promo Bot...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # User Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Admin Commands
    application.add_handler(CommandHandler("admin", admin_promo_panel))
    application.add_handler(CommandHandler("broadcast", broadcast_promo))
    
    # Callback Handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Error Handler
    application.add_error_handler(error_handler)
    
    logger.info("✅ CINEFLIX Promo Bot is running!")
    logger.info(f"🌐 Mini App: {MINI_APP_URL}")
    logger.info(f"👑 Admin: {ADMIN_ID}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
  
