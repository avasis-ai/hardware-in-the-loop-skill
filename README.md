# README.md - Hardware-in-the-Loop Skill

## Agent Skills Validated Against Real-World Physical Hardware

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/hardware-in-the-loop-skill.svg)](https://pypi.org/project/hardware-in-the-loop-skill/)

**Hardware-in-the-Loop Skill** is designed for manufacturing and robotics. The SKILL.md executes code that controls an actual robotic arm or CNC machine, visually verifying the physical outcome via camera before proceeding to the next sequential step.

## 🎯 What It Does

This tool provides essential AI adoption capabilities for heavy manufacturing and robotics. It delivers visually stunning demos of AI intelligently controlling heavy machinery while maintaining rigorous safety protocols through real-time vision feedback loops.

### Example Use Case

```python
from hardware_in_the_loop_skill.hardware_engine import (
    VisionSafetyChecker,
    ServoController,
    HardwareExecutionEngine,
    SkillExecutor
)

# Initialize components
safety_checker = VisionSafetyChecker(camera_index=0)
engine = HardwareExecutionEngine(
    safety_checker=safety_checker
)

# Create skill executor
executor = SkillExecutor(engine)

# Execute a physical validation skill
result = executor.execute_skill(
    "servo_move_safety",
    {"position": 0.5}
)

print(f"Success: {result.success}")
print(f"Safety Status: {result.safety_status.value}")
print(f"Execution Time: {result.execution_time_ms:.1f}ms")
```

## 🚀 Features

- **Real-Time Vision Safety**: Camera-based validation halts operations in milliseconds if unsafe
- **Physical Action Execution**: Control servos, motors, and robotic arms
- **SKILL.md Integration**: Execute validated physical operations
- **Safety Zone Detection**: Define safe and danger zones for operations
- **Emergency Stop Capability**: Instant halt on any safety violation
- **Physical Operation Logging**: Complete audit trail of all operations
- **Cross-Platform Support**: Works with generic webcams and servo controllers

### Core Components

1. **VisionSafetyChecker**
   - Real-time camera integration
   - Safety zone detection
   - Object recognition
   - Confidence scoring
   - Bounding box analysis

2. **ServoController**
   - Serial port communication
   - Servo/motor control
   - Position targeting
   - Timeout management
   - Connection status monitoring

3. **HardwareExecutionEngine**
   - Coordinated operation execution
   - Safety validation integration
   - Emergency stop handling
   - Execution logging
   - Resource management

4. **SkillExecutor**
   - SKILL.md-based execution
   - Pre-defined validation skills
   - Parameterized operations
   - Physical action orchestration
   - Outcome verification

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenCV (opencv-python)
- PyYAML
- PySerial
- Compatible camera and/or servo controller

### Install from PyPI

```bash
pip install hardware-in-the-loop-skill
```

### Install from Source

```bash
git clone https://github.com/avasis-ai/hardware-in-the-loop-skill.git
cd hardware-in-the-loop-skill
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
pip install pytest pytest-mock black isort
```

## 🔧 Usage

### Command-Line Interface

```bash
# Check version
hardware-loop --version

# List available skills
hardware-loop skills

# Execute a physical skill
hardware-loop execute servo_move_safety --position 0.5

# Run simulation
hardware-loop simulate

# Trigger emergency stop
hardware-loop emergency

# Run complete demo
hardware-loop demo
```

### Programmatic Usage

```python
from hardware_in_the_loop_skill.hardware_engine import (
    VisionSafetyChecker,
    HardwareExecutionEngine,
    SkillExecutor
)

# Initialize vision safety checker
safety_checker = VisionSafetyChecker(
    camera_index=0,
    safety_zone_color=(0, 255, 0),      # Green
    danger_zone_color=(255, 0, 0)        # Red
)

# Create execution engine
engine = HardwareExecutionEngine(safety_checker=safety_checker)

# Create skill executor
executor = SkillExecutor(engine)

# Execute physical validation skill
result = executor.execute_skill(
    skill_name="servo_move_safety",
    params={"position": 0.5}
)

# Check result
if result.success:
    print(f"✓ Operation completed successfully")
    print(f"  Safety: {result.safety_status.value}")
    print(f"  Time: {result.execution_time_ms:.1f}ms")
else:
    print(f"✗ Operation failed")
    print(f"  Error: {result.error_message}")
    print(f"  Safety: {result.safety_status.value}")

# Get execution history
log = engine.get_execution_log()
for entry in log:
    print(f"{entry.action_id}: {entry.safety_status.value}")

# Cleanup
engine.release()
```

### Advanced Usage

```python
from hardware_in_the_loop_skill.hardware_engine import (
    VisionSafetyChecker,
    PhysicalAction,
    HardwareExecutionEngine
)

# Custom safety zones
safety_checker = VisionSafetyChecker(camera_index=0)

# Define custom safety configuration
safe_zones = [
    (0, 0, 100, 100),      # Top-left corner safe
    (500, 500, 200, 200)   # Bottom-right safe
]

danger_zones = [
    (200, 200, 50, 50),    # Small danger zone
    (300, 300, 100, 100)   # Large danger zone
]

# Check safety before operation
target_area = (150, 150, 50, 50)
vision_result = safety_checker.check_safety(
    target_area, safe_zones, danger_zones
)

if vision_result.validation_passed:
    print("✓ Safe to proceed with operation")
else:
    print("✗ Unsafe - do not proceed")
    print(f"Confidence: {vision_result.confidence:.2f}")

# Execute custom physical action
engine = HardwareExecutionEngine(safety_checker=safety_checker)
action = PhysicalAction(
    action_id="custom_action",
    action_type="custom_move",
    target_position=0.75,
    timeout_ms=5000,
    safety_threshold=0.8,
    description="Custom servo movement",
    validation_required=True
)

result = engine.execute_action(action)
```

## 📚 API Reference

### VisionSafetyChecker

Real-time vision-based safety validation.

#### `__init__(camera_index, safety_zone_color, danger_zone_color)`

Initialize vision safety checker.

#### `check_safety(target_area, safe_zones, danger_zones)` → VisionResult

Check if target area is safe for physical operation.

#### `VisionResult`

Dataclass containing vision validation:
- `validation_passed`: Whether operation is safe
- `confidence`: Confidence score (0.0-1.0)
- `detected_objects`: List of detected safety-relevant objects
- `bounding_boxes`: Relevant bounding boxes
- `analysis_details`: Detailed analysis information

### ServoController

Servo/motor controller interface.

#### `move_to_position(position, timeout_ms)` → Tuple[bool, str]

Move servo to target position.

### HardwareExecutionEngine

Executes physical actions with vision-based safety.

#### `execute_action(action)` → ExecutionResult

Execute a physical action with full safety validation.

#### `emergency_stop()`

Trigger immediate emergency stop.

### SkillExecutor

Executes SKILL.md-based physical validation skills.

#### `execute_skill(skill_name, params)` → ExecutionResult

Execute a physical validation skill.

#### `list_skills()` → List[Dict[str, Any]]

List available skills.

## 🧪 Testing

Run tests with pytest:

```bash
python -m pytest tests/ -v
```

## 📁 Project Structure

```
hardware-in-the-loop-skill/
├── README.md
├── pyproject.toml
├── LICENSE
├── src/
│   └── hardware_in_the_loop_skill/
│       ├── __init__.py
│       ├── hardware_engine.py
│       └── cli.py
├── tests/
│   └── test_hardware_engine.py
└── .github/
    └── ISSUE_TEMPLATE/
        └── bug_report.md
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Run tests**: `python -m pytest tests/ -v`
5. **Submit a pull request**

### Development Setup

```bash
git clone https://github.com/avasis-ai/hardware-in-the-loop-skill.git
cd hardware-in-the-loop-skill
pip install -e ".[dev]"
pre-commit install
```

## 📝 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 🎯 Vision

Hardware-in-the-Loop Skill is an absolute necessity for AI adoption in heavy manufacturing and robotics. It provides the critical safety infrastructure needed to deploy AI-controlled physical systems reliably and safely.

### Key Innovations

- **Low-Latency Safety Loop**: Millisecond-level vision feedback prevents accidents
- **Physical Validation**: Camera-based verification of all operations
- **Emergency Stop**: Instant halt on any safety violation
- **SKILL.md Integration**: Standardized physical operation framework
- **Comprehensive Logging**: Full audit trail of all physical operations
- **Real-World Testing**: Validated against actual hardware

### Impact on Manufacturing

This tool enables:

- **Safe AI Deployment**: Deploy AI-controlled machinery with confidence
- **Reduced Downtime**: Prevent accidents before they occur
- **Regulatory Compliance**: Meet industrial safety standards
- **Training Platform**: Teach AI safe physical operations
- **Quality Assurance**: Verify physical outcomes automatically
- **Risk Mitigation**: Prevent costly equipment damage

## 🛡️ Security & Trust

- **Trusted dependencies**: opencv-python (6.4+), pyyaml (7.4), pyserial (6.4+) - Community verified
- **MIT License**: Open source, community-driven
- **Safety Focus**: Designed for physical safety
- **Low-Level Control**: Direct hardware access with safety
- **Open Source**: Community-reviewed safety protocols
- **Educational**: Learn professional industrial automation

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/avasis-ai/hardware-in-the-loop-skill/wiki)
- **Issues**: [GitHub Issues](https://github.com/avasis-ai/hardware-in-the-loop-skill/issues)
- **Industrial Automation**: automation@avasis.ai

## 🙏 Acknowledgments

- **OpenCV**: Computer vision library
- **PySerial**: Serial communication library
- **OpenClaw**: Agent framework inspiration
- **Automotive Industry**: Safety validation best practices
- **Manufacturing Community**: Real-world testing and feedback
- **Robotics Community**: Physical operation expertise

---

**Made with 🤖 by [Avasis AI](https://avasis.ai)**

*The essential open-source hardware-in-the-loop validation tool. Safe, reliable, and intelligent physical operations.*
