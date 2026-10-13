"""Brand assets and accessible black/white app appearance."""
import base64
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / 'assets'


def theme_css(theme):
    light = theme == 'White'
    bg, fg, panel, border = ('#ffffff', '#111111', 'rgba(255,255,255,.94)', '#666666') if light else ('#000000', '#ffffff', '#141414', '#888888')
    background = bg
    if light:
        image = base64.b64encode((ASSETS / 'solar-background.jpeg').read_bytes()).decode('ascii')
        background = f"{bg} url('data:image/jpeg;base64,{image}') center / cover fixed no-repeat"
    return f'''<style>
    .stApp {{background:{background};color:{fg};color-scheme:{'light' if light else 'dark'};}}
    .block-container {{max-width:1100px;padding:1.5rem;border-radius:18px;background:{panel};margin-top:1rem;}}
    [data-testid="stHeader"] {{background:{bg};color:{fg};}}
    .stApp h1,.stApp h2,.stApp h3,.stApp p,.stApp label,.stApp [data-testid="stMarkdownContainer"] {{color:{fg};}}
    .card {{border:1px solid {border};border-radius:16px;padding:18px;min-height:128px;background:{panel};color:{fg};}}
    .badge {{display:inline-block;padding:4px 9px;border-radius:999px;border:1px solid {border};font-size:12px;}}
    .title {{font-size:20px;font-weight:700;margin:8px 0;}} .small {{opacity:.85;}}
    .stApp [data-baseweb="input"],.stApp [data-baseweb="textarea"],.stApp [data-baseweb="select"] > div {{background:{bg};color:{fg};border-color:{border};}}
    .stApp input,.stApp textarea {{background:{bg};color:{fg};-webkit-text-fill-color:{fg};caret-color:{fg};}}
    .stApp button {{background:{bg};color:{fg};border:1px solid {border};}}
    .stApp button p {{color:inherit;}}
    .stApp button:hover {{background:{fg};color:{bg};border-color:{fg};}}
    .stApp button:focus-visible {{outline:3px solid {fg};outline-offset:3px;}}
    .stApp [data-testid="stForm"] {{background:{panel};border-color:{border};}}
    .stApp [data-testid="stAlert"] {{background:{panel};color:{fg};border:1px solid {border};}}
    .stApp [data-testid="stCaptionContainer"] {{color:{fg};}}
    @media(max-width:640px) {{.block-container {{padding:1rem;margin-top:.5rem;}}}}
    </style>'''
