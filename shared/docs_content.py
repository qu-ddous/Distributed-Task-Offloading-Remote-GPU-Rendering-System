"""
Comprehensive Bilingual Documentation Data for GPU Task Offloading & Rendering System.
Supports English (Default) and Roman Urdu.
"""

DOCS_DATA = {
    "en": {
        "title": "System Documentation & User Manual",
        "subtitle": "Complete step-by-step guide on task workflows, server resource verification, and UI navigation.",
        "lang_switch_label": "Documentation Language:",
        "sections": [
            {
                "id": "overview",
                "icon": "🌟",
                "tag": "PROJECT PURPOSE & BENEFITS",
                "tag_color": "#3B82F6",
                "title": "Why was this project built?",
                "summary": "Offload heavy video rendering, AI model training, and compute tasks from low-spec laptops to high-performance GPU desktops via a direct LAN cable.",
                "points": [
                    ("🎯 The Core Problem", "Creative and AI workflows (video transcoding, PyTorch deep learning, 3D rendering) demand heavy multi-core CPU power and dedicated NVIDIA GPU VRAM. Lightweight laptops overheat, throttle, drain battery, and take hours to complete these tasks."),
                    ("⚡ The Distributed Solution", "This system pairs your lightweight laptop (Client Studio) directly to a dedicated GPU PC (Worker Server) via an ordinary Ethernet wire. All compute operations execute 100% natively on the server hardware, and results are automatically transferred back to your laptop upon completion."),
                    ("🔒 100% Offline, Private & Free", "No internet connection, router DHCP, or cloud subscriptions are required. Data moves peer-to-peer at full physical cable speeds (up to 1,000 Mbps / 1 Gbps) with cryptographic SHA-256 integrity verification.")
                ]
            },
            {
                "id": "tasks",
                "icon": "🚀",
                "tag": "5 TASK WORKFLOWS (DETAILED GUIDE)",
                "tag_color": "#10B981",
                "title": "How to Run Every Task Profile",
                "summary": "Complete instructions for all five execution profiles available in the New Render Job view.",
                "points": [
                    ("🎬 1. Video Transcoding (GPU Accelerated)",
                     "• Step 1: Open 'New Render Job' and select '🎬 Video Transcode (GPU)'.\n"
                     "• Step 2: Click 'Browse Video File' to select any MP4, MOV, MKV, or AVI video.\n"
                     "• Step 3: Choose target Resolution (Original, 4K, 1440p, 1080p, 720p), Bitrate (2M to 20M), and NVENC Preset (p1 Fastest to p7 Slowest).\n"
                     "• Step 4: Ensure 'Allow CPU Fallback' is checked (gracefully switches to multi-core libx264 if video codecs require CPU).\n"
                     "• Step 5: Click 'Submit & Render on Remote GPU'. Your laptop remains idle while the desktop's NVIDIA GPU renders the stream."),

                    ("🧠 2. Python & AI / Machine Learning (Server Compute)",
                     "• Step 1: Select '🧠 Python / AI Model (Server Compute)'.\n"
                     "• Step 2: Click 'Browse Python (.py)' and choose your training or inference script (e.g. 'train.py').\n"
                     "• Step 3: In Execution Acceleration Profile, choose 'Auto-Detect (CUDA GPU / PyTorch)' or 'Dedicated NVIDIA GPU Preferred'.\n"
                     "• Step 4: Click 'Submit & Run / Train on Server Hardware'.\n"
                     "• Step 5: Studio switches to the Active Job monitor, streaming your training logs, loss curves, and epoch progress live! When finished, execution logs and generated artifacts save to your Downloads folder."),

                    ("⚡ 3. Batch / Shell Automation (.bat, .ps1, .cmd)",
                     "• Step 1: Select '⚡ Batch / Shell Script'.\n"
                     "• Step 2: Browse your batch script or command file.\n"
                     "• Step 3: Click 'Submit & Execute Script on Server'. The script executes in a native Windows command shell on the server machine with full administrator access, streaming terminal stdout and stderr back to your laptop in real-time."),

                    ("🌟 4. All-in-One Universal Task Runner (Entire Project Folders)",
                     "• Step 1: Select '🌟 All-in-One (Any Command / Folder)'.\n"
                     "• Step 2: Click '📁 Select Entire Project Folder...' to pick your project (containing datasets, multiple Python files, or requirements.txt).\n"
                     "• Step 3: In the Terminal Command box, enter the command to execute (e.g. 'pip install -r requirements.txt && python train.py') or click a quick preset chip.\n"
                     "• Step 4: Click 'Submit & Run Universal Task on Server'. Studio bundles your folder into a ZIP, transfers it to the server at Gigabit speed, extracts it in an isolated workspace, executes the command, and returns the result archive!"),

                    ("📁 5. Watch Folder Automation (Hands-Free Drop Workflow)",
                     "• Step 1: In 'Settings', enable Watch Folder and choose a folder on your laptop (e.g. 'C:\\Users\\Name\\Videos\\RenderWatch_In').\n"
                     "• Step 2: In video editors (CapCut, Premiere, DaVinci), set your export directory to this watch folder.\n"
                     "• Step 3: Whenever a new video file finishes exporting into that folder, Client Studio automatically detects it, computes SHA-256, uploads it to the GPU server, renders it, and saves the final video to your Downloads folder without you clicking a single button!")
                ]
            },
            {
                "id": "verification",
                "icon": "🔍",
                "tag": "100% RESOURCE VERIFICATION",
                "tag_color": "#EC4899",
                "title": "How to Verify Server Resources Are Really Being Used",
                "summary": "Four foolproof methods to confirm your laptop is at 0% load and the server is doing 100% of the work.",
                "points": [
                    ("📊 1. Live Telemetry on Client Screen ('⚡ Active Job' Tab)",
                     "While a job is running, the Active Job screen displays real-time server vitals:\n"
                     "• REMOTE CPU LOAD: Live CPU meter of the server PC (updating every second).\n"
                     "• REMOTE RAM USED: Real-time RAM consumption of the server (e.g., '14.2 GB / 32.0 GB').\n"
                     "• Streaming Console Logs: Live stdout/stderr from the server showing epoch losses, print statements, and PyTorch CUDA devices."),

                    ("🖥️ 2. Hardware Gauges on Server Screen ('Overview' & 'GPU Engine' Tabs)",
                     "Look at the Server PC screen during execution:\n"
                     "• GPU Utilization: Jumps from 0% up to 80%-99% as tensor calculations or NVENC encoders engage.\n"
                     "• GPU VRAM Usage: Displays exact dedicated memory allocated (e.g., '5.8 GB / 12.0 GB').\n"
                     "• GPU Temperature: Rises realistically under heavy workload (e.g., from 42°C to 68°C-74°C)."),

                    ("📈 3. Windows Task Manager Comparison (The Ultimate Proof)",
                     "• Open Task Manager on your Laptop (Ctrl + Shift + Esc): CPU load is 1% to 3%, GPU is 0%, and laptop memory is unaffected.\n"
                     "• Open Task Manager on Server PC: You will see 'python.exe' or 'ffmpeg.exe' consuming high CPU and maxing out the GPU 3D/Compute graph!"),

                    ("🔥 4. PyTorch / AI Script CUDA Sanity Code",
                     "Put this snippet at the top of your 'train.py' script:\n"
                     "import torch\n"
                     "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n"
                     "print(f'🔥 Training Running On: {device}')\n"
                     "if torch.cuda.is_available():\n"
                     "    print(f'🖥️ Server GPU: {torch.cuda.get_device_name(0)}')\n"
                     "    print(f'💾 Allocated VRAM: {torch.cuda.memory_allocated(0)/(1024**2):.2f} MB')\n"
                     "When submitted, Client Studio will print your desktop GPU model name directly on your laptop screen!")
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
                    ("⚡ Method 1: 1-Click P2P Pairing Tool (Recommended)",
                     "Run 'dist/DIRECT_CABLE_PAIRING.bat' as Administrator on both machines.\n"
                     "• On Server PC: Press '1' (Sets Static IP: 192.168.99.1 & unblocks firewall).\n"
                     "• On Client Laptop: Press '2' (Sets Static IP: 192.168.99.2).\n"
                     "• In Client Studio: Enter Server IP 192.168.99.1 and click Connect! (Connects in <0.01s)."),

                    ("🔌 Method 2: Automatic Windows Cable (APIPA)",
                     "Connect LAN cable directly between both PCs. Windows automatically assigns a 169.254.x.x address.\n"
                     "• Look at Server PC topbar: note the exact '🔌 Cable IP' shown there (or click '📋 Copy IP').\n"
                     "• Click '🛡️ Unblock Firewall' on the Server topbar.\n"
                     "• On Client Laptop: enter the Server's Cable IP in the Dashboard box and click '⚡ Connect'."),

                    ("🛡️ Firewall Notice",
                     "Windows Defender Firewall classifies direct cable connections as 'Public Network' and blocks port 8000 by default. Clicking 'Unblock Firewall' on the Server or running 'FIX_FIREWALL.bat' as Administrator permanently unblocks TCP 8000 and UDP 8002."),

                    ("💻 Slim Laptops (HP EliteBook, Dell XPS)",
                     "Laptops without a built-in RJ45 port require a USB-to-LAN adapter. Ensure the USB dongle is firmly inserted so Windows recognizes the Ethernet controller.")
                ]
            },
            {
                "id": "ui_guide",
                "icon": "🖥️",
                "tag": "APPLICATION WALKTHROUGH",
                "tag_color": "#F97316",
                "title": "Complete UI Page-by-Page Guide",
                "summary": "Detailed navigation guide for both Client Studio and Worker Server applications.",
                "points": [
                    ("📊 Client: Dashboard Overview", "Displays connection banner, live ping latency, remote server hardware gauges (CPU, RAM, GPU), quick-connect IP entry box, and watch folder monitor."),
                    ("🎬 Client: New Render Job", "Select between 4 task modes (Video Transcode, Python ML, Batch Script, All-in-One Universal). Configure output resolutions, bitrate, presets, and target output folder."),
                    ("📡 Client: Active Job Monitor", "Opens automatically during execution. Shows animated progress bar, stage indicator, speed multiplier/FPS, remote CPU/RAM usage meters, and live streaming console log terminal."),
                    ("📜 Client: Job History", "Table of all completed and past jobs with status pills, elapsed duration, output file paths, and one-click 'Open Folder' shortcuts."),
                    ("⚡ Client: Performance Benchmarks", "5-step live hardware benchmarking suite. Generates a standard video, tests local laptop CPU render time, measures cable upload, benchmarks remote GPU transcode, and computes exact speedup ratio!"),
                    ("⚙️ Client: Host Connection & Settings", "Set worker server IPv4, port (8000), API token, default output directory, default video presets, and configure the automated Watch Folder path."),
                    ("🖥️ Server: Overview Tab", "Real-time dashboard displaying GPU utilization %, GPU VRAM used, GPU temperature, CPU multi-core load, active render job details, and live activity events."),
                    ("⚙️ Server: GPU Engine Tab", "Hardware encoder detection (NVIDIA NVENC, QuickSync, AMF, CPU). Shows driver capabilities, supported codecs (H.264, HEVC, AV1), and hardware encoder status."),
                    ("📋 Server: Render Queue Tab", "Real-time table of all incoming, queued, running, completed, and failed tasks with client IP attribution, progress bars, and administrative cancel buttons."),
                    ("🌐 Server: Network & Connections Tab", "Shows detected network adapters, active client sessions table with live client IPv4, port, live status, last activity timestamp, and total data transferred!"),
                    ("🕒 Server: Activity Logs Tab", "System-wide audit trail recording server lifecycle events, client connections, firewall status, and file transfer completions.")
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
                    ("Q: Where are the rendered outputs saved?", "Rendered files and project results are automatically downloaded to your Client laptop's 'Downloads' folder (or custom directory set in Settings). A prominent 'Open Output Folder' button appears when finished."),
                    ("Q: Why does 'Connection Timed Out' happen?", "Check if: (1) Server PC has GPUWorkerServer.exe running, (2) 'Unblock Firewall' was clicked on Server, (3) Ethernet cable is firmly plugged into both PCs, (4) Exact Cable IP from Server topbar is entered."),
                    ("Q: Does this consume internet quota?", "No! All data streams over the local physical LAN cable. Zero internet bytes are used."),
                    ("Q: Can my friend use my GPU while I am away?", "Yes! Simply leave GPUWorkerServer.exe running on your desktop. Your friend connects their laptop with the cable and runs heavy video renders or AI models without needing your supervision.")
                ]
            }
        ]
    },
    "ur": {
        "title": "Project Documentation & User Rehnumai (Roman Urdu)",
        "subtitle": "Task profiles, server resource verification, aur software use karne ka mukammal tareeqa.",
        "lang_switch_label": "Documentation ki Zaban:",
        "sections": [
            {
                "id": "overview",
                "icon": "🌟",
                "tag": "PROJECT KA MAQSAD AUR FAIDAY",
                "tag_color": "#3B82F6",
                "title": "Yeh Project Kyun Banaya Gaya?",
                "summary": "Kamzor laptop se heavy video rendering, AI model training aur universal scripts ko direct LAN wire ke zariye taqatwar GPU PC par chalana.",
                "points": [
                    ("🎯 Asal Masla Kya Tha?", "Heavy video editing (CapCut, Premiere), 3D animation, aur AI deep learning models (PyTorch/TensorFlow) ke liye heavy multi-core CPU aur mehnga GPU (NVIDIA RTX) chahiye hota hai. Aam laptops par render lagane se laptop garam ho jata hai, hang hota hai aur ghanton lagte hain."),
                    ("⚡ Distributed Hal", "Yeh software aap ke laptop (Client) ko direct ek Ethernet LAN wire se aap ke ya aap ke dost ke taqatwar GPU PC (Server) ke sath jor deta hai. Saara load aur rendering server ke graphics card aur RAM par hoti hai aur result wapas aap ke laptop par save ho jata hai."),
                    ("🔒 100% Offline aur Free", "Iske liye kisi internet, Wi-Fi router ya cloud subscription ki zaroorat nahi hai. Data direct cable ke zariye high-speed (1000 Mbps tak) par transfer hota hai with SHA-256 security.")
                ]
            },
            {
                "id": "tasks",
                "icon": "🚀",
                "tag": "5 TASKS KI TAFSEEL (STEP-BY-STEP GUIDE)",
                "tag_color": "#10B981",
                "title": "Har Task Profile Chalane Ka Tareeqa",
                "summary": "New Render Job view mein mojood 5 mukhtalif task modes ko use karne ki mukammal rehnumai.",
                "points": [
                    ("🎬 1. Video Transcoding (Hardware GPU Render)",
                     "• Step 1: 'New Render Job' tab mein jaein aur '🎬 Video Transcode (GPU)' select karein.\n"
                     "• Step 2: 'Browse Video File' par click karke apni video file choose karein (MP4, MOV, MKV wagera).\n"
                     "• Step 3: Target Resolution (Original, 4K, 1080p, 720p), Bitrate (2M se 20M), aur NVENC Preset (p1 se p7) set karein.\n"
                     "• Step 4: 'Allow CPU Fallback' ko tick rehne dein (agar kisi video mein GPU codec na chale toh server ka CPU use ho).\n"
                     "• Step 5: 'Submit & Render on Remote GPU' dabayein. Laptop bilkul free rahega aur Server ka NVIDIA GPU render karega!"),

                    ("🧠 2. Python & AI / Machine Learning (Server Compute)",
                     "• Step 1: '🧠 Python / AI Model (Server Compute)' wala button dabayein.\n"
                     "• Step 2: 'Browse Python (.py)' par click kar ke apni training script (e.g. 'train.py') select karein.\n"
                     "• Step 3: Acceleration Profile mein 'Auto-Detect (CUDA GPU / PyTorch)' select karein.\n"
                     "• Step 4: 'Submit & Run / Train on Server Hardware' dabayein.\n"
                     "• Step 5: Screen foran Active Job par chali jayegi jahan training ke live epochs, loss values, aur terminal output screen par stream honge. Training khatam hote hi logs aur output aapke Downloads folder mein aa jayenge."),

                    ("⚡ 3. Batch / Shell Automation (.bat, .ps1, .cmd)",
                     "• Step 1: '⚡ Batch / Shell Script' option select karein.\n"
                     "• Step 2: Apni batch script ya system command file browse karein.\n"
                     "• Step 3: 'Submit & Execute Script on Server' dabayein. Script server ke Windows environment mein run hogi aur stdout/stderr live laptop par print hoga."),

                    ("🌟 4. All-in-One Universal Task Runner (Poora Project Folder)",
                     "• Step 1: '🌟 All-in-One (Any Command / Folder)' select karein.\n"
                     "• Step 2: 'Select Entire Project Folder...' par click karke apna poora project folder choose karein (jisme code, dataset, aur requirements.txt mojood hon).\n"
                     "• Step 3: Terminal Command box mein command likhein (e.g. 'pip install -r requirements.txt && python train.py') ya quick preset chip par click karein.\n"
                     "• Step 4: 'Submit & Run Universal Task on Server' dabayein. Studio poore folder ko zip bana kar cable ke zariye server ko bhejega, wahan extract karke command chalayega, aur output file laptop par download kar dega!"),

                    ("📁 5. Watch Folder Automation (CapCut / Premiere Auto-Render)",
                     "• Step 1: 'Settings' mein Watch Folder on karein aur laptop par ek folder set karein (e.g. 'Videos\\RenderWatch_In').\n"
                     "• Step 2: CapCut ya Premiere mein video export karte waqt yeh watch folder select karein.\n"
                     "• Step 3: Jaise hi video us folder mein save hogi, Studio khud usey pakar kar GPU server par render ke liye bhej dega aur final video Downloads mein save kar dega — aapko ek button bhi dabane ki zaroorat nahi!")
                ]
            },
            {
                "id": "verification",
                "icon": "🔍",
                "tag": "100% RESOURCE VERIFICATION",
                "tag_color": "#EC4899",
                "title": "Kaise Pata Chale Ga Ke Server Ke Resources Hi Real Mein Use Ho Rahe Hain?",
                "summary": "4 aisi thos daleelein jin se aap verify kar sakte hain ke laptop par 0% load hai aur sab kuch Server PC ka GPU/CPU/RAM hi use kar raha hai.",
                "points": [
                    ("📊 1. Client Screen Par Live Telemetry ('⚡ Active Job' Tab)",
                     "Job chalte waqt Active Job screen par server ke live vitals dekhein:\n"
                     "• REMOTE CPU LOAD: Server PC ke processor ka live percentage (har second update hota hai).\n"
                     "• REMOTE RAM USED: Server PC ki physical RAM ki live consumption (e.g. '14.2 GB / 32.0 GB').\n"
                     "• Live Console Stream: Server par chalne wali script ka har print statement, loss value, aur epoch live laptop par print hota hai."),

                    ("🖥️ 2. Server Screen Par Live Hardware Gauges ('Overview' & 'GPU Engine' Tabs)",
                     "Server PC ki screen par dekhein:\n"
                     "• GPU Utilization: Tensor calculations ya video rendering shuru hote hi meter 0% se jump karke 80%-99% par chala jata hai.\n"
                     "• GPU VRAM Usage: Dedicated memory live show hoti hai (e.g. '6.2 GB / 12.0 GB').\n"
                     "• GPU Temperature: Heavy kaam ke dauran GPU ka temperature increase hota hua dekhega (e.g. 42°C se 68°C-74°C)."),

                    ("📈 3. Windows Task Manager Comparison (Sab Se Bada Proof)",
                     "• Apne Laptop par Task Manager kholen (Ctrl + Shift + Esc): Laptop ka CPU load sirf 1% se 3% hoga, GPU 0% hoga aur battery safe rahegi.\n"
                     "• Server PC par Task Manager kholen: Wahan 'python.exe' ya 'ffmpeg.exe' 100% GPU compute aur heavy CPU load leti nazar aayegi!"),

                    ("🔥 4. PyTorch / AI Script CUDA Sanity Code",
                     "Apni 'train.py' ke bilkul shuru mein yeh code likhein:\n"
                     "import torch\n"
                     "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n"
                     "print(f'🔥 Training Running On: {device}')\n"
                     "if torch.cuda.is_available():\n"
                     "    print(f'🖥️ Server GPU: {torch.cuda.get_device_name(0)}')\n"
                     "    print(f'💾 Allocated VRAM: {torch.cuda.memory_allocated(0)/(1024**2):.2f} MB')\n"
                     "Jab yeh submit karenge, toh laptop screen par Server ke NVIDIA graphic card ka exact model name print hoga!")
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
                    ("⚡ Tareeqa 1: 1-Click P2P Tool (Sub se Asan & Fast)",
                     "'dist/DIRECT_CABLE_PAIRING.bat' ko dono PCs par Run as Administrator karein.\n"
                     "• Server PC par: '1' dabayein (Static IP: 192.168.99.1 set hogi aur firewall unblock hoga).\n"
                     "• Client Laptop par: '2' dabayein (Static IP: 192.168.99.2 set hogi).\n"
                     "• Client Studio mein: Server IP 192.168.99.1 daal kar Connect dabayein! (0.01s mein instant connect)."),

                    ("🔌 Tareeqa 2: Automatic Windows Cable (APIPA)",
                     "Dono PCs mein LAN wire lagayein. Windows khud 169.254.x.x IP assign karega.\n"
                     "• Server PC ke topbar par dekhein: wahan likhi '🔌 Cable IP' note karein (ya '📋 Copy IP' dabayein).\n"
                     "• Server topbar par '🛡️ Unblock Firewall' dabayein.\n"
                     "• Client Laptop ke Dashboard par banay box mein wahi IP daalein aur '⚡ Connect' dabayein."),

                    ("🛡️ Firewall Unblock Zaroori Hai",
                     "Windows Defender Firewall direct cable ko 'Public Network' samajh kar port 8000 block kar deta hai. Server par 'Unblock Firewall' button dabana ya 'FIX_FIREWALL.bat' chalana zaroori hai taake connection smoothly ho."),

                    ("💻 Slim Laptops (HP EliteBook, Dell wagera)",
                     "Agar laptop slim hai aur direct LAN port nahi hai, toh USB-to-LAN adapter ko USB port mein theek se lagayein taake Windows Ethernet controller ko pehchan sake.")
                ]
            },
            {
                "id": "ui_guide",
                "icon": "🖥️",
                "tag": "UI KA ISTEMAL (PAGE-BY-PAGE GUIDE)",
                "tag_color": "#F97316",
                "title": "Screen aur Buttons ko Kaise Use Karein",
                "summary": "Client Studio aur Server Node ki har screen ka mukammal tareeqa.",
                "points": [
                    ("📊 Client: Dashboard Overview", "Server connection status, latency, server ke CPU/RAM/GPU ke live gauges, aur quick-connect bar."),
                    ("🎬 Client: New Render Job Tab", "Task profile select karein (Video, Python, Batch, Universal), input file ya project folder choose karein, output naam dein, aur 'Submit Remote Job' dabayein."),
                    ("📡 Client: Active Job Monitor", "Job submit hote hi khulti hai. Is mein percentage bar, processing speed/FPS, server CPU/RAM usage meters, aur live terminal console streaming aati hai."),
                    ("📜 Client: Job History", "Tamam purani aur mukammal hone wali jobs ka table, execution time, aur direct 'Open Output Folder' ka button."),
                    ("⚡ Client: Performance Benchmarks", "5-step live hardware benchmarking suite. Standard video generate karke local laptop CPU vs remote server GPU ka speed comparison aur real speedup factor nikalta hai."),
                    ("⚙️ Client: Host & Settings", "Server IP address, port (8000), secret token, default resolutions, aur automated Watch Folder ka path configure karein."),
                    ("🖥️ Server: Overview Tab", "GPU utilization %, GPU VRAM used, GPU temperature, CPU multi-core load, active render job details, aur live activity events."),
                    ("⚙️ Server: GPU Engine Tab", "Hardware encoders (NVIDIA NVENC, QuickSync, AMF, CPU) ki detection, supported codecs, aur hardware status."),
                    ("📋 Server: Render Queue Tab", "Sabhi aane wali tasks ki live queue with client IP, status, progress, aur admin cancel control."),
                    ("🌐 Server: Network & Connections Tab", "Detected network adapters, active client sessions table with live client IPv4, port, live status, last activity, aur data transferred!"),
                    ("🕒 Server: Activity Logs Tab", "System-wide audit trail recording server lifecycle events, connections, aur task status.")
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
                    ("Q: Render hone ke baad file kahan save hoti hai?", "Aap ke laptop ke 'Downloads' folder mein file khud ba khud save ho jati hai. Kaam khatam hote hi 'Open Output Folder' ka button samne aa jata hai."),
                    ("Q: Connection Timeout kyun aa raha hai?", "Check karein: (1) Server PC par GPUWorkerServer.exe chalu ho, (2) Server par 'Unblock Firewall' dabaya ho, (3) Cable dono taraf theek lagi ho, (4) Server IP sahi daali ho."),
                    ("Q: Kya isme mera internet data kharch hoga?", "Nahi! Yeh saara data physical LAN cable ke zariye transfer hota hai, internet ka 1 byte bhi use nahi hota."),
                    ("Q: Kya mera dost mere GPU ko use kar sakta hai?", "Haan! Bas apne GPU PC par GPUWorkerServer.exe on chor dein. Aap ka dost cable laga kar apne laptop se heavy rendering aur AI models aaram se chala sakega.")
                ]
            }
        ]
    }
}
