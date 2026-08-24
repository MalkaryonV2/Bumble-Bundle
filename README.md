# 📦 Flow Launcher IsThereAnyDeal Bundles

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Flow Launcher](https://img.shields.io/badge/Flow%20Launcher-Plugin-purple.svg)](https://www.flowlauncher.com/)

A lightning-fast Flow Launcher plugin to discover active video game bundles from **IsThereAnyDeal**, inspect their exact game compositions, check live Steam prices, and read community review ratings instantly.

</div>

---

## ✨ Features

* **⚡ Instant RSS Search**: Query current game bundles directly from IsThereAnyDeal's feed with zero lag.
* **🔍 Game Search (`bundle game [name]`)**: Search for any specific game across all active bundles to see instantly which bundle contains it, along with store and pricing details.
* **🖼️ Local Caching**: Automatically downloads, optimizes, and caches official Steam game capsules and store logos (`Humble Bundle`, `Fanatical`, etc.) locally for instant subsequent loads.
* **⭐ Live Steam Reviews & Ratings**: Right-clicking a bundle or game search result fetches real-time Steam data, showing you review score descriptors (e.g., *Overwhelmingly Positive*) alongside total review counts.
* **💰 Pricing & Store Integration**: Clear breakdown of bundle pricing structures and direct links to the stores.
* **🔄 Smart Fallbacks**: Automatically falls back to an IsThereAnyDeal search if a bundled title isn't available on Steam.

---

## 🚀 How It Works

* **`bundle [optional search query]`**: Type your keyword to search through active game bundles.
* **`bundle game [game name]`**: Search for a specific game across all active bundles (e.g., `bundle game Hades`). 
* **Left Click**: Opens the selected bundle or game store page directly in your default web browser.
* **Right Click (Context Menu)**: Instantly reveals every game composing that bundle in parallel, complete with individual Steam pricing, review scores, and direct store links (works on both bundle results and game search results!).

---

## 📥 Installation

1. Go into Flow Launcher's plugin store.
2. Select `install plugin from local path`.
3. Select the latest `.zip` from this repo.
4. Ensure Python 3.x is installed on your system.
5. Restart Flow Launcher.

---

## 🎮 Usage

Simply activate the plugin using your designated action keyword:

```text
bundle [optional search query]
