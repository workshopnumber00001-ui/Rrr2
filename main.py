# 🔧 Standard Library
import os
import re
import sys
import time
import json
import random
import string
import shutil
import zipfile
import urllib
import subprocess
import datetime
import pytz
import io
import tempfile
import asyncio
import html as html_lib
from base64 import b64encode, b64decode
from subprocess import getstatusoutput

# 📦 Third-party Libraries
import aiohttp
import aiofiles
import requests
import ffmpeg
import m3u8
import cloudscraper
import yt_dlp
import tgcrypto
from logs import logging
from bs4 import BeautifulSoup
from pytube import YouTube
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from aiohttp import ClientTimeout, ClientError

# ⚙️ Pyrogram
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import (
    FloodWait,
    BadRequest,
    Unauthorized,
    SessionExpired,
    AuthKeyDuplicated,
    AuthKeyUnregistered,
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError
)
from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified

# 🧠 Bot Modules
import auth
import thanos as helper
from thanos import *

from clean import register_clean_handler
from logs import logging
from utils import progress_bar
from vars import *
from pyromod import listen
from db import db

# ================= RAM.PY CONFIGURATION =================

LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "-1003692273087"))
API_BASE = os.getenv("API_BASE", "https://backend.multistreaming.site/api")
RAM_AUTHORIZED_USERS = [int(uid.strip()) for uid in os.getenv("AUTHORIZED_USERS", "5349573682,8453406690").split(",") if uid.strip()]
if not RAM_AUTHORIZED_USERS:
    RAM_AUTHORIZED_USERS = [5349573682, 8453406690]

def is_ram_authorized(user_id):
    return user_id in RAM_AUTHORIZED_USERS or user_id in ADMINS or user_id == OWNER_ID

STYLISH_NAME = os.getenv("STYLISH_NAME", "⛧𓂀 𝕮𝖆𝖕𝖙𝖆𝖎𝖓 ☠️ 𓂀⛧")
START_THUMBNAIL = os.getenv("START_THUMBNAIL", "https://i.ibb.co/xKptwJmc/1782753295338.jpg")
EXTRACT_THUMBNAIL = os.getenv("EXTRACT_THUMBNAIL", "https://i.ibb.co/xKptwJmc/1782753295338.jpg")
BANNER_LINE = "━━━━━━━━━━━━━━━━━━━━━━\n⚡ ᴏᴡɴᴇʀ: ⛧𓂀 𝕮𝖆𝖕𝖙𝖆𝖎𝖓 ☠️ 𓂀⛧\n━━━━━━━━━━━━━━━━━━━━━━\n"

CW_ALL_BATCHES = os.getenv("CW_ALL_BATCHES", "https://cw-ut-apis-e37c22944d2f.herokuapp.com/api/batches")
CW_BATCH_API = os.getenv("CW_BATCH_API", "https://cw-api-website.vercel.app/batch/{}")
CW_TOPIC_API = os.getenv("CW_TOPIC_API", "https://cw-api-website.vercel.app/batch?batchid={}&topicid={}")
CW_VIDEO_API = os.getenv("CW_VIDEO_API", "https://cw-vid-virid.vercel.app/get_video_details?name={}")

CAREERWILL_BUILD_ID = os.getenv("CAREERWILL_BUILD_ID", "WuAwSZiJu-Vol1R998vWW")
CAREERWILL_BASE = f"https://web.careerwill.com/_next/data/{CAREERWILL_BUILD_ID}"
CAREERWILL_BATCHES = f"{CAREERWILL_BASE}/live-classes.json?view=List&interface_id=1"
CAREERWILL_BATCH_DETAIL = f"{CAREERWILL_BASE}/live-classes/{{}}.json?interface_id=1"
CAREERWILL_COOKIE = os.getenv("CAREERWILL_COOKIE", "")

CAREERWILL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://web.careerwill.com/live-classes?view=List&interface_id=1",
    "Accept": "application/json",
}
if CAREERWILL_COOKIE:
    CAREERWILL_HEADERS["Cookie"] = CAREERWILL_COOKIE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# ================= SET IST TIMEZONE =================
IST = pytz.timezone('Asia/Kolkata')
ram_user_data = {}

# ================= HELPER FUNCTIONS (RAM.PY) =================
def sanitize_filename(name):
    return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')

async def fetch_with_retry(session, url, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.warning(f"Attempt {attempt+1}: {url} returned {resp.status}")
        except (ClientError, asyncio.TimeoutError) as e:
            logging.warning(f"Attempt {attempt+1} failed: {e}")
        await asyncio.sleep(1)
    return None

def is_video_link(url):
    if not url:
        return False
    url_lower = url.lower()
    if any(url_lower.endswith(ext) for ext in ['.mp4', '.webm', '.mov']):
        return True
    if 'youtube.com/watch' in url_lower or 'youtu.be/' in url_lower or 'vimeo.com/' in url_lower:
        return True
    return False

def get_video_embed_html(url, title):
    url_lower = url.lower()
    if 'youtube.com/watch' in url_lower:
        vid = re.search(r'v=([^&]+)', url)
        if vid:
            return f'<div class="iframe-container"><iframe src="https://www.youtube.com/embed/{vid.group(1)}" allowfullscreen></iframe></div>'
    if 'youtu.be/' in url_lower:
        vid = url.split('/')[-1].split('?')[0]
        if vid:
            return f'<div class="iframe-container"><iframe src="https://www.youtube.com/embed/{vid}" allowfullscreen></iframe></div>'
    if 'vimeo.com/' in url_lower:
        vid = url.split('/')[-1].split('?')[0]
        if vid:
            return f'<div class="iframe-container"><iframe src="https://player.vimeo.com/video/{vid}" allowfullscreen></iframe></div>'
    if url_lower.endswith(('.mp4', '.webm')):
        mime = 'video/mp4' if url_lower.endswith('.mp4') else 'video/webm'
        return f'<div class="video-container"><video controls preload="metadata"><source src="{url}" type="{mime}"></video></div>'
    return None

async def get_careerwill_build_id():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://web.careerwill.com/live-classes") as resp:
                html_content = await resp.text()
                match = re.search(r'/_next/static/([^/]+)/_buildManifest', html_content)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return None

async def decrypt_video_token_async(session, raw_token_str):
    if not raw_token_str or str(raw_token_str).startswith('http'):
        return raw_token_str, ""
    try:
        target_url = CW_VIDEO_API.format(raw_token_str)
        async with session.get(target_url, timeout=8) as dec_res:
            if dec_res.status == 200:
                dec_data = await dec_res.json()
                if dec_data.get("status") is True and "data" in dec_data and "link" in dec_data["data"]:
                    link_obj = dec_data["data"]["link"]
                    return link_obj.get("file_url"), link_obj.get("token", "")
                else:
                    file_url = dec_data.get('videoUrl') or dec_data.get('url') or dec_data.get('link') or dec_data.get('file_url')
                    return file_url or target_url, dec_data.get('token', '')
    except Exception:
        pass
    return CW_VIDEO_API.format(raw_token_str), ""

async def process_single_video_async(session, vid, topic_name):
    if not isinstance(vid, dict):
        return "", 0
    vid_name = vid.get('title') or vid.get('videoName') or vid.get('name') or 'Video'
    raw_token = vid.get('video_url') or vid.get('videoLink') or vid.get('url') or vid.get('link') or vid.get('video_url_raw')
    if not raw_token:
        for val in vid.values():
            val_str = str(val).strip()
            if "_" in val_str and not val_str.startswith('http') and len(val_str) > 8:
                raw_token = val_str
                break
    if raw_token:
        raw_token_str = str(raw_token).strip()
        if not raw_token_str.startswith('http'):
            video_url, key_token = await decrypt_video_token_async(session, raw_token_str)
            v_text = f"[{topic_name}] {STYLISH_NAME} {vid_name} : {video_url}\n"
            if key_token:
                v_text += f"🔑 DRM Key: {key_token}\n"
            return v_text, 1
        else:
            return f"[{topic_name}] {STYLISH_NAME} {vid_name} : {raw_token_str}\n", 1
    return "", 0

async def extract_topic_content(session, batch_id, topic, t_index):
    if not isinstance(topic, dict):
        return "", 0, 0
    topic_name = topic.get('topicName') or topic.get('name') or 'Unnamed Topic'
    topic_id = topic.get('topicId') or topic.get('id') or topic.get('_id')
    if not topic_id:
        return "", 0, 0
    try:
        content_url = CW_TOPIC_API.format(batch_id, topic_id)
        async with session.get(content_url, timeout=12) as content_res:
            if content_res.status != 200:
                return "", 0, 0
            content_json = await content_res.json()
            inner_data = content_json.get('data', content_json) if isinstance(content_json, dict) else content_json
            raw_videos, raw_pdfs = [], []
            if isinstance(inner_data, dict):
                raw_videos = inner_data.get('classes', []) or inner_data.get('videos', []) or inner_data.get('class', [])
                raw_pdfs = inner_data.get('notes', []) or inner_data.get('pdfs', []) or inner_data.get('batch-notes', [])
            v_count, p_count = 0, 0
            t_text = ""
            if raw_videos:
                tasks = [process_single_video_async(session, vid, topic_name) for vid in raw_videos]
                video_results = await asyncio.gather(*tasks)
                for res_str, count in video_results:
                    t_text += res_str
                    v_count += count
            if raw_pdfs:
                for pdf in raw_pdfs:
                    if isinstance(pdf, dict):
                        pdf_name = pdf.get('title') or pdf.get('pdfName') or pdf.get('name') or 'Document'
                        pdf_url = pdf.get('download_url') or pdf.get('view_url') or pdf.get('pdfLink') or 'No Link'
                        t_text += f"[{topic_name}] {STYLISH_NAME} {pdf_name} : {pdf_url}\n"
                        p_count += 1
            return t_text, v_count, p_count
    except Exception:
        return "", 0, 0

# ================= MODERN HTML TEMPLATE (RAM.PY) =================

HTML_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Content • Rαԃԋα</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg-primary: #0a0e1a; --bg-secondary: #111827; --bg-card: #1a2236;
            --bg-card-hover: #24304a; --text-primary: #e5e7eb; --text-secondary: #9ca3af;
            --accent: #8b5cf6; --accent-hover: #7c3aed; --accent-glow: rgba(139, 92, 246, 0.3);
            --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --border-color: rgba(255, 255, 255, 0.06); --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }
        body {
            font-family: 'Inter', -apple-system, sans-serif; background: var(--bg-primary);
            color: var(--text-primary); min-height: 100vh; padding: 20px;
            background-image: radial-gradient(ellipse at 10% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
                              radial-gradient(ellipse at 90% 80%, rgba(236, 72, 153, 0.05) 0%, transparent 50%);
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: var(--gradient-1); padding: 40px 30px; border-radius: 24px; text-align: center;
            margin-bottom: 30px; position: relative; overflow: hidden;
            box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
        }
        .header::before {
            content: ''; position: absolute; top: -50%; right: -20%; width: 300px; height: 300px;
            background: rgba(255, 255, 255, 0.05); border-radius: 50%; animation: float 6s ease-in-out infinite;
        }
        .header::after {
            content: ''; position: absolute; bottom: -40%; left: -10%; width: 200px; height: 200px;
            background: rgba(255, 255, 255, 0.03); border-radius: 50%; animation: float 8s ease-in-out infinite reverse;
        }
        @keyframes float { 0%, 100% { transform: translate(0, 0); } 50% { transform: translate(-20px, -20px); } }
        .header-content { position: relative; z-index: 1; }
        .header h1 { font-size: 32px; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 8px; text-shadow: 0 2px 20px rgba(0, 0, 0, 0.2); }
        .header h1 i { margin-right: 12px; color: #fbbf24; }
        .header p { opacity: 0.9; font-size: 15px; font-weight: 400; }
        .header .badge-count {
            display: inline-block; background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);
            padding: 6px 20px; border-radius: 50px; margin-top: 12px; font-size: 13px; border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .stats-bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 30px; }
        .stat-item {
            background: var(--bg-card); padding: 16px 20px; border-radius: 16px; text-align: center;
            border: 1px solid var(--border-color); transition: all 0.3s ease;
        }
        .stat-item:hover { transform: translateY(-2px); border-color: var(--accent); box-shadow: 0 0 30px var(--accent-glow); }
        .stat-item .number {
            font-size: 24px; font-weight: 700; background: var(--gradient-1);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .stat-item .label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        .controls { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 24px; justify-content: center; }
        .btn-control {
            background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-primary);
            padding: 12px 28px; border-radius: 50px; font-size: 14px; font-weight: 600; cursor: pointer;
            transition: all 0.3s ease; display: inline-flex; align-items: center; gap: 10px; font-family: 'Inter', sans-serif;
        }
        .btn-control:hover { background: var(--bg-card-hover); border-color: var(--accent); transform: translateY(-2px); box-shadow: 0 8px 25px var(--accent-glow); }
        .btn-control.primary { background: var(--accent); border-color: var(--accent); }
        .btn-control.primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
        .card { background: var(--bg-card); border-radius: 20px; margin-bottom: 16px; border: 1px solid var(--border-color); overflow: hidden; transition: all 0.3s ease; }
        .card:hover { border-color: rgba(139, 92, 246, 0.2); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3); }
        .accordion-header {
            padding: 20px 24px; cursor: pointer; font-weight: 600; font-size: 16px;
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(255, 255, 255, 0.02); transition: all 0.3s ease; user-select: none;
            border-bottom: 1px solid transparent;
        }
        .accordion-header:hover { background: rgba(139, 92, 246, 0.05); }
        .accordion-header.active { border-bottom-color: var(--border-color); }
        .accordion-header .left { display: flex; align-items: center; gap: 12px; }
        .accordion-header .left i { color: var(--accent); font-size: 18px; width: 24px; }
        .accordion-header .badge { background: var(--accent); color: #fff; padding: 2px 14px; border-radius: 50px; font-size: 12px; font-weight: 600; }
        .accordion-header .icon { transition: transform 0.3s ease; color: var(--text-secondary); font-size: 18px; }
        .accordion-header .icon.rotated { transform: rotate(180deg); }
        .accordion-content { max-height: 0; overflow: hidden; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); padding: 0 24px; }
        .accordion-content.active { max-height: 9999px; padding: 20px 24px 24px; }
        .item { padding: 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .item:last-child { border-bottom: none; padding-bottom: 0; }
        .item-title { font-size: 15px; font-weight: 500; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 12px; color: var(--text-primary); line-height: 1.5; }
        .item-title i { color: var(--accent); font-size: 16px; margin-top: 2px; flex-shrink: 0; }
        .item-actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
        .btn {
            padding: 6px 18px; border-radius: 50px; text-decoration: none; font-size: 12px; font-weight: 600;
            display: inline-flex; align-items: center; gap: 8px; transition: all 0.3s ease;
            border: none; cursor: pointer; font-family: 'Inter', sans-serif;
        }
        .btn-watch { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.2); }
        .btn-watch:hover { background: rgba(59, 130, 246, 0.25); transform: translateY(-2px); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2); }
        .btn-download { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
        .btn-download:hover { background: rgba(16, 185, 129, 0.25); transform: translateY(-2px); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2); }
        .btn-pdf { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
        .btn-pdf:hover { background: rgba(245, 158, 11, 0.25); transform: translateY(-2px); box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2); }
        .video-container { margin: 12px 0 10px; border-radius: 14px; overflow: hidden; background: #000; position: relative; }
        .video-container video { width: 100%; display: block; border-radius: 14px; }
        .iframe-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 12px 0 10px; border-radius: 14px; background: #000; }
        .iframe-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; border-radius: 14px; }
        .toast {
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: var(--bg-card); color: var(--text-primary); padding: 14px 28px; border-radius: 16px;
            border: 1px solid var(--border-color); box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            font-size: 14px; font-weight: 500; opacity: 0; transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 999; backdrop-filter: blur(20px); display: flex; align-items: center; gap: 12px;
        }
        .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }
        .toast i { font-size: 20px; }
        .toast.success i { color: #34d399; }
        .toast.error i { color: #f87171; }
        .scroll-top {
            position: fixed; bottom: 30px; right: 30px; background: var(--accent); color: #fff;
            width: 50px; height: 50px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 20px; box-shadow: 0 8px 30px var(--accent-glow); cursor: pointer; transition: all 0.3s ease;
            opacity: 0; pointer-events: none; border: none; z-index: 100;
        }
        .scroll-top.visible { opacity: 1; pointer-events: auto; }
        .scroll-top:hover { transform: scale(1.1) translateY(-3px); background: var(--accent-hover); }
        .shimmer {
            background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
            background-size: 200% 100%; animation: shimmer 1.5s infinite; border-radius: 12px; height: 60px; margin-bottom: 12px;
        }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
        @media (max-width: 640px) { body { padding: 12px; } .header { padding: 28px 20px; } .header h1 { font-size: 24px; } .accordion-header { font-size: 14px; padding: 16px 18px; } .item-title { font-size: 14px; } .btn { font-size: 11px; padding: 5px 14px; } .stats-bar { grid-template-columns: repeat(2, 1fr); } .controls { gap: 8px; } .btn-control { padding: 10px 20px; font-size: 13px; } .toast { width: 90%; font-size: 13px; padding: 12px 20px; } }
        @media (max-width: 400px) { .stats-bar { grid-template-columns: 1fr; } }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg-primary); }
        ::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent-hover); }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="header-content">
            <h1><i class="fas fa-crown"></i> Rαԃԋα</h1>
            <p><i class="fas fa-sparkles"></i> Premium Learning Content</p>
            <span class="badge-count" id="totalItems"><i class="fas fa-layer-group"></i> Loading...</span>
        </div>
    </div>
    <div class="stats-bar" id="statsBar">
        <div class="stat-item"><div class="number" id="statSubjects">0</div><div class="label"><i class="fas fa-folder"></i> Subjects</div></div>
        <div class="stat-item"><div class="number" id="statVideos">0</div><div class="label"><i class="fas fa-video"></i> Videos</div></div>
        <div class="stat-item"><div class="number" id="statPdfs">0</div><div class="label"><i class="fas fa-file-pdf"></i> PDFs</div></div>
        <div class="stat-item"><div class="number" id="statTotal">0</div><div class="label"><i class="fas fa-tasks"></i> Total Items</div></div>
    </div>
    <div class="controls">
        <button class="btn-control primary" onclick="expandAll()"><i class="fas fa-expand-alt"></i> Expand All</button>
        <button class="btn-control" onclick="collapseAll()"><i class="fas fa-compress-alt"></i> Collapse All</button>
        <button class="btn-control" onclick="copyAllContent()"><i class="fas fa-copy"></i> Copy All</button>
        <button class="btn-control" onclick="copyLinksOnly()"><i class="fas fa-link"></i> Copy Links Only</button>
    </div>
    <div id="contentArea"></div>
    <div class="toast" id="toast"><i class="fas fa-check-circle"></i><span id="toastMessage">Copied!</span></div>
    <button class="scroll-top" id="scrollTopBtn" onclick="window.scrollTo({top:0,behavior:'smooth'})"><i class="fas fa-arrow-up"></i></button>
"""

# ================= ORIGINAL DRM BOT CONFIG =================

auto_flags = {}
auto_clicked = False

# Global variables
watermark = "/d"
count = 0
userbot = None
timeout_duration = 300

# Default settings
DEFAULT_SETTINGS = {
    "auto_upload": True,
    "batch_upload": True,
    "resume": False,
    "downloader_name": "🥀°𓏲кяιѕнηα⋆🌿",
    "show_extension": True,
    "caption_style": "bracket_style",
    "show_title": True,
    "quality": "480",
    "thumbnail": "default",
    "pdf_watermark": False,
    "pdf_watermark_text": "",
    "auto_grouping": False,
    "video_player_link": True,
    "pw_token": "your_token_here",
    "proxy": "",
    "sticker_responses": True,
}

# Style display names mapping
STYLE_DISPLAY_NAMES = {
    "default": "📝 Default",
    "minimal_glass": "🔲 Minimal Glass",
    "neon_glow": "💜 Neon Glow",
    "premium_card": "💎 Premium Card",
    "dark_futuristic": "🌑 Dark Futuristic",
    "clean_professional": "✨ Clean Pro",
    "cyber_terminal": "💻 Cyber/Terminal",
    "dual_border": "🏛️ Dual Border",
    "rounded_neon": "🎯 Rounded Neon",
    "instagram": "📸 Instagram",
    "matrix": "💚 Matrix/Code",
    "space_galaxy": "🌌 Space Galaxy",
    "minimal_dots": "⚪ Minimal Dots",
    "clean_glass": "🪟 Clean Glass",
    "smooth_flow": "🌊 Smooth Flow",
    "minimal_dot": "🎯 Minimal Dot",
    "modern_border": "🏛️ Modern Border",
    "ultra_clean": "💎 Ultra Clean",
    "bracket_style": "📦 Bracket Style",
}

ALL_STYLES = [
    "default",
    "minimal_glass",
    "neon_glow",
    "premium_card",
    "dark_futuristic",
    "clean_professional",
    "cyber_terminal",
    "dual_border",
    "rounded_neon",
    "instagram",
    "matrix",
    "space_galaxy",
    "minimal_dots",
    "clean_glass",
    "smooth_flow",
    "minimal_dot",
    "modern_border",
    "ultra_clean",
    "bracket_style",
]

# Initialize bot
bot = Client(
    "ugx",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=300,
    sleep_threshold=60,
    in_memory=True
)

# Register clean handler
register_clean_handler(bot)

# ========================= VIDEO CAPTION STYLES =========================

def get_video_caption(style, count, batch_blockquote, name1, ext_actual, res, date_str, time_str, CR):
    """Generate video caption based on selected style"""
    
    # Remove HTML tags from batch_blockquote for clean display
    plain_batch = re.sub(r'<[^>]+>', '', batch_blockquote).strip()
    
    # ========== BRACKET STYLE (DEFAULT) ==========
    if style == "bracket_style":
        return (
            f"\n[──────────────────────]\n"
            f"│  ✦ ID    : {str(count).zfill(3)}\n"
            f"│\n"
            f"│  Batch : {plain_batch}\n"
            f"│\n"
            f"│  Title : {name1}\n"
            f"│\n"
            f"│  Ext   : {CR}.{ext_actual}\n"
            f"│\n"
            f"│  Res   : {res}\n"
            f"│\n"
            f"│  ✦ Download By : {CR}\n"
            f"[──────────────────────]\n"
            f"\n📅 {time_str}\n"
        )
    
    # ========== OTHER STYLES ==========
    elif style == "minimal_glass":
        return (
            f"\n<b>┌───⧫ 𝐕𝐈𝐃𝐄𝐎 𝐈𝐍𝐅𝐎 ⧫───┐</b>\n"
            f"│\n"
            f"│  <b>📌 Index</b> : {str(count).zfill(3)}\n"
            f"│  <b>📚 Batch</b> : {plain_batch}\n"
            f"│  <b>📖 Title</b> : {name1}\n"
            f"│  <b>📤 Ext</b> : {CR}.{ext_actual}\n"
            f"│  <b>📐 Res</b> : {res}\n"
            f"│  <b>📅 Date</b> : {date_str}\n"
            f"│\n"
            f"├───⧫ <b>UPLOADED BY</b> ⧫───┤\n"
            f"│  <b>{CR}</b>\n"
            f"│\n"
            f"└───⧫ {time_str} ⧫───┘\n"
        )
    elif style == "neon_glow":
        return (
            f"\n<b>◤━━━━━━━━━⧫ 𝐕𝐈𝐃𝐄𝐎 ⧫━━━━━━━━━◥</b>\n\n"
            f"  <b>🧭 ID</b> : {str(count).zfill(3)}\n"
            f"  <b>📦 Batch</b> : {plain_batch}\n"
            f"  <b>📄 Title</b> : {name1}\n"
            f"  <b>⚡ Ext</b> : {CR}.{ext_actual}\n"
            f"  <b>📊 Res</b> : {res}\n"
            f"  <b>📆 Date</b> : {date_str}\n\n"
            f"◣━━━━━━━⧫ <b>{CR}</b> ⧫━━━━━━━◢\n"
            f"<i>{time_str}</i>\n"
        )
    elif style == "premium_card":
        return (
            f"\n<b>┏━━━━━━━━━━━━━━━━━━━━━━┓</b>\n"
            f"<b>┃  ⚡ 𝐕𝐈𝐃𝐄𝐎 𝐃𝐄𝐓𝐀𝐈𝐋𝐒</b>\n"
            f"<b>┣━━━━━━━━━━━━━━━━━━━━━━┫</b>\n"
            f"<b>┃</b>\n"
            f"<b>┃  🏷️ ID</b>  : {str(count).zfill(3)}\n"
            f"<b>┃  📁 Batch</b> : {plain_batch}\n"
            f"<b>┃  📌 Title</b> : {name1}\n"
            f"<b>┃  💾 Ext</b>  : {CR}.{ext_actual}\n"
            f"<b>┃  📐 Res</b>  : {res}\n"
            f"<b>┃  📅 Date</b> : {date_str}\n"
            f"<b>┃</b>\n"
            f"<b>┣━━━━━━━━━━━━━━━━━━━━━━┫</b>\n"
            f"<b>┃  🎯 {CR}</b>\n"
            f"<b>┗━━━━━━━━━━━━━━━━━━━━━━┛</b>\n"
            f"\n<i>{time_str}</i>\n"
        )
    elif style == "dark_futuristic":
        return (
            f"\n<b>╔═══════════════════════╗</b>\n"
            f"<b>║  🔥 VIDEO DETAILS</b>\n"
            f"<b>╠═══════════════════════╣</b>\n"
            f"<b>║</b>\n"
            f"<b>║  ◆ ID</b>    : {str(count).zfill(3)}\n"
            f"<b>║  ◆ Batch</b> : {plain_batch}\n"
            f"<b>║  ◆ Title</b> : {name1}\n"
            f"<b>║  ◆ Ext</b>   : {CR}.{ext_actual}\n"
            f"<b>║  ◆ Res</b>   : {res}\n"
            f"<b>║  ◆ Date</b>  : {date_str}\n"
            f"<b>║</b>\n"
            f"<b>╠═══════════════════════╣</b>\n"
            f"<b>║  ✦ {CR}</b>\n"
            f"<b>╚═══════════════════════╝</b>\n\n"
            f"<i>⏱ {time_str}</i>\n"
        )
    elif style == "clean_professional":
        return (
            f"\n<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>\n"
            f"<b>  📌 VIDEO DETAILS</b>\n"
            f"<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>\n\n"
            f"  <b>🆔 Index</b> : {str(count).zfill(3)}\n"
            f"  <b>📦 Batch</b> : {plain_batch}\n"
            f"  <b>📄 Title</b> : {name1}\n"
            f"  <b>📎 Ext</b>   : {CR}.{ext_actual}\n"
            f"  <b>📐 Res</b>   : {res}\n"
            f"  <b>📆 Date</b>  : {date_str}\n\n"
            f"<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>\n"
            f"  <b>© {CR}</b>\n"
            f"<b>▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬</b>\n"
            f"<i>{time_str}</i>\n"
        )
    elif style == "cyber_terminal":
        return (
            f"\n<b>┌─[ VIDEO ]───────────────────┐</b>\n"
            f"<b>│</b>\n"
            f"<b>│  ╭─▶ ID</b>    : {str(count).zfill(3)}\n"
            f"<b>│  ├─▶ Batch</b> : {plain_batch}\n"
            f"<b>│  ├─▶ Title</b> : {name1}\n"
            f"<b>│  ├─▶ Ext</b>   : {CR}.{ext_actual}\n"
            f"<b>│  ├─▶ Res</b>   : {res}\n"
            f"<b>│  ╰─▶ Date</b>  : {date_str}\n"
            f"<b>│</b>\n"
            f"<b>├─────────────────────────────┤</b>\n"
            f"<b>│  🚀 {CR}</b>\n"
            f"<b>└─────────────────────────────┘</b>\n"
            f"\n<i>⏱ {time_str}</i>\n"
        )
    elif style == "dual_border":
        return (
            f"\n<b>╔══════════════════════════════╗</b>\n"
            f"<b>║   ✦ 𝐕𝐈𝐃𝐄𝐎 𝐃𝐄𝐓𝐀𝐈𝐋𝐒 ✦</b>\n"
            f"<b>╠══════════════════════════════╣</b>\n"
            f"<b>║</b>\n"
            f"<b>║  ✦ Index</b>   : {str(count).zfill(3)}\n"
            f"<b>║  ✦ Batch</b>   : {plain_batch}\n"
            f"<b>║  ✦ Title</b>   : {name1}\n"
            f"<b>║  ✦ Format</b>  : {CR}.{ext_actual}\n"
            f"<b>║  ✦ Quality</b> : {res}\n"
            f"<b>║  ✦ Date</b>    : {date_str}\n"
            f"<b>║</b>\n"
            f"<b>╠══════════════════════════════╣</b>\n"
            f"<b>║  ✦ Uploaded By</b>\n"
            f"<b>║  ╰─ {CR}</b>\n"
            f"<b>╚══════════════════════════════╝</b>\n\n"
            f"<i>🕐 {time_str}</i>\n"
        )
    elif style == "rounded_neon":
        return (
            f"\n<b>◈━━━━━━━━━━━━━━━━━━━━━━━━━◈</b>\n"
            f"<b>▣  🔥 VIDEO INFO</b>\n"
            f"<b>◈━━━━━━━━━━━━━━━━━━━━━━━━━◈</b>\n\n"
            f"  <b>⚡ ID</b>   : {str(count).zfill(3)}\n"
            f"  <b>📦 Batch</b> : {plain_batch}\n"
            f"  <b>📌 Title</b> : {name1}\n"
            f"  <b>🎯 Ext</b>  : {CR}.{ext_actual}\n"
            f"  <b>📐 Res</b>  : {res}\n"
            f"  <b>📅 Date</b> : {date_str}\n\n"
            f"<b>◈━━━━━━━━━━━━━━━━━━━━━━━━━◈</b>\n"
            f"  <b>🌟 {CR}</b>\n"
            f"<b>◈━━━━━━━━━━━━━━━━━━━━━━━━━◈</b>\n"
            f"\n<i>⏰ {time_str}</i>\n"
        )
    elif style == "instagram":
        return (
            f"\n<b>✨✨✨✨✨✨✨✨✨✨✨✨✨</b>\n\n"
            f"  <b>🎬 VIDEO</b>\n\n"
            f"  <b>📌</b> {str(count).zfill(3)}\n"
            f"  <b>📚</b> {plain_batch}\n"
            f"  <b>📖</b> {name1}\n"
            f"  <b>💾</b> {CR}.{ext_actual}\n"
            f"  <b>📐</b> {res}\n"
            f"  <b>📆</b> {date_str}\n\n"
            f"<b>✨✨✨✨✨✨✨✨✨✨✨✨✨</b>\n"
            f"  <b>💫 {CR}</b>\n"
            f"<b>✨✨✨✨✨✨✨✨✨✨✨✨✨</b>\n"
            f"\n<i>{time_str}</i>\n"
        )
    elif style == "matrix":
        return (
            f"\n<b>┌─────────────────────────┐</b>\n"
            f"<b>│  ███╗  ██╗███████╗ ██████╗</b>\n"
            f"<b>│  ████╗ ██║██╔════╝██╔═══██╗</b>\n"
            f"<b>│  ██╔██╗██║█████╗  ██║   ██║</b>\n"
            f"<b>│  ██║╚████║██╔══╝  ██║   ██║</b>\n"
            f"<b>│  ██║ ╚███║██║     ╚██████╔╝</b>\n"
            f"<b>│  ╚═╝  ╚══╝╚═╝      ╚═════╝</b>\n"
            f"<b>├─────────────────────────┤</b>\n"
            f"<b>│  ID</b>    : {str(count).zfill(3)}\n"
            f"<b>│  Batch</b> : {plain_batch}\n"
            f"<b>│  Title</b> : {name1}\n"
            f"<b>│  Ext</b>   : {CR}.{ext_actual}\n"
            f"<b>│  Res</b>   : {res}\n"
            f"<b>│  Date</b>  : {date_str}\n"
            f"<b>├─────────────────────────┤</b>\n"
            f"<b>│  ▶ {CR}</b>\n"
            f"<b>└─────────────────────────┘</b>\n"
            f"\n<i>⏱ {time_str}</i>\n"
        )
    elif style == "space_galaxy":
        return (
            f"\n<b>✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦</b>\n"
            f"<b>    🌟 VIDEO DETAILS</b>\n"
            f"<b>✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦</b>\n\n"
            f"  <b>🪐 Index</b> : {str(count).zfill(3)}\n"
            f"  <b>🌌 Batch</b> : {plain_batch}\n"
            f"  <b>📖 Title</b> : {name1}\n"
            f"  <b>🔗 Ext</b>  : {CR}.{ext_actual}\n"
            f"  <b>📐 Res</b>  : {res}\n"
            f"  <b>📅 Date</b> : {date_str}\n\n"
            f"<b>✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦</b>\n"
            f"  <b>⭐ {CR}</b>\n"
            f"<b>✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦✧✦</b>\n\n"
            f"<i>🕐 {time_str}</i>\n"
        )
    elif style == "minimal_dots":
        return (
            f"\n<b>· · · · · · · · · · · · · · ·</b>\n"
            f"<b>  📌 VIDEO</b>\n"
            f"<b>· · · · · · · · · · · · · · ·</b>\n\n"
            f"  <b>• ID</b>    : {str(count).zfill(3)}\n"
            f"  <b>• Batch</b> : {plain_batch}\n"
            f"  <b>• Title</b> : {name1}\n"
            f"  <b>• Ext</b>   : {CR}.{ext_actual}\n"
            f"  <b>• Res</b>   : {res}\n"
            f"  <b>• Date</b>  : {date_str}\n\n"
            f"<b>· · · · · · · · · · · · · · ·</b>\n"
            f"  <b>{CR}</b>\n"
            f"<b>· · · · · · · · · · · · · · ·</b>\n"
            f"\n<i>{time_str}</i>\n"
        )
    elif style == "clean_glass":
        return (
            f"\n<b>╭─────────────────────╮</b>\n"
            f"<b>│  ✦ VIDEO DETAILS</b>\n"
            f"<b>╰─────────────────────╯</b>\n\n"
            f"  <b>ID</b>    {str(count).zfill(3)}\n"
            f"  <b>Batch</b> {plain_batch}\n"
            f"  <b>Title</b> {name1}\n"
            f"  <b>Ext</b>   {CR}.{ext_actual}\n"
            f"  <b>Res</b>   {res}\n"
            f"  <b>Date</b>  {date_str}\n\n"
            f"<b>─────── ✦ ───────</b>\n"
            f"<i>{time_str}</i>\n"
            f"<b>  {CR}</b>\n"
        )
    elif style == "smooth_flow":
        return (
            f"\n<b>▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁</b>\n"
            f"<b>  📌 VIDEO</b>\n"
            f"<b>▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔</b>\n\n"
            f"  <b>◈ ID</b>    {str(count).zfill(3)}\n"
            f"  <b>◈ Batch</b> {plain_batch}\n"
            f"  <b>◈ Title</b> {name1}\n"
            f"  <b>◈ Ext</b>   {CR}.{ext_actual}\n"
            f"  <b>◈ Res</b>   {res}\n"
            f"  <b>◈ Date</b>  {date_str}\n\n"
            f"<b>▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁</b>\n"
            f"<i>{time_str}</i>\n"
            f"<b>  ◆ {CR}</b>\n"
        )
    elif style == "minimal_dot":
        return (
            f"\n<b>• • • • • • • • • • • • • •</b>\n"
            f"<b>  ▫ VIDEO</b>\n"
            f"<b>• • • • • • • • • • • • • •</b>\n\n"
            f"  <b>◉</b> ID    {str(count).zfill(3)}\n"
            f"  <b>◉</b> Batch {plain_batch}\n"
            f"  <b>◉</b> Title {name1}\n"
            f"  <b>◉</b> Ext   {CR}.{ext_actual}\n"
            f"  <b>◉</b> Res   {res}\n"
            f"  <b>◉</b> Date  {date_str}\n\n"
            f"<b>• • • • • • • • • • • • • •</b>\n"
            f"<i>{time_str}</i>\n"
            f"<b>  {CR}</b>\n"
        )
    elif style == "modern_border":
        return (
            f"\n<b>┌──────────────────────┐</b>\n"
            f"<b>│  ★ VIDEO DETAILS</b>\n"
            f"<b>├──────────────────────┤</b>\n"
            f"<b>│</b>\n"
            f"<b>│  ID</b>    {str(count).zfill(3)}\n"
            f"<b>│  Batch</b> {plain_batch}\n"
            f"<b>│  Title</b> {name1}\n"
            f"<b>│  Ext</b>   {CR}.{ext_actual}\n"
            f"<b>│  Res</b>   {res}\n"
            f"<b>│  Date</b>  {date_str}\n"
            f"<b>│</b>\n"
            f"<b>├──────────────────────┤</b>\n"
            f"<b>│  {CR}</b>\n"
            f"<b>└──────────────────────┘</b>\n"
            f"\n<i>{time_str}</i>\n"
        )
    elif style == "ultra_clean":
        return (
            f"\n<b>── ✦ ── ✦ ── ✦ ──</b>\n"
            f"<b>  VIDEO</b>\n"
            f"<b>── ✦ ── ✦ ── ✦ ──</b>\n\n"
            f"  ID    : {str(count).zfill(3)}\n"
            f"  Batch : {plain_batch}\n"
            f"  Title : {name1}\n"
            f"  Ext   : {CR}.{ext_actual}\n"
            f"  Res   : {res}\n"
            f"  Date  : {date_str}\n\n"
            f"<b>── ✦ ── ✦ ── ✦ ──</b>\n"
            f"<i>{time_str}</i>\n"
            f"<b>  {CR}</b>\n"
        )
    else:
        return (
            f"\n<b>🧭 Index ID:</b> {str(count).zfill(3)}\n\n"
            f"<b>📎 Batch:</b> {plain_batch}\n\n"
            f"<b>📥 Title:</b> {name1}\n\n"
            f"[{date_str}]\n\n"
            f"<b>📤 Extension:</b> {CR}.{ext_actual}\n"
            f"<b>🧩 Resolution:</b> {res}\n\n"
            f"<b>🍁 Uploaded By:</b> {CR}\n\n"
            f"{time_str}\n"
        )

# ========================= SETTINGS SYSTEM =========================

def get_user_settings(user_id: int, bot_username: str = None) -> dict:
    if bot_username is None:
        bot_username = bot.me.username
    settings = db.get_user_settings(user_id, bot_username)
    final = DEFAULT_SETTINGS.copy()
    final.update(settings)
    return final

def update_setting(user_id: int, key: str, value, bot_username: str = None):
    if bot_username is None:
        bot_username = bot.me.username
    db.update_user_setting(user_id, bot_username, key, value)

def settings_menu_markup(user_id: int) -> InlineKeyboardMarkup:
    settings = get_user_settings(user_id)
    buttons = []
    status = lambda key: "✅" if settings.get(key) else "❌"
    buttons.append([InlineKeyboardButton(f"Auto Upload {status('auto_upload')}", callback_data="set_auto_upload_toggle")])
    buttons.append([InlineKeyboardButton(f"Batch Upload {status('batch_upload')}", callback_data="set_batch_upload_toggle")])
    buttons.append([InlineKeyboardButton(f"Resume Interrupted {status('resume')}", callback_data="set_resume_toggle")])
    buttons.append([InlineKeyboardButton(f"Downloader Name: {settings['downloader_name'][:10]}", callback_data="set_downloader_name")])
    buttons.append([InlineKeyboardButton(f"Show Extension {status('show_extension')}", callback_data="set_show_extension_toggle")])
    
    current_style = settings.get('caption_style', 'bracket_style')
    display_name = STYLE_DISPLAY_NAMES.get(current_style, current_style)
    buttons.append([InlineKeyboardButton(f"🎨 Caption Style: {display_name}", callback_data="set_caption_style")])
    
    buttons.append([InlineKeyboardButton(f"Show Title {status('show_title')}", callback_data="set_show_title_toggle")])
    buttons.append([InlineKeyboardButton(f"Quality: {settings['quality']}p", callback_data="set_quality")])
    buttons.append([InlineKeyboardButton(f"Thumbnail: {'Custom' if settings['thumbnail']!='default' else 'Default'}", callback_data="set_thumbnail")])
    buttons.append([InlineKeyboardButton(f"PDF Watermark {status('pdf_watermark')}", callback_data="set_pdf_watermark_toggle")])
    buttons.append([InlineKeyboardButton(f"Auto Grouping {status('auto_grouping')}", callback_data="set_auto_grouping_toggle")])
    buttons.append([InlineKeyboardButton(f"Video Player Link {status('video_player_link')}", callback_data="set_video_player_link_toggle")])
    buttons.append([InlineKeyboardButton(f"PW Token: {'set' if settings['pw_token'] else 'not set'}", callback_data="set_pw_token")])
    buttons.append([InlineKeyboardButton(f"Proxy: {'set' if settings['proxy'] else 'not set'}", callback_data="set_proxy")])
    buttons.append([InlineKeyboardButton("📂 Manage Subject Groups", callback_data="set_subject_groups")])
    buttons.append([InlineKeyboardButton("Manage Database", callback_data="set_db_info")])
    buttons.append([InlineKeyboardButton(f"Sticker Responses {status('sticker_responses')}", callback_data="set_sticker_responses_toggle")])
    buttons.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command("setting") & filters.private)
async def settings_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    await message.reply_text(
        "⚙️ **Settings Menu**\n\nChoose an option to modify:",
        reply_markup=settings_menu_markup(user_id)
    )

@bot.on_callback_query()
async def settings_callback(client: Client, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id
    bot_username = client.me.username
    settings = get_user_settings(user_id, bot_username)

    if data.endswith("_toggle"):
        key = data.replace("set_", "").replace("_toggle", "")
        current = settings.get(key, False)
        update_setting(user_id, key, not current, bot_username)
        await query.answer(f"✅ {key.replace('_',' ').title()} set to {not current}")
        await query.message.edit_text(
            "⚙️ **Settings Menu**\n\nChoose an option to modify:",
            reply_markup=settings_menu_markup(user_id)
        )
        return

    if data == "set_downloader_name":
        await query.answer()
        msg = await query.message.reply_text("✏️ Send the new name (or /cancel):")
        try:
            input_msg: Message = await client.listen(msg.chat.id, timeout=30)
            if input_msg.text and input_msg.text != "/cancel":
                update_setting(user_id, "downloader_name", input_msg.text.strip(), bot_username)
                await input_msg.delete()
                await msg.edit_text("✅ Downloader name updated!")
                await query.message.edit_text(
                    "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                    reply_markup=settings_menu_markup(user_id)
                )
            else:
                await msg.edit_text("❌ Cancelled.")
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "set_caption_style":
        buttons = []
        for style in ALL_STYLES:
            check = " ✅" if settings.get("caption_style") == style else ""
            display_name = STYLE_DISPLAY_NAMES.get(style, style)
            buttons.append([InlineKeyboardButton(f"{display_name}{check}", callback_data=f"set_caption_style_{style}")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.message.edit_text(
            "🎨 **Select Caption Style:**\n\n"
            "<i>Choose how video captions should look.</i>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if data.startswith("set_caption_style_"):
        style = data.replace("set_caption_style_", "")
        if style in ALL_STYLES:
            update_setting(user_id, "caption_style", style, bot_username)
            display_name = STYLE_DISPLAY_NAMES.get(style, style)
            await query.answer(f"✅ Caption style set to {display_name}")
            await query.message.edit_text(
                "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                reply_markup=settings_menu_markup(user_id)
            )
        return

    if data == "set_quality":
        qualities = ["144", "240", "360", "480", "720", "1080"]
        buttons = []
        for q in qualities:
            check = " ✅" if settings.get("quality") == q else ""
            buttons.append([InlineKeyboardButton(f"{q}p{check}", callback_data=f"set_quality_{q}")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.message.edit_text(
            "📐 **Select Upload Quality:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if data.startswith("set_quality_"):
        q = data.replace("set_quality_", "")
        qualities = ["144", "240", "360", "480", "720", "1080"]
        if q in qualities:
            update_setting(user_id, "quality", q, bot_username)
            await query.answer(f"Quality set to {q}p")
            await query.message.edit_text(
                "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                reply_markup=settings_menu_markup(user_id)
            )
        return

    if data == "set_thumbnail":
        await query.answer()
        msg = await query.message.reply_text("🖼️ Send a photo, /default, or /cancel:")
        try:
            input_msg: Message = await client.listen(msg.chat.id, timeout=30)
            if input_msg.photo:
                file_path = f"downloads/thumb_{user_id}.jpg"
                await client.download_media(input_msg.photo, file_name=file_path)
                update_setting(user_id, "thumbnail", file_path, bot_username)
                await msg.edit_text("✅ Thumbnail updated!")
                await query.message.edit_text(
                    "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                    reply_markup=settings_menu_markup(user_id)
                )
            elif input_msg.text == "/default":
                update_setting(user_id, "thumbnail", "default", bot_username)
                await msg.edit_text("✅ Reset to default.")
                await query.message.edit_text(
                    "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                    reply_markup=settings_menu_markup(user_id)
                )
            elif input_msg.text == "/cancel":
                await msg.edit_text("❌ Cancelled.")
            else:
                await msg.edit_text("❌ Invalid input.")
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "set_pw_token":
        await query.answer()
        msg = await query.message.reply_text("🔑 Send new PW token (or /cancel):")
        try:
            input_msg: Message = await client.listen(msg.chat.id, timeout=30)
            if input_msg.text and input_msg.text != "/cancel":
                update_setting(user_id, "pw_token", input_msg.text.strip(), bot_username)
                await msg.edit_text("✅ PW Token updated!")
                await query.message.edit_text(
                    "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                    reply_markup=settings_menu_markup(user_id)
                )
            else:
                await msg.edit_text("❌ Cancelled.")
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "set_proxy":
        await query.answer()
        msg = await query.message.reply_text("🌐 Send proxy URL (or /cancel):")
        try:
            input_msg: Message = await client.listen(msg.chat.id, timeout=30)
            if input_msg.text and input_msg.text != "/cancel":
                update_setting(user_id, "proxy", input_msg.text.strip(), bot_username)
                await msg.edit_text("✅ Proxy updated!")
                await query.message.edit_text(
                    "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                    reply_markup=settings_menu_markup(user_id)
                )
            else:
                await msg.edit_text("❌ Cancelled.")
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "set_db_info":
        try:
            status = "✅ Connected" if db.client is not None else "❌ Disconnected"
            await query.answer(f"Database: {status}")
            await query.message.reply_text(f"📊 **Database Status**\n\nStatus: {status}\nDatabase: {DATABASE_NAME}")
        except Exception as e:
            await query.message.reply_text(f"❌ DB Error: {str(e)}")
        return

    if data == "set_subject_groups":
        groups = db.get_subject_groups(user_id, bot_username)
        text = "📂 **Subject Groups**\n\n"
        if groups:
            for subject, chat_id in groups.items():
                text += f"• {subject} → `{chat_id}`\n"
        else:
            text += "No groups configured.\n"
        text += f"\nDefault Group: `{db.get_default_group(user_id, bot_username) or 'Not set'}`\n\n"
        text += "Use buttons below."
        buttons = [
            [InlineKeyboardButton("➕ Add New Group", callback_data="add_subject_group")],
            [InlineKeyboardButton("🗑️ Remove Group", callback_data="remove_subject_group")],
            [InlineKeyboardButton("📌 Set Default Group", callback_data="set_default_group")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data == "add_subject_group":
        await query.answer()
        msg = await query.message.reply_text("✏️ Send **Subject Name** (e.g., 'Mathematics'):")
        try:
            input1: Message = await client.listen(msg.chat.id, timeout=30)
            if not input1.text or input1.text == "/cancel":
                await msg.edit_text("❌ Cancelled.")
                return
            subject = input1.text.strip()
            await input1.delete()
            await msg.edit_text(f"📤 Now send the **Chat ID** (or forward a message):")
            input2: Message = await client.listen(msg.chat.id, timeout=30)
            if input2.forward_from_chat:
                chat_id = input2.forward_from_chat.id
            elif input2.text and input2.text.lstrip('-').isdigit():
                chat_id = int(input2.text.strip())
            else:
                await msg.edit_text("❌ Invalid chat ID.")
                return
            if db.add_subject_group(user_id, bot_username, subject, chat_id):
                await msg.edit_text(f"✅ Added: {subject} → `{chat_id}`")
            else:
                await msg.edit_text("❌ Failed.")
            await query.message.edit_text(
                "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                reply_markup=settings_menu_markup(user_id)
            )
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "remove_subject_group":
        groups = db.get_subject_groups(user_id, bot_username)
        if not groups:
            await query.answer("No groups.")
            return
        buttons = []
        for subject in groups.keys():
            buttons.append([InlineKeyboardButton(f"🗑️ {subject}", callback_data=f"remove_group_{subject}")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="set_subject_groups")])
        await query.message.edit_text("Select subject to remove:", reply_markup=InlineKeyboardMarkup(buttons))
        return

    if data.startswith("remove_group_"):
        subject = data.replace("remove_group_", "")
        if db.remove_subject_group(user_id, bot_username, subject):
            await query.answer(f"Removed {subject}")
        else:
            await query.answer("Failed.")
        await query.message.edit_text(
            "⚙️ **Settings Menu**\n\nChoose an option to modify:",
            reply_markup=settings_menu_markup(user_id)
        )
        return

    if data == "set_default_group":
        await query.answer()
        msg = await query.message.reply_text("📌 Send Chat ID (or forward):")
        try:
            input_msg: Message = await client.listen(msg.chat.id, timeout=30)
            if input_msg.forward_from_chat:
                chat_id = input_msg.forward_from_chat.id
            elif input_msg.text and input_msg.text.lstrip('-').isdigit():
                chat_id = int(input_msg.text.strip())
            else:
                await msg.edit_text("❌ Invalid.")
                return
            if db.set_default_group(user_id, bot_username, chat_id):
                await msg.edit_text(f"✅ Default group set to `{chat_id}`")
            else:
                await msg.edit_text("❌ Failed.")
            await query.message.edit_text(
                "⚙️ **Settings Menu**\n\nChoose an option to modify:",
                reply_markup=settings_menu_markup(user_id)
            )
        except asyncio.TimeoutError:
            await msg.edit_text("⏰ Timeout.")
        return

    if data == "main_menu":
        await query.message.edit_text(
            "⚙️ **Settings Menu**\n\nChoose an option:",
            reply_markup=settings_menu_markup(user_id)
        )
        return

    # If not handled, pass to ram callback
    await ram_callback_handler(client, query)

# ========================= RAM.PY COMMAND HANDLERS =========================

@bot.on_message(filters.command("extract") & filters.private)
async def extract_cmd(client: Client, message: Message):
    user = message.from_user
    if not is_ram_authorized(user.id):
        await message.reply_text(f"🚫 <b>Access Denied!</b>\n\nApki User ID <code>{user.id}</code> 🤡", parse_mode="html")
        return

    await message.reply_photo(photo=EXTRACT_THUMBNAIL, caption="⏳ <b>Fetching Batches...</b> 🔎", parse_mode="html")
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            data = await fetch_with_retry(session, f"{API_BASE}/courses/")
            if data is None:
                await message.reply_text("❌ API Error! Please try again later. 😵‍💫")
                return
            batches = data.get("data", [])
            if not batches:
                await message.reply_text("⚠️ No batches found. 🥲")
                return
            uid = user.id
            ram_user_data[uid] = {
                'all_batches': batches,
                'batch_map': {str(b['id']): b['title'] for b in batches}
            }
            header = f"📚 <b>Available Batches</b> 📂\n━━━━━━━━━━━━━━━━━━━━━━\nSelect a batch to extract its content.\n━━━━━━━━━━━━━━━━━━━━━━\n"
            kb = []
            for b in batches:
                kb.append([InlineKeyboardButton(f"📁 {b['title'][:40]}", callback_data=f"sel_{b['id']}")])
            kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_extract")])
            await message.reply_text(header, reply_markup=InlineKeyboardMarkup(kb), parse_mode="html")
    except Exception as e:
        logging.exception("Extract error")
        await message.reply_text(f"❌ Error: {str(e)} 😵‍💫")

@bot.on_message(filters.command("cw") & filters.private)
async def cw_cmd(client: Client, message: Message):
    user = message.from_user
    if not is_ram_authorized(user.id):
        await message.reply_text(f"🚫 <b>Access Denied!</b>\n\nApki User ID <code>{user.id}</code> 🤡", parse_mode="html")
        return
    await message.reply_text("⏳ Database fetching CW batches... 🛢️")
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            data = await fetch_with_retry(session, CW_ALL_BATCHES)
            if data is None:
                await message.reply_text("❌ Failed to fetch batches after multiple attempts.\nPlease check the endpoint or try later. 🫠")
                return
            txt_content = f"{BANNER_LINE}\n         CW OFFICIAL BATCHES LIST\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            nested_data = data.get('data') if isinstance(data, dict) and 'data' in data else data
            if isinstance(nested_data, dict):
                for index, (b_id, b_name) in enumerate(nested_data.items(), 1):
                    txt_content += f"{index}. BATCH NAME : {b_name}\n   BATCH ID   : {b_id}\n{'-'*40}\n"
            elif isinstance(nested_data, list):
                for item in nested_data:
                    b_id = item.get('id') or item.get('batchId') or 'N/A'
                    b_name = item.get('name') or item.get('batchName') or 'Unknown'
                    txt_content += f"BATCH NAME : {b_name}\n   BATCH ID   : {b_id}\n{'-'*40}\n"
            else:
                txt_content += "⚠️ Unexpected data format. Raw:\n" + str(nested_data)[:200]
            file_buffer = io.BytesIO(txt_content.encode('utf-8'))
            await message.reply_document(
                document=file_buffer,
                filename="CW_Available_Batches.txt",
                caption="📋 CW ke sabhi available batches ki list tayar hai. 📜\n\n💡 Batch content extract karne ke liye mujhe direct <b>Batch ID</b> send karein. 🎯",
                parse_mode="html"
            )
    except Exception as e:
        logging.exception("CW command error")
        await message.reply_text(f"❌ Unexpected error: {str(e)} 😵‍💫")

# ---------- CW BATCH ID HANDLER (now without ~filters.command) ----------
@bot.on_message(filters.text & filters.private)
async def handle_cw_batch_id(client: Client, message: Message):
    # Ignore if it's a command
    if message.text and message.text.startswith('/'):
        return
    user = message.from_user
    if not is_ram_authorized(user.id):
        return
    text = message.text.strip()
    if not re.match(r'^[A-Za-z0-9_-]{5,30}$', text):
        return
    if re.search(r'https?://', text):
        return

    batch_id = text
    status_msg = await message.reply_text(f"🔍 Processing CW Batch ID: {batch_id}... Fast Async Engine active. ⚡")
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            topics_data = await fetch_with_retry(session, CW_BATCH_API.format(batch_id))
            if topics_data is None:
                await status_msg.edit_text("❌ Batch list fetch failed after retries. Check the batch ID or endpoint. 🫠")
                return
            batch_details = topics_data.get('data', topics_data) if isinstance(topics_data, dict) else topics_data
            batch_name = batch_details.get('batchName') or batch_details.get('name') or f"Batch_{batch_id}"
            topics = batch_details.get('topics', []) if isinstance(batch_details, dict) else batch_details
            if not isinstance(topics, list) or not topics:
                await status_msg.edit_text("⚠️ No topics found in this batch. 🥲")
                return
            await status_msg.edit_text(f"📂 Total {len(topics)} Topics found.\n⚡ Extracting content asynchronously... 🤖")
            txt_content = f"{BANNER_LINE}\n👤 Extracted By: {user.first_name}\n📛 BATCH: {batch_name.upper()}\n🆔 ID: {batch_id}\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
            topic_tasks = [extract_topic_content(session, batch_id, topic, idx) for idx, topic in enumerate(topics, 1)]
            topic_results = await asyncio.gather(*topic_tasks, return_exceptions=True)
            total_videos_all, total_pdfs_all = 0, 0
            for result in topic_results:
                if isinstance(result, Exception):
                    logging.error(f"Topic extraction error: {result}")
                    continue
                text_part, v_c, p_c = result
                txt_content += text_part
                total_videos_all += v_c
                total_pdfs_all += p_c
            summary_text = (
                f"✨ <b>{STYLISH_NAME}</b>\n\n"
                f"✅ <b>Extraction Complete!</b>\n\n"
                f"📄 <b>Batch:</b> {batch_name}\n"
                f"📹 <b>Total Videos:</b> {total_videos_all}\n"
                f"📑 <b>Total PDFs:</b> {total_pdfs_all}"
            )
            filename = f"_քǟռɖɛʏ_ʝɨ_{sanitize_filename(batch_name)}.txt"
            file_buffer = io.BytesIO(txt_content.encode('utf-8'))
            await message.reply_document(
                document=file_buffer,
                filename=filename,
                caption=summary_text,
                parse_mode="html"
            )
            await status_msg.delete()
    except Exception as e:
        logging.exception("CW batch extraction error")
        await status_msg.edit_text(f"❌ Error occurred: {str(e)} 😵‍💫")

@bot.on_message(filters.command("careerwill") & filters.private)
async def careerwill_cmd(client: Client, message: Message):
    user = message.from_user
    if not is_ram_authorized(user.id):
        await message.reply_text("🚫 <b>Access Denied!</b> 🤡", parse_mode="html")
        return

    msg = await message.reply_text("⏳ Fetching Careerwill batches... 🧭")
    try:
        global CAREERWILL_BASE, CAREERWILL_BATCHES, CAREERWILL_BATCH_DETAIL
        async with aiohttp.ClientSession(headers=CAREERWILL_HEADERS) as session:
            data = await fetch_with_retry(session, CAREERWILL_BATCHES)
            if data is None:
                build_id = await get_careerwill_build_id()
                if build_id:
                    CAREERWILL_BASE = f"https://web.careerwill.com/_next/data/{build_id}"
                    CAREERWILL_BATCHES = f"{CAREERWILL_BASE}/live-classes.json?view=List&interface_id=1"
                    CAREERWILL_BATCH_DETAIL = f"{CAREERWILL_BASE}/live-classes/{{}}.json?interface_id=1"
                    data = await fetch_with_retry(session, CAREERWILL_BATCHES)
                if data is None:
                    await msg.edit_text("❌ Failed to fetch Careerwill batches. Please check build ID or try later. 🫠")
                    return

        live_classes = data.get("pageProps", {}).get("liveClasses", [])
        if not live_classes:
            await msg.edit_text("⚠️ No batches found. 🥲")
            return

        uid = user.id
        ram_user_data[uid] = {
            'careerwill_batches': live_classes,
            'careerwill_batch_map': {str(b['id']): b['batchName'] for b in live_classes}
        }

        kb = []
        for batch in live_classes[:20]:
            btn_text = f"📁 {batch['batchName'][:35]}"
            kb.append([InlineKeyboardButton(btn_text, callback_data=f"cw_batch_{batch['id']}")])

        kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_extract")])

        await msg.edit_text(
            f"📚 <b>Careerwill Batches</b> 📚\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Total: {len(live_classes)} batches\n"
            f"Select a batch to extract videos.\n"
            f"━━━━━━━━━━━━━━━━━━━━━━",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="html"
        )
    except Exception as e:
        logging.exception("Careerwill error")
        await msg.edit_text(f"❌ Error: {str(e)} 😵‍💫")

@bot.on_message(filters.command("html") & filters.private)
async def html_cmd(client: Client, message: Message):
    uid = message.from_user.id
    if uid in ram_user_data:
        ram_user_data[uid].pop('split_mode', None)
        ram_user_data[uid].pop('split_data', None)
        ram_user_data[uid].pop('split_current_page', None)
    await message.reply_text("📂 Ab wo <b>.txt</b> file bhejein jise HTML mein convert karna hai. 🤔🎨", parse_mode="html")

@bot.on_message(filters.command("split") & filters.private)
async def split_cmd(client: Client, message: Message):
    user = message.from_user
    if not is_ram_authorized(user.id):
        await message.reply_text("🚫 <b>Access Denied!</b> 🤡", parse_mode="html")
        return
    uid = user.id
    if uid not in ram_user_data:
        ram_user_data[uid] = {}
    ram_user_data[uid]['split_mode'] = True
    await message.reply_text(
        "📂 Ab wo <b>.txt</b> file bhejein. 🤔\n\n"
        "✅ I Will split your txt 🌻 topic wise 🎞️",
        parse_mode="html"
    )

@bot.on_message(filters.document & filters.private)
async def handle_txt_file(client: Client, message: Message):
    doc = message.document
    if not doc or not doc.file_name.lower().endswith('.txt'):
        return

    user = message.from_user
    uid = user.id

    if uid in ram_user_data and ram_user_data[uid].get('split_mode', False):
        await handle_split_txt(client, message, doc)
        return

    await handle_txt_to_html(client, message, doc)

async def handle_txt_to_html(client: Client, message: Message, doc):
    msg = await message.reply_text("⏳ Processing HTML... 🎨🖌️")
    raw_name = doc.file_name.replace(".txt", "").replace(".html", "")
    html_name = f"•{sanitize_filename(raw_name)}.html"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_in:
            bot_file = await client.download_media(doc, file_name=tmp_in.name)
            tmp_in_path = tmp_in.name

        subjects = {}
        total_videos = 0
        total_pdfs = 0

        with open(tmp_in_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if "http" in line:
                    parts = line.split(" : ", 1) if " : " in line else line.split(":", 1)
                    if len(parts) < 2: continue
                    title, url = parts[0].strip(), parts[1].strip()
                    sub_name = title.split(']')[0].replace('[', '').strip() if "[" in title and "]" in title else "General"
                    if sub_name not in subjects:
                        subjects[sub_name] = []
                    is_pdf = ".pdf" in url.lower() or "drive.google.com" in url.lower()
                    if is_pdf:
                        total_pdfs += 1
                    else:
                        total_videos += 1
                    subjects[sub_name].append({'t': title, 'u': url})

        body_html = f"""
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                document.getElementById('statSubjects').textContent = '{len(subjects)}';
                document.getElementById('statVideos').textContent = '{total_videos}';
                document.getElementById('statPdfs').textContent = '{total_pdfs}';
                document.getElementById('statTotal').textContent = '{total_videos + total_pdfs}';
                document.getElementById('totalItems').innerHTML = '<i class="fas fa-layer-group"></i> {total_videos + total_pdfs} Items';
            }});
        </script>
        """

        for i, (s_name, items) in enumerate(subjects.items()):
            sid = f"sub_{i}"
            body_html += f"""
            <div class="card">
                <div class="accordion-header" onclick="toggleAccordion('{sid}')">
                    <span class="left">
                        <i class="fas fa-folder-open"></i>
                        {s_name}
                        <span class="badge">{len(items)}</span>
                    </span>
                    <span class="icon" id="icon_{sid}">
                        <i class="fas fa-chevron-down"></i>
                    </span>
                </div>
                <div id="{sid}" class="accordion-content">
            """
            for itm in items:
                link, name = itm['u'], itm['t']
                is_pdf = ".pdf" in link.lower() or "drive.google.com" in link.lower()
                is_vid = is_video_link(link)

                body_html += f"""
                    <div class="item">
                        <div class="item-title">
                            <i class="fas fa-file-alt"></i>
                            <span>{name}</span>
                        </div>
                """
                if is_vid:
                    embed_html = get_video_embed_html(link, name)
                    if embed_html:
                        body_html += embed_html
                body_html += """
                        <div class="item-actions">
                """
                if is_pdf:
                    body_html += f'<a href="{link}" class="btn btn-pdf" target="_blank"><i class="fas fa-file-pdf"></i> View PDF</a>'
                else:
                    body_html += f'<a href="{link}" class="btn btn-watch" target="_blank"><i class="fas fa-play"></i> Watch</a>'
                    body_html += f'<a href="{link}" class="btn btn-download" download><i class="fas fa-download"></i> Download</a>'
                body_html += """
                        </div>
                    </div>
                """
            body_html += "</div></div>"

        html_footer = """
    </div>

    <script>
        function toggleAccordion(id) {
            const content = document.getElementById(id);
            const icon = document.getElementById('icon_' + id);
            const header = content.previousElementSibling;

            if (content.classList.contains('active')) {
                content.classList.remove('active');
                icon.classList.remove('rotated');
                header.classList.remove('active');
            } else {
                content.classList.add('active');
                icon.classList.add('rotated');
                header.classList.add('active');
            }
        }

        function expandAll() {
            document.querySelectorAll('.accordion-content').forEach(el => {
                el.classList.add('active');
                const id = el.id;
                const icon = document.getElementById('icon_' + id);
                const header = el.previousElementSibling;
                if (icon) icon.classList.add('rotated');
                if (header) header.classList.add('active');
            });
            showToast('✅ All sections expanded!', 'success');
        }

        function collapseAll() {
            document.querySelectorAll('.accordion-content').forEach(el => {
                el.classList.remove('active');
                const id = el.id;
                const icon = document.getElementById('icon_' + id);
                const header = el.previousElementSibling;
                if (icon) icon.classList.remove('rotated');
                if (header) header.classList.remove('active');
            });
            showToast('📦 All sections collapsed!', 'success');
        }

        function copyAllContent() {
            const items = document.querySelectorAll('.item');
            let text = '';
            let count = 0;
            items.forEach(item => {
                const title = item.querySelector('.item-title span')?.innerText || '';
                const links = item.querySelectorAll('.item-actions a');
                let actions = [];
                links.forEach(a => {
                    const label = a.innerText.trim();
                    const href = a.href;
                    actions.push(label + ': ' + href);
                });
                if (title) text += title + '\\n';
                if (actions.length) text += actions.join('\\n') + '\\n\\n';
                count++;
            });

            navigator.clipboard.writeText(text).then(() => {
                showToast('✅ ' + count + ' items copied to clipboard!', 'success');
            }).catch(() => {
                showToast('❌ Failed to copy. Please copy manually.', 'error');
            });
        }

        function copyLinksOnly() {
            const links = document.querySelectorAll('.item-actions a');
            let text = '';
            let count = 0;
            links.forEach(a => {
                const label = a.innerText.trim();
                const href = a.href;
                text += label + ': ' + href + '\\n';
                count++;
            });

            navigator.clipboard.writeText(text).then(() => {
                showToast('✅ ' + count + ' links copied!', 'success');
            }).catch(() => {
                showToast('❌ Failed to copy links.', 'error');
            });
        }

        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            const toastMsg = document.getElementById('toastMessage');
            const icon = toast.querySelector('i');

            toastMsg.textContent = message;
            toast.className = 'toast ' + type;
            icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';

            toast.classList.add('show');
            clearTimeout(toast._timeout);
            toast._timeout = setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        window.addEventListener('scroll', function() {
            const btn = document.getElementById('scrollTopBtn');
            if (window.scrollY > 300) {
                btn.classList.add('visible');
            } else {
                btn.classList.remove('visible');
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                expandAll();
            }
            if (e.ctrlKey && e.key === 'c') {
                e.preventDefault();
                collapseAll();
            }
            if (e.ctrlKey && e.key === 'a') {
                e.preventDefault();
                copyAllContent();
            }
        });
    </script>
</body>
</html>
"""

        full_html = HTML_HEADER + body_html + html_footer
        with open(html_name, 'w', encoding='utf-8') as hf:
            hf.write(full_html)

        await message.reply_document(
            document=html_name,
            caption=f"✨ <b>{STYLISH_NAME}</b>\n✅ HTML Conversion Successful! 🥳",
            parse_mode="html"
        )
        await msg.delete()
    except Exception as e:
        logging.exception("HTML conversion error")
        await message.reply_text(f"❌ Error: {str(e)} 😵‍💫")
    finally:
        if os.path.exists(tmp_in_path): os.remove(tmp_in_path)
        if os.path.exists(html_name): os.remove(html_name)

async def handle_split_txt(client: Client, message: Message, doc):
    user = message.from_user
    uid = user.id
    msg = await message.reply_text("⏳ Analyzing file and extracting subjects... 🤖⚡")

    original_filename = doc.file_name
    base_name = os.path.splitext(original_filename)[0]
    sanitized_base = sanitize_filename(base_name)

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_in:
            bot_file = await client.download_media(doc, file_name=tmp_in.name)
            tmp_in_path = tmp_in.name

        groups_dict = {}

        with open(tmp_in_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                line = line.strip()
                if not line or "http" not in line:
                    continue

                parts = re.split(r'\s*:\s*', line, 1)
                if len(parts) < 2:
                    continue

                title, url = parts[0].strip(), parts[1].strip()

                subject = "General"
                if '[' in title and ']' in title:
                    bracket_content = title.split(']', 1)[0].replace('[', '').strip()
                    subject_parts = re.split(r'[-|,;_]', bracket_content)
                    subject = subject_parts[0].strip()
                    if not subject:
                        subject = "General"
                else:
                    subject = "General"

                subject = re.sub(r'^[^\w\s]+', '', subject).strip()
                if not subject:
                    subject = "General"

                norm_key = re.sub(r'\s+', '_', subject.strip())

                if norm_key not in groups_dict:
                    groups_dict[norm_key] = {
                        'subject': subject,
                        'lines': [],
                        'videos': 0,
                        'pdfs': 0
                    }

                is_pdf = (
                    ".pdf" in url.lower() or
                    "/file/d/" in url.lower() or
                    "drive.google.com" in url.lower() or
                    "docs.google.com" in url.lower()
                )

                if is_pdf:
                    groups_dict[norm_key]['pdfs'] += 1
                else:
                    groups_dict[norm_key]['videos'] += 1

                groups_dict[norm_key]['lines'].append(line)

        if not groups_dict:
            await msg.edit_text("❌ No valid entries found in the TXT file. 💀", parse_mode="html")
            return

        groups_list = list(groups_dict.values())
        total_subjects = len(groups_list)

        ram_user_data[uid] = {
            'split_data': {
                'groups': groups_list,
                'selected': [True] * total_subjects,
                'base_name': sanitized_base,
                'original_filename': original_filename
            },
            'split_current_page': 0
        }

        await display_split_menu(client, message, msg, page=0)

    except Exception as e:
        logging.exception("Split error")
        await message.reply_text(f"❌ Error: {str(e)} 😵‍💫")
    finally:
        if os.path.exists(tmp_in_path):
            os.remove(tmp_in_path)

async def display_split_menu(client: Client, message: Message, status_msg=None, page=0):
    uid = message.from_user.id
    data = ram_user_data.get(uid, {}).get('split_data')
    if not data:
        return

    groups = data['groups']
    selected = data['selected']
    total_subjects = len(groups)

    ITEMS_PER_PAGE = 8
    total_pages = (total_subjects + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_idx = page * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_subjects)

    keyboard = []

    for idx in range(start_idx, end_idx):
        group = groups[idx]
        subject = group['subject']
        total_count = group['videos'] + group['pdfs']
        icon = "✅" if selected[idx] else "🔲"
        btn_text = f"{icon} {subject} ({total_count})"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"split_toggle_{idx}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"split_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="split_ignore"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"split_page_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([
        InlineKeyboardButton("✅ Select All", callback_data="split_select_all"),
        InlineKeyboardButton("❌ Deselect All", callback_data="split_deselect_all")
    ])
    keyboard.append([InlineKeyboardButton("📨 Done", callback_data="split_done")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    header_text = (
        f"🟢 <b>Subjects Extracted Successfully !</b> 🥳🎯\n"
        f"🗂️ Total Subjects (Folders): {total_subjects}\n"
        f"📝 Total Items: {sum(len(g['lines']) for g in groups)}\n\n"
        f"👉 <b>Select Subjects from below Buttons :</b> 🧩"
    )

    if status_msg:
        await status_msg.edit_text(header_text, reply_markup=reply_markup, parse_mode="html")
    else:
        await message.edit_text(header_text, reply_markup=reply_markup, parse_mode="html")

# ---------- RAM CALLBACK HANDLER ----------
async def ram_callback_handler(client: Client, query: CallbackQuery):
    user = query.from_user
    uid = user.id
    data = query.data

    # Split callbacks
    if data.startswith("split_toggle_"):
        idx = int(data.split("_")[2])
        split_data = ram_user_data.get(uid, {}).get('split_data')
        if split_data:
            split_data['selected'][idx] = not split_data['selected'][idx]
            current_page = ram_user_data.get(uid, {}).get('split_current_page', 0)
            await display_split_menu(client, query.message, page=current_page)
            await query.answer()
        return

    if data == "split_select_all":
        split_data = ram_user_data.get(uid, {}).get('split_data')
        if split_data:
            for i in range(len(split_data['selected'])):
                split_data['selected'][i] = True
            current_page = ram_user_data.get(uid, {}).get('split_current_page', 0)
            await display_split_menu(client, query.message, page=current_page)
            await query.answer()
        return

    if data == "split_deselect_all":
        split_data = ram_user_data.get(uid, {}).get('split_data')
        if split_data:
            for i in range(len(split_data['selected'])):
                split_data['selected'][i] = False
            current_page = ram_user_data.get(uid, {}).get('split_current_page', 0)
            await display_split_menu(client, query.message, page=current_page)
            await query.answer()
        return

    if data.startswith("split_page_"):
        page = int(data.split("_")[2])
        ram_user_data[uid]['split_current_page'] = page
        await display_split_menu(client, query.message, page=page)
        await query.answer()
        return

    if data == "split_ignore":
        await query.answer()
        return

    if data == "split_done":
        split_data = ram_user_data.get(uid, {}).get('split_data')
        if not split_data:
            await query.edit_message_text("⚠️ Session expired. Please use /split command again. 💀")
            await query.answer()
            return

        selected_indices = [i for i, s in enumerate(split_data['selected']) if s]
        if not selected_indices:
            await query.answer("⚠️ Koi subject select nahi kiya gaya. Please select at least one subject. 🫣", show_alert=True)
            return

        await query.edit_message_text("⏳ Generating selected files... Please wait. 🤞✨")

        base_name = split_data['base_name']
        original_filename = split_data['original_filename']

        for idx in selected_indices:
            group = split_data['groups'][idx]
            subject = group['subject']
            lines = group['lines']
            video_count = group['videos']
            pdf_count = group['pdfs']
            total = len(lines)

            content = "\n".join(lines)
            file_buffer = io.BytesIO(content.encode('utf-8'))

            filename = f"{base_name}_{sanitize_filename(subject)}.txt"
            display_name = subject

            caption = (
                f"📂 <b>{display_name}</b> (<code>{original_filename}</code>)\n"
                f"📦 Total: {total}\n"
                f"🎥 Videos: {video_count}\n"
                f"📄 PDFs: {pdf_count}"
            )

            await query.message.reply_document(
                document=file_buffer,
                filename=filename,
                caption=caption,
                parse_mode="html"
            )
            await asyncio.sleep(0.3)

        await query.message.reply_text(
            f"✅ Split Complete! 🎉\n"
            f"📁 Total Files Generated: {len(selected_indices)} 🤌\n"
            f"✨ {STYLISH_NAME}",
            parse_mode="html"
        )

        ram_user_data[uid].pop('split_data', None)
        ram_user_data[uid].pop('split_current_page', None)
        ram_user_data[uid]['split_mode'] = False
        await query.edit_message_text("✅ Done! Files sent above. 🚀")
        await query.answer()
        return

    # Extract / Careerwill callbacks
    if data.startswith("sel_"):
        if not is_ram_authorized(uid):
            await query.answer("🚫 Access Denied!", show_alert=True)
            return
        await query.answer()
        b_id = data.split("_")[1]
        b_name = ram_user_data.get(uid, {}).get('batch_map', {}).get(b_id, "Batch")
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                batch_data = await fetch_with_retry(session, f"{API_BASE}/courses/{b_id}/classes?populate=full")
                if batch_data is None:
                    await query.edit_message_text("❌ Error loading batch details. 🫠")
                    return
                topics = batch_data.get("data", {}).get("classes", [])
                v_count = 0
                p_count = 0
                for t in topics:
                    for cls in t.get("classes", []):
                        if cls.get('class_link'):
                            v_count += 1
                        if cls.get("classPdf"):
                            p_count += len(cls.get("classPdf", []))
                ram_user_data[uid].update({
                    'curr_topics': topics,
                    'curr_batch_name': b_name,
                    'curr_batch_id': b_id,
                    'curr_v_count': v_count,
                    'curr_p_count': p_count
                })
                summary = (
                    f"✅ <b>Batch Selected</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📛 <b>Name:</b> {b_name}\n"
                    f"📂 <b>Folders:</b> {len(topics)}\n"
                    f"📹 <b>Videos:</b> {v_count}\n"
                    f"📑 <b>PDFs:</b> {p_count}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Click the button below to extract all content as a TXT file."
                )
                kb = [
                    [InlineKeyboardButton("📥 Extract Full TXT", callback_data="act_full")],
                    [InlineKeyboardButton("🔙 Back to Batches", callback_data="back_to_batches")]
                ]
                await query.edit_message_text(summary, reply_markup=InlineKeyboardMarkup(kb), parse_mode="html")
        except Exception as e:
            logging.exception("Callback selection error")
            await query.edit_message_text("❌ Error loading batch. 😵‍💫")

    elif data == "act_full":
        if not is_ram_authorized(uid):
            await query.answer("🚫 Access Denied!", show_alert=True)
            return
        await query.answer()
        topics = ram_user_data.get(uid, {}).get('curr_topics', [])
        b_name = ram_user_data.get(uid, {}).get('curr_batch_name', 'Batch')
        b_id = ram_user_data.get(uid, {}).get('curr_batch_id', '')
        v_count = ram_user_data.get(uid, {}).get('curr_v_count', 0)
        p_count = ram_user_data.get(uid, {}).get('curr_p_count', 0)
        processing_msg = await query.edit_message_text(
            f"⏳ <b>Extracting content from</b> <code>{b_name}</code>...\nPlease wait, this may take a moment. ⚡",
            parse_mode="html"
        )
        output = [
            f"{BANNER_LINE}",
            f"👤 <b>Extracted By:</b> {user.first_name} (@{user.username or 'N/A'})",
            f"📛 <b>Batch:</b> {b_name} (ID: {b_id})",
            f"📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
        ]
        for t in topics:
            topic_name = t.get('topicName', 'General')
            for cls in t.get("classes", []):
                title = cls.get('title', 'Untitled').strip()
                v_link = cls.get('class_link')
                if v_link:
                    output.append(f"🎥 [{topic_name}] {STYLISH_NAME} {title} (VIDEO) : {v_link}")
                for pdf in cls.get("classPdf", []):
                    p_url = pdf.get("url") if isinstance(pdf, dict) else str(pdf)
                    if p_url:
                        output.append(f"📄 [{topic_name}] {STYLISH_NAME} {title} (PDF) : {p_url}")
        filename = f"🦋⍣⃝_R𝒂₫𝖍𝒂⚚_{sanitize_filename(b_name)}.txt"
        file_buffer = io.BytesIO("\n".join(output).encode('utf-8'))
        caption = (
            f"✨ <b>{STYLISH_NAME}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ <b>Extraction Complete!</b>\n"
            f"📛 <b>Batch:</b> {b_name}\n"
            f"📹 <b>Videos:</b> {v_count}\n"
            f"📑 <b>PDFs:</b> {p_count}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>By:</b> {user.first_name}"
        )
        await query.message.reply_document(document=file_buffer, filename=filename, caption=caption, parse_mode="html")
        await processing_msg.delete()

    elif data == "back_to_batches":
        if not is_ram_authorized(uid):
            await query.answer("🚫 Access Denied!", show_alert=True)
            return
        await query.answer()
        batches = ram_user_data.get(uid, {}).get('all_batches', [])
        if not batches:
            await query.edit_message_text("⚠️ No batches in cache. Please use /extract again. 🥲")
            return
        header = f"📚 <b>Available Batches</b>\n━━━━━━━━━━━━━━━━━━━━━━\nSelect a batch to extract its content.\n━━━━━━━━━━━━━━━━━━━━━━\n"
        kb = []
        for b in batches:
            kb.append([InlineKeyboardButton(f"📁 {b['title'][:40]}", callback_data=f"sel_{b['id']}")])
        kb.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_extract")])
        await query.edit_message_text(header, reply_markup=InlineKeyboardMarkup(kb), parse_mode="html")

    elif data.startswith("cw_batch_"):
        if not is_ram_authorized(uid):
            await query.answer("🚫 Access Denied!", show_alert=True)
            return
        await query.answer()
        batch_id = data.split("_")[2]
        batch_name = ram_user_data.get(uid, {}).get('careerwill_batch_map', {}).get(batch_id, "Batch")
        processing_msg = await query.edit_message_text(
            f"⏳ Extracting videos from <b>{batch_name}</b>... 🎬",
            parse_mode="html"
        )
        try:
            async with aiohttp.ClientSession(headers=CAREERWILL_HEADERS) as session:
                url = CAREERWILL_BATCH_DETAIL.format(batch_id)
                data = await fetch_with_retry(session, url)
                if data is None:
                    await processing_msg.edit_text("❌ Failed to fetch batch details. 🫠")
                    return

                batch_class_data = data.get("pageProps", {}).get("batchClassData", {})
                classes = batch_class_data.get("classes", [])
                if not classes:
                    await processing_msg.edit_text("⚠️ No videos found in this batch. 🥲")
                    return

                output = [
                    f"{BANNER_LINE}",
                    f"👤 <b>Extracted By:</b> {user.first_name} (@{user.username or 'N/A'})",
                    f"📛 <b>Batch:</b> {batch_name} (ID: {batch_id})",
                    f"📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                ]

                for cls in classes:
                    lesson_name = cls.get('lessonName', 'Untitled')
                    lesson_url = cls.get('lessonUrl', '')
                    if lesson_url:
                        if not lesson_url.startswith('http'):
                            video_url = f"https://www.youtube.com/watch?v={lesson_url}"
                        else:
                            video_url = lesson_url
                        output.append(f"🎥 {lesson_name} : {video_url}")

                filename = f"Careerwill_{sanitize_filename(batch_name)}.txt"
                file_buffer = io.BytesIO("\n".join(output).encode('utf-8'))

                caption = (
                    f"✨ <b>{STYLISH_NAME}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ <b>Extraction Complete!</b>\n"
                    f"📛 <b>Batch:</b> {batch_name}\n"
                    f"🎥 <b>Videos:</b> {len(classes)}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>By:</b> {user.first_name}"
                )

                await query.message.reply_document(
                    document=file_buffer,
                    filename=filename,
                    caption=caption,
                    parse_mode="html"
                )
                await processing_msg.delete()
        except Exception as e:
            logging.exception("Careerwill batch error")
            await processing_msg.edit_text(f"❌ Error: {str(e)} 😵‍💫")

    elif data == "cancel_extract":
        await query.answer()
        await query.edit_message_text("❌ Action cancelled. 🙅‍♂️")

# ================= ORIGINAL DRM HANDLERS =================

@bot.on_message(filters.command("start") & (filters.private | filters.channel))
async def start_cmd(client: Client, message: Message):
    try:
        if message.chat.type == "channel":
            if not db.is_channel_authorized(message.chat.id, client.me.username):
                return
            await message.reply_text(
                "**✨ Bot is active in this channel**\n\n"
                "**Available Commands:**\n"
                "• /drm - Download DRM videos\n"
                "• /plan - View channel subscription\n\n"
                "Send these commands in the channel to use them."
            )
        else:
            is_authorized = db.is_user_authorized(message.from_user.id, client.me.username)
            is_admin = db.is_admin(message.from_user.id)
            if not is_authorized:
                await message.reply_photo(
                    photo=photologo,
                    caption=(
                        f"<b>⛔ Access Denied</b>\n\n"
                        f"<blockquote>You don't have permission to use this bot.</blockquote>\n"
                        f"<i>Contact admin to get access.</i>"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/Helpbykrishna2_bot")],
                        [InlineKeyboardButton("ℹ️ Features", callback_data="help")]
                    ])
                )
                return
            
            commands_list = (
                "• <b>/drm</b> - Start uploading courses\n"
                "• <b>/plan</b> - View subscription details\n"
            )
            if is_admin:
                commands_list += "\n<b>👑 Admin:</b>\n• /users - List all users\n"
            
            caption = (
                f"<b>┌───⧫ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ⧫───┐</b>\n"
                f"│\n"
                f"│  👋 <b>Hello, {message.from_user.first_name}</b>\n"
                f"│\n"
                f"│  ✨ <i>қⲅⳕ⳽ⲏⲛⲇ ★⚔ is ready!</i>\n"
                f"│  📌 Use commands below\n"
                f"│\n"
                f"│  <b>📁 Commands:</b>\n"
                f"{commands_list}\n"
                f"│\n"
                f"└───⧫ <b>қⲅⳕ⳽ⲏⲛⲇ ★⚔</b> ⧫───┘"
            )
            
            await message.reply_photo(
                photo=photologo,
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📞 Contact", url="https://t.me/Helpbykrishna2_bot")],
                    [InlineKeyboardButton("ℹ️ Features", callback_data="help"),
                     InlineKeyboardButton("📊 Plan", callback_data="plan")]
                ])
            )
    except Exception as e:
        print(f"Error in start: {str(e)}")

# Authorization filter – FIX: no ~ used
def auth_check_filter(_, client, message):
    try:
        if message.chat.type == "channel":
            return db.is_channel_authorized(message.chat.id, client.me.username)
        else:
            return db.is_user_authorized(message.from_user.id, client.me.username)
    except Exception:
        return False

# Create a negated filter without using ~
not_auth_filter = filters.create(lambda _, client, message: not auth_check_filter(_, client, message))

@bot.on_message(not_auth_filter & filters.private & filters.command)
async def unauthorized_handler(client, message):
    await message.reply(
        "<b>Mʏ Nᴀᴍᴇ [DRM Wɪᴢᴀʀᴅ 🦋](https://t.me/DRM_Wizardbot)</b>\n\n"
        "<blockquote>You need to have an active subscription to use this bot.\n"
        "Please contact admin to get premium access.</blockquote>",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("💫 Get Premium Access", url="https://t.me/Helpbykrishna2_bot")
        ]])
    )

@bot.on_message(filters.command("id") & filters.private)
async def id_command(client, message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.command("t2h") & filters.private)
async def call_html_handler(client, message):
    await message.reply_text("Use /html command to convert TXT to HTML.")

auth_filter = filters.create(auth_check_filter)

@bot.on_message(filters.command("logs") & auth_filter)
async def send_logs_auth(client, message):
    if message.chat.type == "channel":
        if not db.is_channel_authorized(message.chat.id, client.me.username):
            return
    else:
        if not db.is_user_authorized(message.from_user.id, client.me.username):
            await message.reply_text("❌ Not authorized.")
            return
    try:
        with open("logs.txt", "rb") as file:
            sent = await message.reply_text("**📤 Sending logs...**")
            await message.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await message.reply_text(f"**Error:** {e}")

@bot.on_message(filters.command("t2t") & filters.private)
async def text_to_txt(client, message):
    # Your original code
    pass

@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client, message):
    # Your original code
    pass

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client, message):
    # Your original code
    pass

@bot.on_message(filters.command("stop") & filters.private)
async def restart_handler(client, message):
    await message.reply_text("🚦 **STOPPED**", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

# DRM command – copy your full drm handler here
@bot.on_message(filters.command("drm") & auth_filter)
async def drm_cmd(client: Client, message: Message):
    # Paste your complete drm handler code here.
    # For now, a placeholder:
    await message.reply_text("DRM command is active. Please upload a .txt file.")

# Text handler for single links – now without ~filters.command, using explicit check
@bot.on_message(filters.text & filters.private)
async def text_handler(client, message):
    # Ignore commands and empty messages
    if not message.text or message.text.startswith('/'):
        return
    # Your original text handler code for single DRM links.
    pass

# ================= OTHER FUNCTIONS =================

def notify_owner():
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": OWNER_ID, "text": "Bot Is Live Now 🤖"})
    except:
        pass

def reset_and_set_commands():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
        requests.post(url, json={"commands": []})
        commands = [
            {"command": "start", "description": "✅ Check if bot is alive"},
            {"command": "drm", "description": "📄 Upload .txt file for DRM"},
            {"command": "extract", "description": "📂 Extract batches (Auth)"},
            {"command": "cw", "description": "📋 Get CW batches (Auth)"},
            {"command": "careerwill", "description": "🎯 Careerwill batches (Auth)"},
            {"command": "html", "description": "🌐 TXT to HTML"},
            {"command": "split", "description": "✂️ Split TXT subject-wise (Auth)"},
            {"command": "setting", "description": "⚙️ Settings"},
            {"command": "stop", "description": "⏹ Stop bot"},
            {"command": "cookies", "description": "🍪 Upload cookies"},
            {"command": "id", "description": "🆔 Get chat ID"},
        ]
        requests.post(url, json={"commands": commands})
    except:
        pass

if __name__ == "__main__":
    reset_and_set_commands()
    notify_owner()
    bot.run()
