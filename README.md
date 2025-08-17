╔═════════════════════════════════════════════════════════════════╗
║                                                                 ║
║ ███╗   ██╗███████╗███╗   ███╗ █████╗ ██████╗  ██████╗ ████████║ ║
║ ████╗  ██║██╔════╝████╗ ████║██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝ ║
║ ██╔██╗ ██║█████╗  ██╔████╔██║███████║██████╔╝██║   ██║   ██║    ║
║ ██║╚██╗██║██╔══╝  ██║╚██╔╝██║██╔══██║██╔══██╗██║   ██║   ██║    ║
║ ██║ ╚████║███████╗██║ ╚═╝ ██║██║  ██║██████╔╝╚██████╔╝   ██║    ║
║ ╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝    ╚═╝    ║
║                                                                 ║
╚═════════════════════════════════════════════════════════════════╝

───────────────────────────────────────────────────────────────
 NEMABOT – Interactive C. elegans Neural Network Simulator
───────────────────────────────────────────────────────────────

 Nemabot is an experimental simulator designed to visualize and
 manipulate the nervous system of the nematode *Caenorhabditis
 elegans* in real time.

 Through direct neuron control and activity monitoring, Nemabot
 helps you understand how a simple network of neurons drives
 behavior and locomotion in a digital worm.

───────────────────────────────────────────────────────────────
 ▓ FEATURES
───────────────────────────────────────────────────────────────

 • Real-time graphing of selected neuron activity
 • Manual activation and inhibition of any neuron
 • Observe how neural signals produce movement
 • Educational tool to explore biological connectomes
 • Coded in Python with Pygame for graphics & input

───────────────────────────────────────────────────────────────
 ▓ FILE STRUCTURE
───────────────────────────────────────────────────────────────

 ▸ nemabot.py       – Main simulation loop
 ▸ connectome.py    – Neural logic & connectome data

 (optional folders)
 ▸ /data            – Raw neuron & connection data
 ▸ /examples        – Preset stim/test scenarios
 ▸ /tests           – Unit tests & diagnostics

───────────────────────────────────────────────────────────────
 ▓ HOW TO RUN
───────────────────────────────────────────────────────────────

 ▸ Step 1: Install dependencies

     pip install -r requirements.txt

 ▸ Step 2: Launch simulator

     python nemabot.py

 Requires:
 - Python 3.7+
 - Pygame

───────────────────────────────────────────────────────────────
 ▓ RESOURCES
───────────────────────────────────────────────────────────────

 ▸ WormAtlas ............ https://www.wormatlas.org/
 ▸ OpenWorm Project ...... http://www.openworm.org/
 ▸ Connectome Paper ...... XXX
 ▸ Pygame Documentation .. https://www.pygame.org/docs/

───────────────────────────────────────────────────────────────
 ▓ LICENSE
───────────────────────────────────────────────────────────────

 Nemabot is free software under GNU GPL v3 or later.

 Based in part on the original GoPiGo project architecture.
 © 2025 – Nemabot Project

 Read full license: https://www.gnu.org/licenses/gpl-3.0.txt