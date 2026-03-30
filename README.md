<div align="center">

<img src="https://img.shields.io/badge/Language-Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/License-MIT-4CC61E?style=flat-square&logo=osi&logoColor=white" alt="License">
<img src="https://img.shields.io/badge/Version-0.1.0-3B82F6?style=flat-square" alt="Version">
<img src="https://img.shields.io/badge/PRs_Welcome-3B82F6?style=flat-square" alt="PRs Welcome">

<br/>
<br/>

<h3>Agent skills validated against real-world physical hardware.</h3>

<i>Designed for manufacturing and robotics, the SKILL.md executes code that controls an actual robotic arm or CNC machine, visually verifying the physical outcome via camera before proceeding to the next sequential step.</i>

<br/>
<br/>

<a href="#installation"><b>Install</b></a>
&ensp;·&ensp;
<a href="#quick-start"><b>Quick Start</b></a>
&ensp;·&ensp;
<a href="#features"><b>Features</b></a>
&ensp;·&ensp;
<a href="#architecture"><b>Architecture</b></a>
&ensp;·&ensp;
<a href="#demo"><b>Demo</b></a>

</div>

---
## Installation

```bash
pip install hardware-in-the-loop-skill
```

## Quick Start

```bash
hardware-in-the-loop-skill --help
```

## Architecture

```
hardware-in-the-loop-skill/
├── pyproject.toml
├── README.md
├── src/
│   └── hardware_in_the_loop_skill/
│       ├── __init__.py
│       └── cli.py
├── tests/
│   └── test_hardware_in_the_loop_skill.py
└── AGENTS.md
```

## Demo

<!-- Add screenshot or GIF here -->

> Coming soon

## Development

```bash
git clone https://github.com/avasis-ai/hardware-in-the-loop-skill
cd hardware-in-the-loop-skill
pip install -e .
pytest tests/ -v
```

## Links

- **Repository**: https://github.com/avasis-ai/hardware-in-the-loop-skill
- **PyPI**: https://pypi.org/project/hardware-in-the-loop-skill
- **Issues**: https://github.com/avasis-ai/hardware-in-the-loop-skill/issues

---

<div align="center">
<i>Part of the <a href="https://github.com/avasis-ai">AVASIS AI</a> open-source ecosystem</i>
</div>
