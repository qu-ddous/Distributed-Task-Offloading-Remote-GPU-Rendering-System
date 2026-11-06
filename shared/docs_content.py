"""
Comprehensive Bilingual Documentation Data for GPU Task Offloading & Rendering System.
Supports English (Default) and Roman Urdu.
"""

DOCS_DATA = {
    "en": {
        "title": "System Documentation & User Manual",
        "subtitle": "Complete guide on capabilities, architecture, tasks, and usage instructions.",
        "lang_switch_label": "Documentation Language:",
        "sections": [
            {
                "id": "overview",
                "icon": "🌟",
                "tag": "PROJECT PURPOSE & BENEFITS",
                "tag_color": "#3B82F6",
                "title": "Why was this project built?",
                "summary": "Offload heavy video rendering, AI compute, and script execution from low-spec laptops to high-performance GPU desktops via direct cable.",
                "points": [
                    ("🎯 The Core Problem", "Creative workflows (video rendering, 3D animations, AI model inference, ML training) require powerful multi-core CPUs and dedicated NVIDIA/AMD GPUs. Lightweight laptops overheat, throttle, or take hours to complete these tasks."),
                    ("⚡ The Solution", "This system pairs your lightweight laptop (Client) directly to a powerful GPU desktop (Server) via a simple Ethernet LAN wire. All processing runs 100% on the server hardware, while results are automatically downloaded back to your laptop."),
                    ("🔒 100% Offline & Free", "No internet access, cloud subscriptions, or external servers required. Data transfers peer-to-peer at direct cable speeds (up to 1,000 Mbps / 1 Gbps) with cryptographic SHA-256 integrity validation.")
                ]
            },
            {
                "id": "tasks",
                "icon": "🎬",
                "tag": "SUPPORTED WORKFLOWS",
                "tag_color": "#10B981",
                "title": "What Tasks Can You Perform?",
                "summary": "Four dedicated task execution profiles tailored for media, machine learning, and universal execution.",
                "points": [
                    ("🎬 1. Video Transcoding & GPU Acceleration", "Transcode or render videos using server hardware encoders (NVIDIA NVENC, Intel QuickSync, AMD AMF, MediaFoundation) or multi-core CPU. Scale resolutions (720p, 1080p, 1440p, 4K) and customize bitrates (2M to 20M)."),
                    ("🧠 2. Python & AI / Machine Learning", "Run machine learning training scripts, deep learning model inference (PyTorch, TensorFlow, OpenCV), and data science pipelines on the server's discrete GPU VRAM and multi-core CPU. Real-time console logs stream back to your screen."),
                    ("⚡ 3. Batch / Shell Automation (.bat, .cmd)", "Execute administrative batch files, shell commands, compilation tasks, and FFmpeg command pipelines directly on the server without consuming laptop resources."),
                    ("🌟 4. All-in-One Universal Task Runner", "Select ANY project folder or enter any command. Studio packages the folder into a secure ZIP, transfers it to the server, extracts it, executes your command, and automatically returns the generated output archive to your laptop!"),
                    ("📁 5. Watch Folder Automation (CapCut / Premiere)", "Designate an export watch folder on your laptop. Set CapCut, Premiere, or DaVinci to export there. As soon as a video file appears, Studio automatically offloads it to the server for hardware rendering!")
                ]
            },
            {
                "id": "connection",
                "icon": "🔌",
                "tag": "CONNECTION SETUP",
                "tag_color": "#8B5CF6",
                "title": "How to Connect via Direct Cable",
                "summary": "Follow these simple steps to establish a high-speed direct peer-to-peer cable connection.",
                "points": [
                    ("⚡ Method 1: 1-Click P2P Pairing Tool (Recommended)", "Run 'dist/DIRECT_CABLE_PAIRING.bat' as Administrator.\n• On Server PC: Press '1' (Sets Static IP: 192.168.99.1 & unblocks firewall).\n• On Client Laptop: Press '2' (Sets Static IP: 192.168.99.2).\n• In Client Studio: Enter Server IP 192.168.99.1 and click Connect! (Connects in <0.01s)."),
                    ("🔌 Method 2: Automatic Windows Cable (APIPA)", "Connect LAN cable between both PCs. Windows assigns 169.254.x.x automatically. On Server, click 'Unblock Firewall' in the topbar. On Client, click 'Auto-Detect' to locate the server automatically."),
                    ("🛡️ Firewall Notice", "Windows Defender Firewall classifies direct cable connections as 'Public Network' and blocks port 8000 by default. Clicking 'Unblock Firewall' on the Server or running 'FIX_FIREWALL.bat' permanently resolves this."),
                    ("💻 Slim Laptops (HP EliteBook, Dell XPS)", "Laptops without a built-in RJ45 port require a USB-to-LAN adapter. Ensure the USB dongle is firmly inserted so Windows recognizes the Ethernet controller.")
                ]
            },
            {
                "id": "ui_guide",
                "icon": "🖥️",
                "tag": "APPLICATION WALKTHROUGH",
                "tag_color": "#F97316",
                "title": "Step-by-Step UI Guide",
                "summary": "How to navigate and utilize every feature in Client Studio and Server Node.",
                "points": [
                    ("📊 Dashboard Overview", "Displays connection health, real-time ping latency, remote server hardware gauges (CPU, RAM, GPU), quick-connect IP entry, and watch folder monitor."),
                    ("🎬 New Render Job Tab", "Pick your task profile (Video, Python, Batch, Universal). Select your input file or project folder. Set output name, target folder, resolution, and click 'Submit Remote Job'."),
                    ("📡 Live Telemetry & Execution Monitor", "Automatically opens upon job submission. Displays live progress bar, stage indicator, speed multiplier/FPS, server CPU & RAM usage meters, and real-time streaming terminal logs."),
                    ("⚡ Performance Benchmarks", "Run direct latency tests, socket round-trip benchmarks, and network stress tests to verify maximum cable throughput between the two machines."),
                    ("⚙️ Host Connection & Settings", "Configure worker server IPv4, port (default 8000), shared secret token, default render resolutions, and watch folder path.")
                ]
            },
            {
                "id": "faq",
                "icon": "❓",
                "tag": "FAQS & TROUBLESHOOTING",
                "tag_color": "#06B6D4",
                "title": "Frequently Asked Questions",
                "summary": "Quick answers to common questions and troubleshooting tips.",
                "points": [
                    ("Q: Where are the rendered outputs saved?", "Rendered files and project results are automatically downloaded to your Client laptop's 'Downloads' folder (or custom output directory set in Settings). A prominent 'Open Folder' button appears when finished."),
                    ("Q: Why does 'Connection Timed Out' happen?", "Check if: (1) Server PC has GPUWorkerServer.exe running, (2) 'Unblock Firewall' was clicked on Server, (3) Client and Server have their Ethernet cable connected, (4) Correct Server IP is entered."),
                    ("Q: Does this consume my internet quota?", "No! All data streams over the local physical LAN cable. Zero internet bytes are used."),
                    ("Q: Can my friend use my GPU while I am away?", "Yes! Simply leave GPUWorkerServer.exe running on your desktop. Your friend connects their laptop with the cable and runs render jobs or AI models without needing your supervision.")
                ]
            }
        ]
    },
    "ur": {
        "title": "Project Documentation & User Rehnumai (Roman Urdu)",
        "subtitle": "System ke maqsad, task profiles, wire connection aur software use karne ka asan tareeqa.",
        "lang_switch_label": "Documentation ki Zaban:",
        "sections": [
            {
                "id": "overview",
                "icon": "🌟",
                "tag": "PROJECT KA MAQSAD AUR FAIDAY",
                "tag_color": "#3B82F6",
                "title": "Yeh Project Kyun Banaya Gaya?",
                "summary": "Halkay/kamzor laptop se heavy video rendering, AI model training aur scripts ko direct wire ke zariye taqatwar GPU PC par chalana.",
                "points": [
                    ("🎯 Asal Masla Kya Tha?", "Heavy video editing (CapCut, Premiere), 3D animation, aur AI model training ke liye heavy multi-core CPU aur mehnga GPU (NVIDIA/AMD) chahiye hota hai. Aam laptops par render lagane se laptop garam ho jata hai aur ghanton lagte hain."),
                    ("⚡ Asan Hal", "Yeh software aap ke laptop (Client) ko direct ek Ethernet LAN wire se aap ke ya aap ke dost ke taqatwar GPU PC (Server) ke sath jor deta hai. Saara load aur rendering server ke graphics card aur RAM par hoti hai aur result wapas aap ke laptop par save ho jata hai."),
                    ("🔒 100% Offline aur Free", "Iske liye kisi internet, Wi-Fi ya cloud subscription ki zaroorat nahi hai. Data direct cable ke zariye high-speed (1000 Mbps tak) par transfer hota hai with SHA-256 security.")
                ]
            },
            {
                "id": "tasks",
                "icon": "🎬",
                "tag": "TASKS KI TAFSEEL",
                "tag_color": "#10B981",
                "title": "Is par Kaun Kaun se Kaam Chalaye ja sakte hain?",
                "summary": "Chaar makhsoos task profiles jo har qisam ke media, AI aur automation kaam ko handle karti hain.",
                "points": [
                    ("🎬 1. Video Transcoding & Hardware GPU Render", "Server ke graphics card (NVIDIA NVENC, Intel QuickSync, AMD AMF) ka use kar ke kisi bhi video ko fast convert/render karein. Resolution (720p, 1080p, 1440p, 4K) aur Bitrate customize karein."),
                    ("🧠 2. Python & AI / Machine Learning (Server Compute)", "Heavy Python scripts, PyTorch/TensorFlow deep learning models, aur data science training ko server ke GPU VRAM aur CPU par run karein. Client screen par live console logs nazar aate hain."),
                    ("⚡ 3. Batch / Shell Scripts (.bat, .cmd)", "Batch automation files aur FFmpeg commands ko direct server hardware par execute karein bina laptop par load daale."),
                    ("🌟 4. All-in-One Universal Task Runner (Folder & Command)", "Koi bhi project folder select karein. Studio khud usay zip bana kar server ko bhejta hai, server par extract kar ke aap ki command chalata hai (e.g. 'python train.py'), aur result wapas aap ke laptop par download kar deta hai!"),
                    ("📁 5. Watch Folder Automation (CapCut / Premiere Auto-Render)", "Laptop par ek Watch Folder set karein. CapCut ya Premiere mein video export karte waqt yeh folder choose karein. Jaise hi video save hogi, Studio khud usay pakar kar GPU server par render ke liye bhej dega!")
                ]
            },
            {
                "id": "connection",
                "icon": "🔌",
                "tag": "WIRE CONNECTION REHNUMAI",
                "tag_color": "#8B5CF6",
                "title": "Direct LAN Wire se Connect Karne ka Tareeqa",
                "summary": "Dono computers ko direct Ethernet cable se jorne ke 2 asan tareeqay.",
                "points": [
                    ("⚡ Tareeqa 1: 1-Click P2P Tool (Sub se Asan & Fast)", "'dist/DIRECT_CABLE_PAIRING.bat' ko Run as Administrator karein.\n• Server PC par: '1' dabayein (IP set hogi: 192.168.99.1 aur firewall unblock hoga).\n• Client Laptop par: '2' dabayein (IP set hogi: 192.168.99.2).\n• Client Studio mein: Server IP 192.168.99.1 daal kar Connect dabayein! (0.01s mein instant connect)."),
                    ("🔌 Tareeqa 2: Automatic Windows Cable (APIPA)", "Dono PCs mein LAN wire lagayein. Windows khud 169.254.x.x IP assign karega. Server par top bar mein '🛡️ Unblock Firewall' dabayein. Client par '🔍 Auto-Detect' dabayein."),
                    ("🛡️ Firewall Unblock Zaroori Hai", "Windows Defender Firewall direct cable ko 'Public Network' samajh kar port 8000 block kar deta hai. Server par 'Unblock Firewall' button ya 'FIX_FIREWALL.bat' chalana zaroori hai."),
                    ("💻 Slim Laptops (HP EliteBook, Dell wagera)", "Agar laptop slim hai aur direct LAN port nahi hai, toh USB-to-LAN adapter ko USB port mein mazbooti se lagayein taake Windows usey detect kare.")
                ]
            },
            {
                "id": "ui_guide",
                "icon": "🖥️",
                "tag": "UI KA ISTEMAL",
                "tag_color": "#F97316",
                "title": "Screen aur Buttons ko Kaise Use Karein",
                "summary": "Client Studio aur Server Node ki har screen ka mukammal tareeqa.",
                "points": [
                    ("📊 Dashboard Overview", "Server connection status, latency, server ke CPU/RAM/GPU ke live gauges, aur quick connect bar yahan mojood hain."),
                    ("🎬 New Render Job Tab", "Task type select karein (Video, Python, Batch, Universal), apni file ya project folder choose karein, output naam dein, aur 'Submit Remote Job' dabayein."),
                    ("📡 Live Monitor Screen", "Job submit hote hi yeh screen khud khul jati hai. Is mein real-time percentage, processing speed/FPS, server CPU/RAM usage aur live terminal logs aate hain."),
                    ("⚡ Performance Benchmarks", "Cable ki real speed aur packet round-trip test karne ke liye benchmarks run karein."),
                    ("⚙️ Host & Settings", "Server IP address, port (8000), secret token, aur default preferences configure karein.")
                ]
            },
            {
                "id": "faq",
                "icon": "❓",
                "tag": "AKSAR POOCHE JANAY WALAY SAWALAT",
                "tag_color": "#06B6D4",
                "title": "FAQs aur Troubleshooting",
                "summary": "Ahem sawalat ke jawab aur masail ka hal.",
                "points": [
                    ("Q: Render hone ke baad file kahan save hoti hai?", "Aap ke laptop ke 'Downloads' folder mein file khud ba khud save ho jati hai. Kaam khatam hote hi 'Open Result Folder' ka button samne aa jata hai."),
                    ("Q: Connection Timeout kyun aa raha hai?", "Check karein: (1) Server PC par GPUWorkerServer.exe chalu ho, (2) Server par 'Unblock Firewall' dabaya ho, (3) Cable dono taraf theek lagi ho, (4) Server IP sahi daali ho."),
                    ("Q: Kya isme mera internet data kharch hoga?", "Nahi! Yeh saara data physical LAN cable ke zariye transfer hota hai, internet ka 1 byte bhi use nahi hota."),
                    ("Q: Kya mera dost mere GPU ko use kar sakta hai?", "Haan! Bas apne GPU PC par GPUWorkerServer.exe on chor dein. Aap ka dost cable laga kar apne laptop se heavy rendering aaram se kar sakega.")
                ]
            }
        ]
    }
}

