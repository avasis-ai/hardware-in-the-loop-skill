"""Command-line interface for Hardware-in-the-Loop Skill."""

import click
import json
from typing import Optional

from .hardware_engine import (
    VisionSafetyChecker,
    ServoController,
    HardwareExecutionEngine,
    SkillExecutor,
    PhysicalAction,
    ExecutionResult,
    SafetyStatus
)


@click.group()
@click.version_option(version="0.1.0", prog_name="hardware-loop")
def main() -> None:
    """Hardware-in-the-Loop Skill - Physical validation for robotics and manufacturing."""
    pass


@main.command()
def skills() -> None:
    """List available physical validation skills."""
    # Initialize executor with default engine
    engine = HardwareExecutionEngine()
    executor = SkillExecutor(engine)
    
    skills = executor.list_skills()
    
    click.echo(f"\n🤖 Available Physical Validation Skills")
    click.echo("=" * 60)
    
    for skill in skills:
        click.echo(f"\n  {skill['name']}")
        click.echo(f"    Type: {skill['action_type']}")
        click.echo(f"    Description: {skill['description']}")


@main.command()
@click.argument("skill_name")
@click.option("--position", "-p", default=0.5, help="Target position (0.0-1.0)")
def execute(skill_name: str, position: float) -> None:
    """Execute a physical validation skill."""
    # Initialize engine
    engine = HardwareExecutionEngine()
    executor = SkillExecutor(engine)
    
    try:
        params = {"position": position}
        result = executor.execute_skill(skill_name, params)
        
        click.echo(f"\n📋 Execution Result: {result.action_id}")
        click.echo("=" * 60)
        click.echo(f"Skill: {skill_name}")
        click.echo(f"Success: {'✅' if result.success else '❌'}")
        click.echo(f"Safety Status: {result.safety_status.value}")
        click.echo(f"Execution Time: {result.execution_time_ms:.1f}ms")
        
        if result.vision_validation:
            click.echo(f"\n📷 Vision Validation:")
            click.echo(f"   Passed: {'✅' if result.vision_validation.validation_passed else '❌'}")
            click.echo(f"   Confidence: {result.vision_validation.confidence:.2f}")
            click.echo(f"   Detected Objects: {len(result.vision_validation.detected_objects)}")
        
        if result.error_message:
            click.echo(f"\n⚠️ Error: {result.error_message}")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}")


@main.command()
def simulate() -> None:
    """Run a physical operation simulation."""
    click.echo("\n🧪 Hardware-in-the-Loop Simulation")
    click.echo("=" * 60)
    
    # Initialize engine
    engine = HardwareExecutionEngine()
    executor = SkillExecutor(engine)
    
    # Execute multiple actions
    actions = [
        ("servo_move_safety", 0.3),
        ("gripper_validation", 0.7),
        ("object_pickup", 0.5)
    ]
    
    click.echo("\n📊 Executing Physical Actions:")
    click.echo("-" * 60)
    
    for skill_name, position in actions:
        click.echo(f"\nExecuting: {skill_name} at position {position}")
        
        try:
            result = executor.execute_skill(skill_name, {"position": position})
            
            status_icon = "✅" if result.success else "❌"
            safety_icon = "🟢" if result.safety_status == SafetyStatus.SAFE else "🟡" if result.safety_status == SafetyStatus.WARNING else "🔴"
            
            click.echo(f"   {status_icon} Success: {result.success}")
            click.echo(f"   {safety_icon} Safety: {result.safety_status.value}")
            click.echo(f"   Time: {result.execution_time_ms:.1f}ms")
            
        except ValueError as e:
            click.echo(f"   ❌ Error: {e}")
    
    click.echo(f"\n{'=' * 60}")
    click.echo(f"Simulation complete!")


@main.command()
def emergency() -> None:
    """Trigger emergency stop."""
    engine = HardwareExecutionEngine()
    engine.emergency_stop()
    
    click.echo("\n🚨 Emergency Stop Triggered")
    click.echo("=" * 60)
    click.echo("All physical operations have been halted.")


@main.command()
def demo() -> None:
    """Run a complete demo."""
    click.echo("\n🎮 Hardware-in-the-Loop Skill Demo")
    click.echo("=" * 60)
    click.echo("\nThis demo simulates physical operations with vision-based safety validation.")
    
    # Initialize engine
    engine = HardwareExecutionEngine()
    executor = SkillExecutor(engine)
    
    # List available skills
    skills = executor.list_skills()
    click.echo(f"\n📋 Available Skills ({len(skills)}):")
    for skill in skills:
        click.echo(f"  • {skill['name']}")
    
    # Run simulation
    click.echo("\n🏭 Running Physical Operations Simulation...")
    
    engine2 = HardwareExecutionEngine()
    executor2 = SkillExecutor(engine2)
    
    # Execute several actions
    for i in range(3):
        skill_name = list(executor2._skills.keys())[i % len(executor2._skills)]
        position = 0.3 + (i * 0.2)
        
        click.echo(f"\n   Action {i+1}: {skill_name} at {position:.1f}")
        
        result = executor2.execute_skill(skill_name, {"position": position})
        
        status = "✓" if result.success else "✗"
        click.echo(f"      Status: {status} {result.safety_status.value}")
        click.echo(f"      Time: {result.execution_time_ms:.1f}ms")
    
    # Show execution log
    log = engine2.get_execution_log()
    
    click.echo(f"\n📊 Execution Log ({len(log)} actions):")
    for entry in log:
        icon = "✓" if entry.success else "✗"
        click.echo(f"  {icon} {entry.action_id}: {entry.safety_status.value}")


@main.command()
def help_text() -> None:
    """Show extended help information."""
    click.echo("""
Hardware-in-the-Loop Skill - Physical validation for robotics and manufacturing

FEATURES:
  • Vision-based safety validation
  • Real-time camera monitoring
  • Servo/motor control integration
  • Emergency stop capability
  • Physical operation logging
  • SKILL.md skill execution

USAGE:
  hardware-loop COMMAND [OPTIONS]
  
Commands:
  skills        List available physical validation skills
  execute       Execute a physical validation skill
  simulate      Run a physical operation simulation
  emergency     Trigger emergency stop
  demo          Run complete demo
  config        Show configuration

OPTIONS:
  --skill, -s   Skill name to execute
  --position, -p  Target position (0.0-1.0)

EXAMPLES:
  hardware-loop skills
  hardware-loop execute servo_move_safety --position 0.5
  hardware-loop simulate
  hardware-loop demo

For more information, visit: https://github.com/avasis-ai/hardware-in-the-loop-skill
    """)


def main_entry() -> None:
    """Main entry point."""
    main(prog_name="hardware-loop")


if __name__ == "__main__":
    main_entry()
