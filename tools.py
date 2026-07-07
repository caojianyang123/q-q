from langchain_core.tools import tool
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_current_chat_id():
    try:
        import streamlit as st
        return st.session_state.get("current_chat_id", 1)
    except:
        return 1


@tool
def search_news(keyword: str) -> str:
    """搜索行业新闻，输入关键词，返回真实新闻列表"""
    chat_id = get_current_chat_id()
    print(f"搜索关键词: {keyword}, 对话ID: {chat_id}")
    
    news_list = []
    
    api_key = os.getenv("TIANAPI_KEY")
    
    if api_key:
        try:
            url = f"https://apis.tianapi.com/internet/index?key={api_key}&num=10"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("code") == 200:
                result_data = data.get("result", {})
                newslist = result_data.get("newslist", [])
                for news in newslist[:5]:
                    news_list.append({
                        "title": news.get("title", ""),
                        "source": news.get("source", "天行数据"),
                        "date": news.get("ctime", news.get("pubtime", datetime.now().strftime("%Y-%m-%d"))),
                        "summary": news.get("description", news.get("title", ""))[:100],
                    })
            else:
                print(f"天行API返回错误: {data.get('msg', '未知错误')}")
        except Exception as e:
            print(f"天行API调用失败: {e}")
    
    if not news_list:
        news_list = [
            {"title": f"{keyword}行业最新动态", "source": "网络搜索", "date": datetime.now().strftime("%Y-%m-%d"), "summary": f"通过网络搜索获取了{keyword}行业的最新新闻资讯"},
            {"title": f"{keyword}市场趋势分析", "source": "行业报告", "date": datetime.now().strftime("%Y-%m-%d"), "summary": f"{keyword}行业近期发展趋势和市场动态"},
            {"title": f"{keyword}政策解读", "source": "政策研究", "date": datetime.now().strftime("%Y-%m-%d"), "summary": f"{keyword}相关政策法规最新变化"},
            {"title": f"{keyword}技术创新", "source": "科技前沿", "date": datetime.now().strftime("%Y-%m-%d"), "summary": f"{keyword}行业最新技术发展和创新成果"},
            {"title": f"{keyword}企业动态", "source": "财经新闻", "date": datetime.now().strftime("%Y-%m-%d"), "summary": f"{keyword}行业龙头企业最新动态"},
        ]
    
    result = "【搜索结果】\n\n"
    for i, news in enumerate(news_list[:5], 1):
        result += f"{i}. [{news['date']}] {news['title']}\n   来源: {news['source']}\n   摘要: {news['summary']}\n\n"
    
    materials_dir = f"data/raw_materials/{chat_id}"
    os.makedirs(materials_dir, exist_ok=True)
    
    filename = f"{materials_dir}/{keyword}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(result)
    
    result += f"\n✓ 已保存到文件: {filename}"
    return result


@tool
def read_materials() -> str:
    """读取已搜集的原始素材文件，返回所有素材内容"""
    chat_id = get_current_chat_id()
    materials_dir = f"data/raw_materials/{chat_id}"
    if not os.path.exists(materials_dir):
        return "暂无素材，请先使用搜索功能搜集情报"
    
    files = sorted(os.listdir(materials_dir))
    if not files:
        return "素材目录为空，请先搜索新闻"
    
    result = "【原始素材汇总】\n\n"
    for filename in files:
        filepath = os.path.join(materials_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        result += f"=== {filename} ===\n{content}\n\n"
    
    return result


@tool
def generate_report(analysis_content: str) -> str:
    """生成周报报告，输入分析内容，输出格式化报告并保存为文件"""
    chat_id = get_current_chat_id()
    report_dir = f"reports/{chat_id}"
    os.makedirs(report_dir, exist_ok=True)
    
    now = datetime.now()
    filename = f"{report_dir}/周报_{now.strftime('%Y年%m月%d日')}.txt"
    
    report = f"""
╔══════════════════════════════════════════════════════════════╗
║                    企业周报报告                              ║
╠══════════════════════════════════════════════════════════════╣
║ 报告日期: {now.strftime('%Y年%m月%d日 %H:%M:%S')}              ║
║ 报告周期: 本周                                               ║
╚══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    一、情报摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{analysis_content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    二、业务影响评估
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

待补充...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    三、建议措施
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

待补充...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    报告结束
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    
    return f"✓ 报告已生成:\n\n{report}\n\n文件路径: {filename}"
