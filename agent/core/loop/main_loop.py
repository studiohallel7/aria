"""
Main Loop - Core autonomous agent loop implementation.
Handles the continuous cycle of observation, decision, action, and reflection.
"""

import time
import random
from datetime import datetime
from typing import Optional, Dict, Any, List

from core.state.agent_state import (
    AgentStatus,
    AgentState,
    OperationMode,
    get_current_state,
    save_current_state,
    get_context_manager,
    save_context_manager,
)
from core.cognition.thinking import ThinkingEngine
from core.cognition.planner import Planner
from core.cognition.reflection import ReflectionEngine
from core.cognition.intention import IntentionManager
from core.autonomy.mode_manager import ModeManager
from core.autonomy.triggers import TriggerEvaluator
from infra.monitoring.logger import AgentLogger


class AgentLoop:
    """Main autonomous agent loop."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = AgentLogger()
        
        # Initialize components
        self.thinking = ThinkingEngine()
        self.planner = Planner()
        self.reflection = ReflectionEngine()
        self.intention = IntentionManager()
        self.mode_manager = ModeManager()
        self.triggers = TriggerEvaluator()
        
        # State
        self.running = True
        self.cycle_count = 0
        self.last_cycle_time: Optional[datetime] = None
        
        # Configuration
        self.cycle_interval = 5  # seconds
        self.max_cycles_before_rest = 100
        
    def run(self) -> None:
        """Run the main agent loop."""
        self.logger.info("Starting agent loop")
        
        while self.running:
            try:
                self._execute_cycle()
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Cycle error: {e}")
                self._handle_error(e)
                
            # Wait for next cycle
            time.sleep(self.cycle_interval)
    
    def _execute_cycle(self) -> None:
        """Execute a single cycle of the agent loop."""
        cycle_start = datetime.now()
        
        # Load current state
        state = get_current_state()
        ctx = get_context_manager()
        
        # Update cycle info
        self.cycle_count += 1
        state.cycle_count = self.cycle_count
        state.last_cycle_time = cycle_start
        
        if self.verbose:
            print(f"\n{'='*50}")
            print(f"Cycle {self.cycle_count} started at {cycle_start.strftime('%H:%M:%S')}")
            print(f"State: {state.state.value} | Mode: {state.mode.value}")
            print(f"{'='*50}")
        
        # Step 1: Observe internal and external state
        if self.verbose:
            print("\n[1] Observing state...")
        state.state = AgentState.THINKING
        observations = self._observe(state, ctx)
        
        # Step 2: Check API consumption and availability
        if self.verbose:
            print("[2] Checking API availability...")
        api_status = self._check_api_status()
        
        # Step 3: Check user tasks
        if self.verbose:
            print("[3] Checking user tasks...")
        pending_tasks = ctx.get_pending_tasks()
        
        # Step 4: Evaluate triggers
        if self.verbose:
            print("[4] Evaluating triggers...")
        triggered = self.triggers.evaluate(observations, pending_tasks, state)
        
        # Step 5: Define intention
        if self.verbose:
            print("[5] Defining intention...")
        intention = self.intention.decide(
            state=state,
            observations=observations,
            triggers=triggered,
            has_user_tasks=len(pending_tasks) > 0,
        )
        
        if self.verbose:
            print(f"Intention: {intention}")
        
        # Step 6-7: Plan and execute based on intention
        if intention != "none":
            if self.verbose:
                print(f"[6-7] Planning and executing: {intention}...")
            
            if intention == "user_task" and pending_tasks:
                state.state = AgentState.EXECUTING
                state.current_task = pending_tasks[0]["task"]
                result = self._execute_user_task(pending_tasks[0], state, ctx)
            elif intention == "explore":
                state.state = AgentState.EXPLORING
                result = self._execute_exploration(state, ctx)
            elif intention == "learn":
                state.state = AgentState.THINKING
                result = self._execute_learning(state, ctx)
            elif intention == "reflect":
                state.state = AgentState.THINKING
                result = self._execute_reflection(state, ctx)
            else:
                result = {"status": "no_action"}
            
            # Step 8: Register
            if self.verbose:
                print("[8] Registering...")
            self._register(cycle_start, intention, result, state, ctx)
            
            # Step 9: Reflect
            if self.verbose:
                print("[9] Reflecting...")
            self._reflect(result, state, ctx)
        else:
            if self.verbose:
                print("[6-10] No action needed, waiting...")
            state.state = AgentState.IDLE
        
        # Save state
        save_current_state(state)
        save_context_manager(ctx)
        
        # Check for rest
        if self.cycle_count >= self.max_cycles_before_rest:
            self.logger.info(f"Reached max cycles ({self.max_cycles_before_rest}), taking rest")
            self.cycle_count = 0
    
    def _observe(self, state: AgentStatus, ctx) -> Dict[str, Any]:
        """Observe internal and external state."""
        return {
            "internal_state": state.state.value,
            "mode": state.mode.value,
            "error_count": state.error_count,
            "thought_depth": state.thought_depth,
            "context_items": len(ctx.items),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _check_api_status(self) -> Dict[str, Any]:
        """Check API availability and quotas."""
        # Placeholder - will be implemented with accounts manager
        return {
            "available": True,
            "quota_remaining": 100.0,
            "active_provider": "openai",
        }
    
    def _execute_user_task(self, task: Dict, state: AgentStatus, ctx) -> Dict[str, Any]:
        """Execute a user task."""
        self.logger.info(f"Executing user task: {task['task']}")
        
        # Use thinking engine to plan task execution
        plan = self.thinking.think(task['task'], state, ctx)
        
        # Execute plan (simplified)
        result = {
            "task": task['task'],
            "status": "completed",
            "plan": plan,
        }
        
        # Mark task as complete
        task_idx = next((i for i, t in enumerate(ctx.user_tasks) if t['task'] == task['task']), None)
        if task_idx is not None:
            ctx.complete_task(task_idx)
        
        return result
    
    def _execute_exploration(self, state: AgentStatus, ctx) -> Dict[str, Any]:
        """Execute exploration in free mode."""
        self.logger.info("Exploring...")
        
        # Generate curiosity-based exploration
        topic = self.thinking.generate_curiosity_topic(ctx)
        
        return {
            "type": "exploration",
            "topic": topic,
            "status": "completed",
        }
    
    def _execute_learning(self, state: AgentStatus, ctx) -> Dict[str, Any]:
        """Execute learning activity."""
        self.logger.info("Learning...")
        
        return {
            "type": "learning",
            "status": "completed",
        }
    
    def _execute_reflection(self, state: AgentStatus, ctx) -> Dict[str, Any]:
        """Execute reflection on recent actions."""
        self.logger.info("Reflecting...")
        
        return {
            "type": "reflection",
            "status": "completed",
        }
    
    def _register(self, cycle_time: datetime, intention: str, result: Dict, state: AgentStatus, ctx) -> None:
        """Register cycle results."""
        ctx.add_item(
            f"Cycle {self.cycle_count}: {intention} - {result.get('status', 'unknown')}",
            priority=1,
            source="internal",
        )
    
    def _reflect(self, result: Dict, state: AgentStatus, ctx) -> None:
        """Reflect on the cycle results."""
        if result.get('status') == 'completed':
            self.logger.debug("Cycle completed successfully")
    
    def _handle_error(self, error: Exception) -> None:
        """Handle cycle errors."""
        state = get_current_state()
        state.error_count += 1
        state.state = AgentState.IDLE
        save_current_state(state)
        
        self.logger.error(f"Error handled: {error}")
    
    def stop(self) -> None:
        """Stop the agent loop."""
        self.running = False
        self.logger.info("Agent loop stopped")