"""
Command and message handlers for the Telegram bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

# Import Pumen Agent core components
from providers import UniversalProvider
from tools import SkillRegistry, DecisionEngine

# Global instances for the telegram bot
# Note: In a robust multi-user bot, these should be managed per user/chat session.
try:
    from cli.chat import CURRENT_PROVIDER, CURRENT_MODEL
    
    # Fallback to gemini if not configured
    provider = CURRENT_PROVIDER or "gemini"
    model = CURRENT_MODEL or "gemini-2.5-flash"
    
    llm_provider = UniversalProvider(provider_name=provider, model_name=model)
    registry = SkillRegistry()
    decision_engine = DecisionEngine(registry, llm_provider=llm_provider)
except Exception as e:
    logging.error(f"Failed to initialize Pumen Engine: {e}")
    llm_provider = None
    decision_engine = None


async def handle_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command from a Telegram user.

    Args:
        update (Update): The incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): The context object provided by the handler.

    Returns:
        None
    """
    if update.message:
        await update.message.reply_text("Xin chào! Tôi là Pumen Agent. Bạn cần giúp gì?")


from telegram import InlineKeyboardButton, InlineKeyboardMarkup

async def handle_provider_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global llm_provider
    if not update.message: return
    
    from providers import SUPPORTED_PROVIDERS
    if not context.args:
        keyboard = [
            [InlineKeyboardButton(p.capitalize(), callback_data=f"provider_{p}")]
            for p in SUPPORTED_PROVIDERS.keys()
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Vui lòng chọn nhà cung cấp:", reply_markup=reply_markup)
        return
        
    new_provider = context.args[0].lower()
    if new_provider not in SUPPORTED_PROVIDERS:
        await update.message.reply_text(f"❌ Nhà cung cấp {new_provider} không được hỗ trợ.\nHỗ trợ: {', '.join(SUPPORTED_PROVIDERS.keys())}")
        return
        
    try:
        from cli.chat import save_user_config
        from providers import get_available_models
        
        models = get_available_models(new_provider)
        new_model = models[0] if models else "unknown"
        
        llm_provider = UniversalProvider(provider_name=new_provider, model_name=new_model)
        if decision_engine:
            decision_engine.llm = llm_provider
            
        save_user_config(new_provider, new_model)
        await update.message.reply_text(f"✅ Đã chuyển sang nhà cung cấp: {new_provider}\nModel tự động chọn: {new_model}")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi chuyển provider: {e}")


async def handle_model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global llm_provider
    if not update.message: return
    
    if not context.args:
        from providers import get_available_models
        provider_name = getattr(llm_provider, "provider_name", "gemini")
        models = get_available_models(provider_name)
        
        if not models:
            await update.message.reply_text(f"Không tự động lấy được danh sách model cho {provider_name}. Vui lòng gõ: /model <tên>")
            return
            
        keyboard = []
        for i in range(0, len(models), 2):
            row = [InlineKeyboardButton(m, callback_data=f"model_{m}") for m in models[i:i+2]]
            keyboard.append(row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"Chọn model cho {provider_name}:", reply_markup=reply_markup)
        return
        
    new_model = context.args[0]
    try:
        from cli.chat import save_user_config
        provider_name = getattr(llm_provider, "provider_name", "gemini")
        
        llm_provider = UniversalProvider(provider_name=provider_name, model_name=new_model)
        if decision_engine:
            decision_engine.llm = llm_provider
            
        save_user_config(provider_name, new_model)
        await update.message.reply_text(f"✅ Đã chuyển model thành: {new_model}")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi chuyển model: {e}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    global llm_provider
    from cli.chat import save_user_config
    from providers import get_available_models, UniversalProvider
    
    try:
        if data.startswith("provider_"):
            new_provider = data.replace("provider_", "")
            models = get_available_models(new_provider)
            new_model = models[0] if models else "unknown"
            
            llm_provider = UniversalProvider(provider_name=new_provider, model_name=new_model)
            if decision_engine:
                decision_engine.llm = llm_provider
                
            save_user_config(new_provider, new_model)
            await query.edit_message_text(f"✅ Đã chọn nhà cung cấp: {new_provider}\nModel tự động chọn: {new_model}")
            
        elif data.startswith("model_"):
            new_model = data.replace("model_", "")
            provider_name = getattr(llm_provider, "provider_name", "gemini")
            
            llm_provider = UniversalProvider(provider_name=provider_name, model_name=new_model)
            if decision_engine:
                decision_engine.llm = llm_provider
                
            save_user_config(provider_name, new_model)
            await query.edit_message_text(f"✅ Đã chọn model: {new_model}")
    except Exception as e:
        await query.edit_message_text(f"❌ Đã xảy ra lỗi: {e}")



async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle incoming text messages from a Telegram user.

    This function intercepts the user's message, uses the DecisionEngine to determine
    if a specific skill (like browser_automation) is needed, and either executes
    that skill or falls back to a normal conversational response via Gemini.

    Args:
        update (Update): The incoming update containing the message.
        context (ContextTypes.DEFAULT_TYPE): The context object provided by the handler.

    Returns:
        None
    """
    if not update.message or not update.message.text:
        return

    user_text = update.message.text

    if not decision_engine or not llm_provider:
        await update.message.reply_text(f"⚠️ Hệ thống AI chưa sẵn sàng. Bạn vừa nhắn: {user_text}")
        return

    # Notify user that the bot is processing
    processing_msg = await update.message.reply_text("⏳ Đang phân tích yêu cầu...")

    try:
        # 1. Decide the appropriate skill based on user intent
        decision = decision_engine.decide_skill(user_text)
        chosen_skill = decision.get("skill", "UNKNOWN")
        reasoning = decision.get("analysis", "Không rõ lý do.")

        if chosen_skill != "UNKNOWN":
            await processing_msg.edit_text(f"🔍 Skill selected: {chosen_skill}\nReasoning: {reasoning}")

            # 2. Execute the chosen skill
            await update.message.reply_text(f"Đang thực thi kỹ năng {chosen_skill}...")
            
            try:
                # We extract the arguments from the decision engine's tool call parsing
                tool_args = decision.get("arguments", {})
                
                # Dynamically execute through the unified skill registry
                result = await registry.execute_tool(chosen_skill, **tool_args)
                
                # We output as raw text to avoid Markdown parsing errors in Telegram
                await update.message.reply_text(f"{str(result)}")
            except Exception as ex:
                await update.message.reply_text(f"Lỗi thực thi kỹ năng '{chosen_skill}': {ex}")
        
        else:
            # 3. Fallback to standard chat conversation
            await processing_msg.edit_text("💬 Đang suy nghĩ...")
            
            full_response = ""
            for chunk in llm_provider.send_message_stream(user_text):
                full_response += chunk
                
            # Send the complete response back to the user
            # Again, plain text to avoid unescaped characters breaking telegram's Markdown parser
            await processing_msg.edit_text(full_response)

    except Exception as e:
        await processing_msg.edit_text(f"Có lỗi xảy ra trong quá trình xử lý: {str(e)}")
