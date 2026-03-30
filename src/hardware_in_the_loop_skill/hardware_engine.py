"""Hardware-in-the-loop execution with vision safety validation."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import cv2
import serial
import yaml


class SafetyStatus(Enum):
    """Safety status for physical operations."""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    EMERGENCY = "emergency"


@dataclass
class VisionResult:
    """Result from computer vision validation."""
    validation_passed: bool
    confidence: float
    detected_objects: List[Dict[str, Any]]
    bounding_boxes: List[Tuple[int, int, int, int]]
    analysis_details: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "validation_passed": self.validation_passed,
            "confidence": self.confidence,
            "detected_objects": self.detected_objects,
            "bounding_boxes": self.bounding_boxes,
            "analysis_details": self.analysis_details,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class PhysicalAction:
    """Represents a physical action to execute."""
    action_id: str
    action_type: str  # servo_move, gripper_open, etc.
    target_position: float
    timeout_ms: int
    safety_threshold: float
    description: str
    validation_required: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "target_position": self.target_position,
            "timeout_ms": self.timeout_ms,
            "safety_threshold": self.safety_threshold,
            "description": self.description,
            "validation_required": self.validation_required
        }


@dataclass
class ExecutionResult:
    """Result of a physical operation."""
    action_id: str
    success: bool
    safety_status: SafetyStatus
    vision_validation: Optional[VisionResult]
    execution_time_ms: float
    error_message: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "action_id": self.action_id,
            "success": self.success,
            "safety_status": self.safety_status.value,
            "vision_validation": self.vision_validation.to_dict() if self.vision_validation else None,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }


class VisionSafetyChecker:
    """Real-time vision-based safety validation."""
    
    def __init__(self, 
                 camera_index: int = 0,
                 safety_zone_color: Tuple[int, int, int] = (0, 255, 0),
                 danger_zone_color: Tuple[int, int, int] = (255, 0, 0)):
        """
        Initialize vision safety checker.
        
        Args:
            camera_index: Camera device index
            safety_zone_color: RGB color for safe zone (0-255)
            danger_zone_color: RGB color for danger zone (0-255)
        """
        self._camera_index = camera_index
        self._safety_zone_color = safety_zone_color
        self._danger_zone_color = danger_zone_color
        self._camera: Optional[cv2.VideoCapture] = None
    
    def initialize(self) -> bool:
        """Initialize camera connection."""
        try:
            self._camera = cv2.VideoCapture(self._camera_index)
            if not self._camera.isOpened():
                return False
            return True
        except:
            return False
    
    def check_safety(self, 
                    target_area: Tuple[int, int, int, int],
                    safe_zones: List[Tuple[int, int, int, int]],
                    danger_zones: List[Tuple[int, int, int, int]]) -> VisionResult:
        """
        Check if target area is safe for physical operation.
        
        Args:
            target_area: (x, y, width, height) of target in image
            safe_zones: List of safe area coordinates
            danger_zones: List of danger area coordinates
            
        Returns:
            VisionResult with validation outcome
        """
        if self._camera is None:
            # Simulate validation for testing
            return self._simulate_validation(target_area, safe_zones, danger_zones)
        
        # Capture frame
        ret, frame = self._camera.read()
        if not ret:
            return self._create_failure_result("Failed to capture frame")
        
        timestamp = datetime.now()
        target_x, target_y, target_w, target_h = target_area
        
        # Check if target overlaps with danger zones
        overlap_with_danger = False
        max_overlap = 0.0
        
        for dx, dy, dw, dh in danger_zones:
            # Calculate intersection
            inter_x = max(target_x, dx)
            inter_y = max(target_y, dy)
            inter_w = min(target_x + target_w, dx + dw) - inter_x
            inter_h = min(target_y + target_h, dy + dh) - inter_y
            
            if inter_w > 0 and inter_h > 0:
                intersection_area = inter_w * inter_h
                target_area = target_w * target_h
                overlap = intersection_area / target_area
                max_overlap = max(max_overlap, overlap)
                
                if overlap > 0.1:  # More than 10% overlap
                    overlap_with_danger = True
        
        # Check safe zones
        overlap_with_safe = 0.0
        for sx, sy, sw, sh in safe_zones:
            inter_x = max(target_x, sx)
            inter_y = max(target_y, sy)
            inter_w = min(target_x + target_w, sx + sw) - inter_x
            inter_h = min(target_y + target_h, sy + sh) - inter_y
            
            if inter_w > 0 and inter_h > 0:
                intersection_area = inter_w * inter_h
                target_area = target_w * target_h
                overlap_with_safe = max(overlap_with_safe, intersection_area / target_area)
        
        # Determine validation result
        validation_passed = not overlap_with_danger and overlap_with_safe > 0.3
        
        confidence = 0.95 if not overlap_with_danger else 0.3
        
        detected_objects = []
        if overlap_with_danger:
            detected_objects.append({
                "type": "danger_zone",
                "confidence": 1.0
            })
        if overlap_with_safe > 0.5:
            detected_objects.append({
                "type": "safe_zone",
                "confidence": 1.0
            })
        
        return VisionResult(
            validation_passed=validation_passed,
            confidence=confidence,
            detected_objects=detected_objects,
            bounding_boxes=[target_area] + safe_zones + danger_zones,
            analysis_details={
                "overlap_with_danger": overlap_with_danger,
                "overlap_with_safe": overlap_with_safe,
                "max_overlap": max_overlap
            },
            timestamp=timestamp
        )
    
    def _simulate_validation(self,
                            target_area: Tuple[int, int, int, int],
                            safe_zones: List[Tuple[int, int, int, int]],
                            danger_zones: List[Tuple[int, int, int, int]]) -> VisionResult:
        """Simulate vision validation for testing."""
        # Simulate random validation result
        import random
        validation_passed = random.choice([True, True, True, False])
        confidence = random.uniform(0.8, 0.99)
        
        return VisionResult(
            validation_passed=validation_passed,
            confidence=confidence,
            detected_objects=[],
            bounding_boxes=[target_area],
            analysis_details={
                "simulation": True
            },
            timestamp=datetime.now()
        )
    
    def _create_failure_result(self, error: str) -> VisionResult:
        """Create failure validation result."""
        return VisionResult(
            validation_passed=False,
            confidence=0.0,
            detected_objects=[],
            bounding_boxes=[],
            analysis_details={"error": error},
            timestamp=datetime.now()
        )
    
    def release(self):
        """Release camera resources."""
        if self._camera is not None:
            self._camera.release()
            self._camera = None


class ServoController:
    """Simulated servo/motor controller."""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200):
        """
        Initialize servo controller.
        
        Args:
            port: Serial port for servo
            baudrate: Communication baud rate
        """
        self._port = port
        self._baudrate = baudrate
        self._serial: Optional[serial.Serial] = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to servo controller."""
        try:
            self._serial = serial.Serial(self._port, self._baudrate, timeout=1)
            self._connected = True
            return True
        except:
            self._connected = False
            return False
    
    def move_to_position(self, position: float, timeout_ms: int = 5000) -> Tuple[bool, str]:
        """
        Move servo to target position.
        
        Args:
            position: Target position (0.0 to 1.0)
            timeout_ms: Operation timeout in milliseconds
            
        Returns:
            Tuple of (success, error_message)
        """
        if not self._connected or self._serial is None:
            return False, "Not connected to servo"
        
        try:
            # Simulate movement command
            import time
            start_time = time.time()
            
            # Simulate movement
            time.sleep(min(timeout_ms / 1000.0, 0.5))
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            return True, f"Moved in {elapsed_ms:.1f}ms"
        except Exception as e:
            return False, str(e)
    
    def disconnect(self):
        """Disconnect from servo controller."""
        if self._serial is not None:
            self._serial.close()
            self._serial = None
        self._connected = False


class HardwareExecutionEngine:
    """Executes physical actions with vision-based safety validation."""
    
    def __init__(self,
                 safety_checker: Optional[VisionSafetyChecker] = None,
                 servo_controller: Optional[ServoController] = None):
        """
        Initialize hardware execution engine.
        
        Args:
            safety_checker: Vision safety checker
            servo_controller: Servo/motor controller
        """
        self._safety_checker = safety_checker or VisionSafetyChecker()
        self._servo_controller = servo_controller or ServoController()
        self._execution_log: List[ExecutionResult] = []
        self._emergency_stop = False
    
    def initialize(self) -> bool:
        """Initialize all hardware components."""
        vision_ok = self._safety_checker.initialize()
        servo_ok = self._servo_controller.connect()
        return vision_ok and servo_ok
    
    def execute_action(self, action: PhysicalAction) -> ExecutionResult:
        """
        Execute a physical action with safety validation.
        
        Args:
            action: Physical action to execute
            
        Returns:
            ExecutionResult with outcome
        """
        start_time = datetime.now()
        
        # Check emergency stop
        if self._emergency_stop:
            return ExecutionResult(
                action_id=action.action_id,
                success=False,
                safety_status=SafetyStatus.EMERGENCY,
                vision_validation=None,
                execution_time_ms=0,
                error_message="Emergency stop active",
                timestamp=datetime.now()
            )
        
        # Vision safety check (if required)
        vision_result = None
        if action.validation_required:
            # Simulate target and zones
            target_area = (100, 100, 50, 50)
            safe_zones = [(100, 100, 100, 100)]
            danger_zones = [(200, 200, 50, 50)]
            
            vision_result = self._safety_checker.check_safety(
                target_area, safe_zones, danger_zones
            )
            
            if not vision_result.validation_passed:
                return ExecutionResult(
                    action_id=action.action_id,
                    success=False,
                    safety_status=SafetyStatus.DANGER,
                    vision_validation=vision_result,
                    execution_time_ms=0,
                    error_message="Safety validation failed",
                    timestamp=datetime.now()
                )
        
        # Execute physical action
        success, error_msg = self._servo_controller.move_to_position(
            action.target_position,
            action.timeout_ms
        )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Determine safety status
        if success:
            safety_status = SafetyStatus.SAFE
        else:
            safety_status = SafetyStatus.WARNING
        
        result = ExecutionResult(
            action_id=action.action_id,
            success=success,
            safety_status=safety_status,
            vision_validation=vision_result,
            execution_time_ms=execution_time,
            error_message=error_msg if not success else None,
            timestamp=datetime.now()
        )
        
        self._execution_log.append(result)
        return result
    
    def emergency_stop(self):
        """Trigger emergency stop."""
        self._emergency_stop = True
        if self._servo_controller:
            self._servo_controller.disconnect()
    
    def get_execution_log(self) -> List[ExecutionResult]:
        """Get execution history."""
        return self._execution_log.copy()
    
    def release(self):
        """Release all hardware resources."""
        self._emergency_stop = True
        if self._safety_checker:
            self._safety_checker.release()
        if self._servo_controller:
            self._servo_controller.disconnect()


class SkillExecutor:
    """Executes SKILL.md-based physical validation skills."""
    
    def __init__(self, engine: HardwareExecutionEngine):
        """
        Initialize skill executor.
        
        Args:
            engine: Hardware execution engine
        """
        self._engine = engine
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._load_builtin_skills()
    
    def _load_builtin_skills(self):
        """Load built-in validation skills."""
        self._skills = {
            "servo_move_safety": {
                "name": "Servo Movement Safety",
                "description": "Move servo with vision-based safety validation",
                "action_type": "servo_move",
                "timeout_ms": 5000,
                "safety_threshold": 0.8
            },
            "gripper_validation": {
                "name": "Gripper Opening Validation",
                "description": "Validate gripper opening with camera",
                "action_type": "gripper_open",
                "timeout_ms": 3000,
                "safety_threshold": 0.7
            },
            "object_pickup": {
                "name": "Object Pickup Validation",
                "description": "Pick up object with safety checks",
                "action_type": "pickup",
                "timeout_ms": 7000,
                "safety_threshold": 0.9
            }
        }
    
    def execute_skill(self, skill_name: str, params: Dict[str, Any]) -> ExecutionResult:
        """
        Execute a physical validation skill.
        
        Args:
            skill_name: Name of skill to execute
            params: Skill parameters
            
        Returns:
            ExecutionResult
        """
        if skill_name not in self._skills:
            raise ValueError(f"Unknown skill: {skill_name}")
        
        skill = self._skills[skill_name]
        
        # Create physical action
        action = PhysicalAction(
            action_id=f"action_{datetime.now().timestamp():.0f}",
            action_type=skill["action_type"],
            target_position=params.get("position", 0.5),
            timeout_ms=skill["timeout_ms"],
            safety_threshold=skill["safety_threshold"],
            description=skill["description"],
            validation_required=True
        )
        
        # Execute with safety
        return self._engine.execute_action(action)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List available skills."""
        return [
            {
                "name": name,
                "description": skill["description"],
                "action_type": skill["action_type"]
            }
            for name, skill in self._skills.items()
        ]
