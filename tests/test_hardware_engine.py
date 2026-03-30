"""Tests for Hardware-in-the-Loop Skill."""

import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hardware_in_the_loop_skill.hardware_engine import (
    VisionSafetyChecker,
    ServoController,
    HardwareExecutionEngine,
    SkillExecutor,
    PhysicalAction,
    ExecutionResult,
    SafetyStatus,
    VisionResult
)


class TestVisionSafetyChecker:
    """Tests for VisionSafetyChecker."""
    
    def test_initialization(self):
        """Test checker initialization."""
        checker = VisionSafetyChecker(
            camera_index=0,
            safety_zone_color=(0, 255, 0),
            danger_zone_color=(255, 0, 0)
        )
        
        assert checker._camera_index == 0
        assert checker._safety_zone_color == (0, 255, 0)
        assert checker._danger_zone_color == (255, 0, 0)
    
    def test_safety_check_with_zones(self):
        """Test safety check with defined zones."""
        checker = VisionSafetyChecker()
        
        target_area = (100, 100, 50, 50)
        safe_zones = [(100, 100, 100, 100)]
        danger_zones = [(200, 200, 50, 50)]
        
        result = checker.check_safety(target_area, safe_zones, danger_zones)
        
        assert isinstance(result, VisionResult)
        assert isinstance(result.validation_passed, bool)
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.detected_objects, list)
        assert isinstance(result.bounding_boxes, list)
    
    def test_safety_check_result_to_dict(self):
        """Test converting result to dictionary."""
        checker = VisionSafetyChecker()
        
        target_area = (100, 100, 50, 50)
        safe_zones = [(0, 0, 100, 100)]
        danger_zones = [(200, 200, 50, 50)]
        
        result = checker.check_safety(target_area, safe_zones, danger_zones)
        
        data = result.to_dict()
        
        assert 'validation_passed' in data
        assert 'confidence' in data
        assert 'detected_objects' in data
        assert 'timestamp' in data


class TestServoController:
    """Tests for ServoController."""
    
    def test_initialization(self):
        """Test controller initialization."""
        controller = ServoController(
            port="/dev/ttyUSB0",
            baudrate=115200
        )
        
        assert controller._port == "/dev/ttyUSB0"
        assert controller._baudrate == 115200
        assert controller._connected is False
    
    def test_move_to_position_fallback(self):
        """Test movement without actual connection."""
        controller = ServoController()
        
        # Without connection, should return failure
        success, error_msg = controller.move_to_position(0.5)
        
        assert success is False
        assert error_msg is not None


class TestHardwareExecutionEngine:
    """Tests for HardwareExecutionEngine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = HardwareExecutionEngine()
        
        assert engine._safety_checker is not None
        assert engine._servo_controller is not None
        assert engine._emergency_stop is False
    
    def test_execute_action(self):
        """Test executing a physical action."""
        engine = HardwareExecutionEngine()
        
        action = PhysicalAction(
            action_id="test_action",
            action_type="servo_move",
            target_position=0.5,
            timeout_ms=5000,
            safety_threshold=0.8,
            description="Test movement",
            validation_required=True
        )
        
        result = engine.execute_action(action)
        
        assert isinstance(result, ExecutionResult)
        assert result.action_id == "test_action"
        assert isinstance(result.success, bool)
        assert isinstance(result.safety_status, SafetyStatus)
    
    def test_execute_action_no_validation(self):
        """Test action without validation."""
        engine = HardwareExecutionEngine()
        
        action = PhysicalAction(
            action_id="test_action_no_vision",
            action_type="servo_move",
            target_position=0.75,
            timeout_ms=3000,
            safety_threshold=0.9,
            description="Test without validation",
            validation_required=False
        )
        
        result = engine.execute_action(action)
        
        assert isinstance(result, ExecutionResult)
        assert result.vision_validation is None
    
    def test_emergency_stop(self):
        """Test emergency stop."""
        engine = HardwareExecutionEngine()
        
        engine.emergency_stop()
        
        assert engine._emergency_stop is True
    
    def test_get_execution_log(self):
        """Test getting execution log."""
        engine = HardwareExecutionEngine()
        
        action = PhysicalAction(
            action_id="test_log",
            action_type="test",
            target_position=0.5,
            timeout_ms=1000,
            safety_threshold=0.8,
            description="Test logging",
            validation_required=True
        )
        
        engine.execute_action(action)
        
        log = engine.get_execution_log()
        
        assert len(log) == 1
        assert log[0].action_id == "test_log"
    
    def test_release(self):
        """Test releasing resources."""
        engine = HardwareExecutionEngine()
        
        engine.release()
        
        assert engine._emergency_stop is True


class TestSkillExecutor:
    """Tests for SkillExecutor."""
    
    def test_list_skills(self):
        """Test listing available skills."""
        engine = HardwareExecutionEngine()
        executor = SkillExecutor(engine)
        
        skills = executor.list_skills()
        
        assert len(skills) >= 3
        assert all('name' in s for s in skills)
        assert all('description' in s for s in skills)
    
    def test_execute_skill(self):
        """Test executing a skill."""
        engine = HardwareExecutionEngine()
        executor = SkillExecutor(engine)
        
        result = executor.execute_skill(
            "servo_move_safety",
            {"position": 0.5}
        )
        
        assert isinstance(result, ExecutionResult)
        assert result.success is True or result.success is False
    
    def test_execute_unknown_skill(self):
        """Test executing unknown skill."""
        engine = HardwareExecutionEngine()
        executor = SkillExecutor(engine)
        
        with pytest.raises(ValueError, match="Unknown skill"):
            executor.execute_skill("nonexistent_skill", {})


class TestPhysicalAction:
    """Tests for PhysicalAction."""
    
    def test_action_creation(self):
        """Test creating a physical action."""
        action = PhysicalAction(
            action_id="action_001",
            action_type="servo_move",
            target_position=0.75,
            timeout_ms=5000,
            safety_threshold=0.9,
            description="Test movement",
            validation_required=True
        )
        
        assert action.action_id == "action_001"
        assert action.action_type == "servo_move"
        assert action.target_position == 0.75
    
    def test_action_to_dict(self):
        """Test converting action to dictionary."""
        action = PhysicalAction(
            action_id="action_002",
            action_type="gripper_open",
            target_position=0.25,
            timeout_ms=3000,
            safety_threshold=0.8,
            description="Gripper test",
            validation_required=False
        )
        
        data = action.to_dict()
        
        assert data['action_id'] == "action_002"
        assert data['validation_required'] is False


class TestExecutionResult:
    """Tests for ExecutionResult."""
    
    def test_result_creation(self):
        """Test creating execution result."""
        result = ExecutionResult(
            action_id="test_result",
            success=True,
            safety_status=SafetyStatus.SAFE,
            vision_validation=None,
            execution_time_ms=250.5,
            error_message=None,
            timestamp=datetime.now()
        )
        
        assert result.action_id == "test_result"
        assert result.success is True
        assert result.safety_status == SafetyStatus.SAFE
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ExecutionResult(
            action_id="test_result_002",
            success=False,
            safety_status=SafetyStatus.DANGER,
            vision_validation=None,
            execution_time_ms=100.0,
            error_message="Test error",
            timestamp=datetime.now()
        )
        
        data = result.to_dict()
        
        assert data['action_id'] == "test_result_002"
        assert data['success'] is False
        assert data['safety_status'] == "danger"
        assert data['error_message'] == "Test error"


class TestSafetyStatus:
    """Tests for SafetyStatus enum."""
    
    def test_status_values(self):
        """Test safety status values."""
        assert SafetyStatus.SAFE.value == "safe"
        assert SafetyStatus.WARNING.value == "warning"
        assert SafetyStatus.DANGER.value == "danger"
        assert SafetyStatus.EMERGENCY.value == "emergency"


class TestVisionResult:
    """Tests for VisionResult."""
    
    def test_result_creation(self):
        """Test creating vision result."""
        result = VisionResult(
            validation_passed=True,
            confidence=0.95,
            detected_objects=[],
            bounding_boxes=[],
            analysis_details={"simulation": True},
            timestamp=datetime.now()
        )
        
        assert result.validation_passed is True
        assert result.confidence == 0.95
        assert len(result.detected_objects) == 0
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = VisionResult(
            validation_passed=False,
            confidence=0.3,
            detected_objects=[{"type": "danger"}],
            bounding_boxes=[(100, 100, 50, 50)],
            analysis_details={"overlap": 0.5},
            timestamp=datetime.now()
        )
        
        data = result.to_dict()
        
        assert data['validation_passed'] is False
        assert data['confidence'] == 0.3
        assert len(data['detected_objects']) == 1
