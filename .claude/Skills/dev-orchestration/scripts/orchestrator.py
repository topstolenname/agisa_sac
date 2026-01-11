#!/usr/bin/env python3
"""
Dev Team Orchestrator - State machine for coordinating AI agents
"""
import json
import os
import sys
from pathlib import Path
from enum import Enum
import subprocess

# --- Configuration ---
STATE_FILE = ".dev-team-state.json"
PERSONAS_FILE = Path(__file__).parent.parent / "references" / "agent-personas.md"

class AgentRole(str, Enum):
    ARCHITECT = "architect-pm"
    DEVELOPER = "developer"
    QA_CRITIC = "qa-critic"
    WRITER = "tech-writer"

class Orchestrator:
    def __init__(self, project_name="unknown"):
        self.state = self._load_state()
        if self.state["project_name"] == "unknown" and project_name != "unknown":
            self.state["project_name"] = project_name
        self.personas = self._load_personas()

    def _load_state(self):
        """Load or initialize project state"""
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {
            "project_name": "unknown",
            "phase": "planning",  # planning, implementation, documentation, complete
            "current_component": None,
            "completed_components": [],
            "qa_failures": 0,
            "history": []
        }

    def _load_personas(self):
        """Extracts agent prompts from markdown file"""
        if not PERSONAS_FILE.exists():
            print(f"Warning: {PERSONAS_FILE} not found. Using defaults.")
            return {}
        
        content = PERSONAS_FILE.read_text()
        personas = {}
        current_role = None
        current_content = []
        
        for line in content.splitlines():
            if line.startswith("# Role:"):
                # Save previous role
                if current_role:
                    personas[current_role] = "\n".join(current_content)
                # Start new role
                current_role = line.split(":", 1)[1].strip().lower()
                current_content = []
            elif current_role:
                current_content.append(line)
        
        # Save last role
        if current_role:
            personas[current_role] = "\n".join(current_content)
        
        return personas

    def save_state(self):
        """Persist state to disk"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def extract_components_from_design(self):
        """Auto-discover components from design.md"""
        design_file = Path("design.md")
        if not design_file.exists():
            return []
        
        content = design_file.read_text()
        components = []
        
        # Look for common patterns
        # Example: "## Components" section or "1. database-layer" lists
        in_component_section = False
        for line in content.splitlines():
            if "component" in line.lower() and line.startswith("#"):
                in_component_section = True
                continue
            
            if in_component_section:
                # Match numbered lists or bullet points
                if line.strip().startswith(("-", "*", "1.", "2.", "3.")):
                    # Extract component name
                    comp = line.strip().lstrip("-*123456789. ").split(":")[0].strip()
                    if comp:
                        components.append(comp.lower().replace(" ", "-"))
                elif line.strip().startswith("#"):
                    # New section, stop
                    break
        
        return components

    def check_test_result(self, component):
        """
        Automatically check if tests pass
        Returns: ("PASS", "") or ("FAIL", error_message)
        """
        test_file = Path(f"tests/test_{component}.py")
        if not test_file.exists():
            return "FAIL", f"Test file {test_file} not found"
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(test_file), "-v"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return "PASS", ""
            else:
                # Extract meaningful error
                stderr = result.stderr if result.stderr else result.stdout
                return "FAIL", stderr[:500]  # Truncate long errors
        except subprocess.TimeoutExpired:
            return "FAIL", "Tests timed out after 30 seconds"
        except FileNotFoundError:
            # pytest not installed, fallback to manual
            return "UNKNOWN", "pytest not found, manual verification needed"

    def get_next_task(self):
        """
        Core state machine logic
        Returns: (AgentRole, instruction_string)
        """
        phase = self.state["phase"]
        
        # PHASE 1: PLANNING
        if phase == "planning":
            spec_exists = Path("spec.md").exists()
            design_exists = Path("design.md").exists()
            
            if spec_exists and design_exists:
                print("✅ Planning artifacts detected (spec.md, design.md)")
                
                # Try to extract components
                components = self.extract_components_from_design()
                if components:
                    print(f"📋 Discovered components: {', '.join(components)}")
                    self.state["discovered_components"] = components
                
                self.state["phase"] = "implementation"
                self.save_state()
                return self.get_next_task()  # Recurse into implementation
            
            return AgentRole.ARCHITECT, (
                "Review the user request. Create:\n"
                "1. spec.md - User stories, acceptance criteria, requirements\n"
                "2. design.md - Architecture, file structure, component list\n"
                "3. schema.sql (if database needed)\n"
                "Output 'PLANNING COMPLETE' when done."
            )

        # PHASE 2: IMPLEMENTATION LOOP
        elif phase == "implementation":
            current = self.state.get("current_component")
            
            # No component in progress - pick next one
            if not current:
                # Check if we have discovered components
                discovered = self.state.get("discovered_components", [])
                remaining = [c for c in discovered if c not in self.state["completed_components"]]
                
                if remaining:
                    # Auto-select next component
                    next_comp = remaining[0]
                    print(f"🎯 Auto-selecting next component: {next_comp}")
                    print(f"   Remaining: {', '.join(remaining[1:]) if len(remaining) > 1 else 'None'}")
                else:
                    # Manual selection
                    print("\n" + "="*60)
                    print("📊 CURRENT STATE:")
                    print(f"   Completed: {', '.join(self.state['completed_components']) or 'None'}")
                    print(f"   Total components: {len(self.state['completed_components'])}")
                    print("="*60)
                    next_comp = input("▶ Enter next component name (or 'DONE' to finish): ").strip()
                
                if next_comp.upper() == "DONE":
                    self.state["phase"] = "documentation"
                    self.save_state()
                    return self.get_next_task()
                
                self.state["current_component"] = next_comp
                self.state["qa_failures"] = 0
                self.save_state()
                return AgentRole.DEVELOPER, (
                    f"Implement component: {next_comp}\n"
                    f"Refer to spec.md and design.md for requirements.\n"
                    f"Write clean, well-structured code."
                )
            
            # Component in progress - check who went last
            last_action = self.state["history"][-1]["role"] if self.state["history"] else "none"
            
            if last_action == AgentRole.DEVELOPER:
                # Developer just finished, QA is next
                return AgentRole.QA_CRITIC, (
                    f"Test component: {current}\n"
                    f"1. Write test file: tests/test_{current}.py\n"
                    f"2. Execute tests using pytest\n"
                    f"3. Analyze results\n"
                    f"Output: 'QA RESULT: PASS' or 'QA RESULT: FAIL - [reason]'"
                )
            
            elif last_action == AgentRole.QA_CRITIC:
                # QA just finished, check results
                status, error = self.check_test_result(current)
                
                if status == "UNKNOWN":
                    # Manual verification
                    result = input(f"⚠️  pytest not found. Did {current} pass QA? (y/n): ").strip().lower()
                    status = "PASS" if result == 'y' else "FAIL"
                    error = "Manual verification"
                
                if status == "PASS":
                    print(f"✅ {current} PASSED quality checks")
                    self.state["completed_components"].append(current)
                    self.state["current_component"] = None
                    self.state["qa_failures"] = 0
                    self.save_state()
                    return self.get_next_task()
                else:
                    print(f"❌ {current} FAILED (iteration {self.state['qa_failures'] + 1})")
                    print(f"   Error: {error[:200]}")
                    self.state["qa_failures"] += 1
                    return AgentRole.DEVELOPER, (
                        f"Fix component: {current}\n"
                        f"Tests failed (iteration {self.state['qa_failures']})\n"
                        f"Error details:\n{error}\n"
                        f"Analyze the failure and fix the root cause."
                    )
            
            # Default: Start development
            return AgentRole.DEVELOPER, f"Implement component: {current}. Refer to spec.md."

        # PHASE 3: DOCUMENTATION
        elif phase == "documentation":
            readme_exists = Path("README.md").exists()
            if readme_exists:
                print("✅ Documentation complete")
                self.state["phase"] = "complete"
                self.save_state()
                return None, "PROJECT COMPLETE"
            
            return AgentRole.WRITER, (
                "Generate final documentation:\n"
                "1. README.md - Installation, usage, examples\n"
                "2. Add/verify docstrings in all Python files\n"
                "3. Create API.md if project is a library\n"
                f"Completed components: {', '.join(self.state['completed_components'])}"
            )
        
        # PHASE 4: COMPLETE
        else:
            return None, "PROJECT COMPLETE - All phases finished"

    def run_turn(self):
        """Execute one turn of the state machine"""
        result = self.get_next_task()
        
        if result[0] is None:
            print(f"\n🎉 {result[1]}")
            return None
        
        role, instructions = result
        system_prompt = self.personas.get(role, "You are a helpful AI assistant.")
        
        print(f"\n{'='*60}")
        print(f"🤖 AGENT: {role.upper()}")
        print(f"{'='*60}")
        print(f"📋 TASK:\n{instructions}")
        print(f"{'='*60}")
        print(f"\n💬 SYSTEM PROMPT:\n{system_prompt[:300]}...")
        print(f"{'='*60}\n")
        
        # TODO: Hook into your local LLM here
        # Example with OpenAI-compatible API:
        # response = openai.ChatCompletion.create(
        #     model="qwen2.5:7b",
        #     messages=[
        #         {"role": "system", "content": system_prompt},
        #         {"role": "user", "content": instructions}
        #     ]
        # )
        # print(response.choices[0].message.content)
        
        # For now, manual execution
        input("Press Enter when agent has completed this task...")
        
        # Log to history
        self.state["history"].append({"role": role, "task": instructions[:100]})
        self.save_state()
        
        return role

    def reset(self):
        """Reset state for new project"""
        if Path(STATE_FILE).exists():
            Path(STATE_FILE).unlink()
        print("🔄 State reset. Starting fresh.")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--reset":
            Orchestrator().reset()
            return
        project_name = sys.argv[1]
    else:
        project_name = input("📝 Project name: ").strip() or "unknown"
    
    orch = Orchestrator(project_name)
    
    # Run continuously until complete
    while True:
        result = orch.run_turn()
        if result is None:
            break
        
        # Ask if user wants to continue
        cont = input("\n▶ Continue to next agent? (y/n/quit): ").strip().lower()
        if cont in ['n', 'q', 'quit']:
            print("⏸️  Paused. Run script again to resume.")
            break

if __name__ == "__main__":
    main()
