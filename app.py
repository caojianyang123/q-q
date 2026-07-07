import streamlit as st
from agents import chat_with_main, chat_with_specific
import os
import json

CHAT_FILE = "chat_history.json"

st.set_page_config(page_title="多智能体助手", page_icon="🤖", layout="wide")

agent_options = {
    "auto": "🤖 自动选择",
    "search": "🔍 情报搜集",
    "analysis": "📊 数据分析",
    "report": "📝 报告撰写",
}

def load_chats():
    if os.path.exists(CHAT_FILE):
        try:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return [{"id": 1, "title": "新对话", "messages": []}]

def save_chats():
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.chat_sessions, f)

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = load_chats()
    st.session_state.active_chat_id = st.session_state.chat_sessions[0]["id"]

def create_new_chat():
    if st.session_state.chat_sessions:
        new_id = max(c["id"] for c in st.session_state.chat_sessions) + 1
    else:
        new_id = 1
    st.session_state.chat_sessions.append({
        "id": new_id,
        "title": "新对话",
        "messages": [],
    })
    st.session_state.active_chat_id = new_id
    save_chats()

def delete_chat(chat_id: int):
    for i, chat in enumerate(st.session_state.chat_sessions):
        if chat["id"] == chat_id:
            del st.session_state.chat_sessions[i]
            break
    
    raw_dir = f"data/raw_materials/{chat_id}"
    report_dir = f"reports/{chat_id}"
    
    if os.path.exists(raw_dir):
        for f in os.listdir(raw_dir):
            os.remove(os.path.join(raw_dir, f))
        os.rmdir(raw_dir)
    
    if os.path.exists(report_dir):
        for f in os.listdir(report_dir):
            os.remove(os.path.join(report_dir, f))
        os.rmdir(report_dir)
    
    if st.session_state.chat_sessions:
        st.session_state.active_chat_id = st.session_state.chat_sessions[0]["id"]
    else:
        create_new_chat()
    
    save_chats()

def get_current_chat():
    for chat in st.session_state.chat_sessions:
        if chat["id"] == st.session_state.active_chat_id:
            return chat
    return None

def get_generated_files(chat_id: int):
    files = []
    raw_dir = f"data/raw_materials/{chat_id}"
    report_dir = f"reports/{chat_id}"
    
    if os.path.exists(raw_dir):
        for f in os.listdir(raw_dir):
            files.append({"path": os.path.join(raw_dir, f), "type": "搜索数据"})
    
    if os.path.exists(report_dir):
        for f in os.listdir(report_dir):
            files.append({"path": os.path.join(report_dir, f), "type": "周报"})
    
    return files

with st.sidebar:
    st.button("➕ 新对话", on_click=create_new_chat)
    st.divider()
    
    for chat in st.session_state.chat_sessions:
        is_active = chat["id"] == st.session_state.active_chat_id
        title = chat["messages"][0]["content"][:20] if chat["messages"] else "新对话"
        
        col_chat, col_del = st.columns([4, 1])
        with col_chat:
            if st.button(title, key=f"chat_{chat['id']}", use_container_width=True, 
                        type="primary" if is_active else "secondary"):
                st.session_state.active_chat_id = chat["id"]
        with col_del:
            if st.button("🗑️", key=f"del_{chat['id']}", use_container_width=True):
                delete_chat(chat["id"])
                st.rerun()
    
    st.divider()
    st.selectbox("选择智能体", options=list(agent_options.keys()), 
                 format_func=lambda x: agent_options[x], key="agent_select")

current_chat = get_current_chat()
st.session_state["current_chat_id"] = current_chat["id"]

col1, col2 = st.columns([3, 1])

with col1:
    st.title("🤖 多智能体助手")
    st.caption("情报搜集 · 数据分析 · 报告撰写")

    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            if "agent" in msg:
                st.caption(f"由 {agent_options.get(msg['agent'], msg['agent'])} 回答")
            st.markdown(msg["content"])

    if prompt := st.chat_input("问我任何问题..."):
        current_chat["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                history = ""
                for msg in current_chat["messages"][:-1]:
                    role = "用户" if msg["role"] == "user" else "助手"
                    history += f"{role}: {msg['content']}\n"
                
                selected_agent = st.session_state.get("agent_select", "auto")
                st.session_state["current_chat_id"] = current_chat["id"]
                if selected_agent == "auto":
                    response = chat_with_main(prompt, history, current_chat["id"])
                    agent_name = "auto"
                else:
                    response = chat_with_specific(selected_agent, prompt, history, current_chat["id"])
                    agent_name = selected_agent
            st.caption(f"由 {agent_options.get(agent_name, agent_name)} 回答")
            st.markdown(response)

        current_chat["messages"].append(
            {"role": "assistant", "content": response, "agent": agent_name}
        )
        save_chats()

with col2:
    st.subheader("📁 生成的文件")
    files = get_generated_files(current_chat["id"])
    if files:
        for file_info in files:
            with st.expander(f"{file_info['type']}: {os.path.basename(file_info['path'])}"):
                try:
                    with open(file_info["path"], "r", encoding="utf-8") as f:
                        content = f.read()
                    st.text_area("", content, height=200)
                except:
                    st.write("无法读取文件")
    else:
        st.write("暂无生成的文件")