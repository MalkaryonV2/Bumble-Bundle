import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
import re
import os
import webbrowser
import html
from urllib.parse import urlparse, quote
import time

PLUGIN_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.join(PLUGIN_DIR, "Cache")
STEAM_CACHE_FILE = os.path.join(CACHE_DIR, "steam_cache.json")

try:
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
except Exception:
    pass

ACTION_KEYWORD = "bundle"
try:
    with open(os.path.join(PLUGIN_DIR, "plugin.json"), "r", encoding="utf-8") as f:
        p_data = json.load(f)
        ak = p_data.get("ActionKeyword") or p_data.get("ActionKeywords")
        if isinstance(ak, list) and ak:
            ACTION_KEYWORD = ak[0]
        elif isinstance(ak, str) and ak:
            ACTION_KEYWORD = ak
except Exception:
    pass

_BUNDLES_CACHE = []
_CACHE_TIMESTAMP = 0
CACHE_DURATION = 300

_STEAM_CACHE = {}
if os.path.exists(STEAM_CACHE_FILE):
    try:
        with open(STEAM_CACHE_FILE, "r", encoding="utf-8") as f:
            _STEAM_CACHE = json.load(f)
    except Exception:
        pass

def save_steam_cache():
    try:
        with open(STEAM_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_STEAM_CACHE, f)
    except Exception:
        pass

def get_store_icon(store_text, store_url=""):
    if not store_text:
        return "icon.png"
    store_lower = store_text.lower()
    clean_name = re.sub(r'[^a-z0-9]', '', store_lower)
    if not clean_name:
        return "icon.png"
    
    domain = ""
    if store_url:
        try:
            parsed_url = urlparse(store_url)
            netloc = parsed_url.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            domain = netloc
        except Exception:
            pass

    if not domain:
        domain_map = {
            "humble": "humblebundle.com",
            "fanatical": "fanatical.com",
            "indiegala": "indiegala.com",
            "greenmangaming": "greenmangaming.com",
            "gmg": "greenmangaming.com",
            "gog": "gog.com",
            "steam": "steampowered.com",
            "epicgames": "epicgames.com",
            "itchio": "itch.io"
        }
        domain = domain_map.get(clean_name, f"{clean_name}.com")

    icon_url = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
    local_icon_path = os.path.join(CACHE_DIR, f"{clean_name}_logo.ico")
    
    if not os.path.exists(local_icon_path) or os.path.getsize(local_icon_path) == 0:
        try:
            req = urllib.request.Request(icon_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=2) as response:
                with open(local_icon_path, 'wb') as f:
                    f.write(response.read())
        except Exception:
            pass
            
    if os.path.exists(local_icon_path) and os.path.getsize(local_icon_path) > 0:
        return local_icon_path
    return "icon.png"

def get_game_icon(app_id, img_url):
    if not app_id and not img_url:
        return "icon.png"
    filename = f"game_{app_id}.jpg" if app_id else "game_custom.jpg"
    local_path = os.path.join(CACHE_DIR, filename)
    
    if not os.path.exists(local_path) or os.path.getsize(local_path) == 0:
        if img_url:
            try:
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=2) as response:
                    with open(local_path, 'wb') as f:
                        f.write(response.read())
            except Exception:
                pass
                
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    return "icon.png"

def open_url(url):
    try:
        webbrowser.open(url)
    except Exception:
        pass
    return None

def clean_html(raw_html):
    if not raw_html:
        return ""
    try:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return html.unescape(cleantext).strip()
    except Exception:
        return ""

def get_game_info(game_name):
    if game_name in _STEAM_CACHE:
        cached = _STEAM_CACHE[game_name]
        if len(cached) == 3 and os.path.exists(cached[2]):
            return cached[0], cached[1], cached[2]

    try:
        query_url = f"https://store.steampowered.com/api/storesearch/?term={quote(game_name)}&l=english&cc=US"
        req = urllib.request.Request(query_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            items = data.get("items", [])
            if items:
                item = items[0]
                app_id = item.get("id")
                steam_url = f"https://store.steampowered.com/app/{app_id}/"
                
                img_url = item.get("tiny_image")
                if not img_url and app_id:
                    img_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/capsule_sm_120.jpg"
                
                local_icon = get_game_icon(app_id, img_url)
                
                price_info = item.get("price")
                if price_info:
                    final_cents = price_info.get("final")
                    if final_cents is not None:
                        price_str = "Free" if final_cents == 0 else f"${final_cents / 100.0:.2f}"
                    else:
                        price_str = "Available on Steam"
                else:
                    price_str = "Free / F2P"
                
                # Récupération des avis et notes Steam
                review_str = ""
                if app_id:
                    try:
                        rev_url = f"https://store.steampowered.com/appreviews/{app_id}?json=1&purchase_type=all"
                        rev_req = urllib.request.Request(rev_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(rev_req, timeout=1.0) as rev_resp:
                            rev_data = json.loads(rev_resp.read().decode('utf-8'))
                            summary = rev_data.get("query_summary", {})
                            score_desc = summary.get("review_score_desc", "")
                            total_revs = summary.get("total_reviews", 0)
                            if score_desc:
                                review_str = f" — {score_desc} ({total_revs:,} reviews)"
                    except Exception:
                        pass
                
                sub_text = f"Steam Price: {price_str}{review_str}"
                res = (steam_url, sub_text, local_icon)
                _STEAM_CACHE[game_name] = res
                save_steam_cache()
                return res
    except Exception:
        pass

    itad_url = f"https://isthereanydeal.com/search/?q={quote(game_name)}"
    res = (itad_url, "Not on Steam — Compare on IsThereAnyDeal", "icon.png")
    _STEAM_CACHE[game_name] = res
    save_steam_cache()
    return res

def fetch_bundles():
    global _BUNDLES_CACHE, _CACHE_TIMESTAMP
    current_time = time.time()
    if _BUNDLES_CACHE and (current_time - _CACHE_TIMESTAMP < CACHE_DURATION):
        return _BUNDLES_CACHE

    url = "https://isthereanydeal.com/feeds/US/USD/bundles.rss"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 BumbleBundle/39.0'})
    
    results = []
    seen_names = set()
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        channel = root.find('channel')
        if channel is None:
            return _BUNDLES_CACHE if _BUNDLES_CACHE else []
            
        for item in channel.findall('item'):
            try:
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                
                raw_title = title_elem.text if title_elem is not None and title_elem.text else ""
                link = link_elem.text if link_elem is not None and link_elem.text else "https://isthereanydeal.com"
                description_raw = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                
                if not raw_title or "tier" in raw_title.lower() or " by " not in raw_title:
                    continue
                
                parts = raw_title.rsplit(" by ", 1)
                name = parts[0].strip()
                store = parts[1].strip()
                
                if name in seen_names:
                    continue
                seen_names.add(name)
                
                clean_desc = clean_html(description_raw)
                
                found_raw_prices = re.findall(r'([\$\€\£])(\d+(?:\.\d{2})?)', clean_desc + " " + raw_title)
                price_dict = {}
                for symbol, val_str in found_raw_prices:
                    try:
                        val = float(val_str)
                        price_dict[val] = f"{symbol}{val_str}"
                    except Exception:
                        pass
                
                unique_prices = [price_dict[v] for v in sorted(price_dict.keys())]
                price_str = " / ".join(unique_prices) if unique_prices else "Variable price"
                
                results.append({
                    "Title": name,
                    "SubTitle": f"{store} — {price_str}",
                    "IcoPath": get_store_icon(store, link),
                    "Link": link,
                    "Store": store,
                    "Prices": price_str,
                    "Description": clean_desc
                })
                
                if len(results) >= 15:
                    break
            except Exception:
                continue
        
        if results:
            _BUNDLES_CACHE = results
            _CACHE_TIMESTAMP = current_time
        return results
    except Exception:
        return _BUNDLES_CACHE if _BUNDLES_CACHE else []

def query(param=""):
    bundles = fetch_bundles()
    if not bundles:
        return {"result": [{"Title": "No bundles found", "SubTitle": "", "IcoPath": "icon.png"}]}
        
    if param:
        filtered = [b for b in bundles if param.lower() in b["Title"].lower()]
        if not filtered:
            return {"result": [{"Title": f"No bundle matches '{param}'", "SubTitle": "", "IcoPath": "icon.png"}]}
        bundles_to_show = filtered
    else:
        bundles_to_show = bundles
        
    formatted_results = []
    for b in bundles_to_show:
        formatted_results.append({
            "Title": b["Title"],
            "SubTitle": b["SubTitle"],
            "IcoPath": b["IcoPath"],
            "ContextData": b["Title"],
            "JsonRPCAction": {
                "method": "open_url",
                "parameters": [b["Link"]],
                "hide_window_after_execution": True
            }
        })
    return {"result": formatted_results}

if __name__ == "__main__":
    response_payload = {"result": [{"Title": "Loading...", "SubTitle": "", "IcoPath": "icon.png"}]}
    try:
        if len(sys.argv) > 1:
            request = json.loads(sys.argv[1])
            method = request.get("method")
            parameters = request.get("parameters", [])

            if method == "query":
                search_text = parameters[0] if len(parameters) > 0 else ""
                response_payload = query(search_text)
                
            elif method == "context_menu":
                bundle_title = parameters[0] if parameters else ""
                bundles = fetch_bundles()
                target_bundle = next((b for b in bundles if b["Title"].lower() == bundle_title.lower()), None)
                
                menu_results = []
                if target_bundle:
                    menu_results.append({
                        "Title": f"Open {target_bundle['Title']} in browser",
                        "SubTitle": f"{target_bundle['Store']} — {target_bundle['Prices']}",
                        "IcoPath": target_bundle["IcoPath"],
                        "JsonRPCAction": {
                            "method": "open_url",
                            "parameters": [target_bundle["Link"]],
                            "hide_window_after_execution": True
                        }
                    })
                    
                    desc = target_bundle.get("Description", "")
                    lines = [l.strip() for l in desc.split('\n') if l.strip()]
                    game_lines = []
                    for line in lines:
                        l_lower = line.lower()
                        if "expires on" in l_lower or "go to bundle" in l_lower or "tier" in l_lower:
                            continue
                        if any(p in line for p in target_bundle['Prices'].split(" / ")) and len(line) < 15:
                            continue
                        if len(line) > 3:
                            game_lines.append(line)
                            
                    if game_lines:
                        games_to_fetch = game_lines[:15]
                        for g_line in games_to_fetch:
                            game_url, game_sub, game_icon = get_game_info(g_line)
                            menu_results.append({
                                "Title": g_line,
                                "SubTitle": game_sub,
                                "IcoPath": game_icon,
                                "JsonRPCAction": {
                                    "method": "open_url",
                                    "parameters": [game_url],
                                    "hide_window_after_execution": True
                                }
                            })
                    else:
                        menu_results.append({
                            "Title": "No additional games list found",
                            "SubTitle": "Open in browser to see details",
                            "IcoPath": "icon.png",
                            "JsonRPCAction": {
                                "method": "open_url",
                                "parameters": [target_bundle["Link"]],
                                "hide_window_after_execution": True
                            }
                        })
                else:
                    menu_results.append({
                        "Title": "Bundle not found",
                        "SubTitle": "",
                        "IcoPath": "icon.png"
                    })
                    
                response_payload = {"result": menu_results}
                
            elif method == "open_url":
                if parameters:
                    open_url(parameters[0])
                response_payload = {"result": []}
                
    except Exception as ex:
        response_payload = {
            "result": [{
                "Title": "Error",
                "SubTitle": str(ex),
                "IcoPath": "icon.png"
            }]
        }
    print(json.dumps(response_payload))
