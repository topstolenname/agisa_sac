 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/src/agisa_sac/agent.py b/src/agisa_sac/agent.py
index ca4990f9b8855a6d242d4532e919873788b7ba55..5583df0eeddc195ee3a32ad9c1d77cf84b80c081 100644
--- a/src/agisa_sac/agent.py
+++ b/src/agisa_sac/agent.py
@@ -103,56 +103,64 @@ class EnhancedAgent:
         except Exception as e: warnings.warn(f"Agent {agent_id}: Failed voice load: {e}", RuntimeWarning); raise ValueError("Voice load failed") from e
         try: temporal_resonance = TemporalResonanceTracker.from_dict(data['temporal_resonance_state'], agent_id=agent_id)
         except Exception as e: warnings.warn(f"Agent {agent_id}: Failed resonance load: {e}", RuntimeWarning); raise ValueError("Resonance load failed") from e
 
         # Create agent instance, passing reconstructed components, and DO NOT add initial memory
         agent = cls( agent_id=agent_id, personality=cognitive.personality, # Get personality from loaded cognitive state
                      capacity=memory.capacity, message_bus=message_bus, use_semantic=memory.use_semantic,
                      memory=memory, cognitive=cognitive, voice=voice, temporal_resonance=temporal_resonance,
                      add_initial_memory=False ) # Important flag
 
         # Load remaining agent-level state
         agent.last_reflection_trigger = data.get("last_reflection_trigger")
         # agent.recent_decision_log = [] # Don't load runtime log
 
         # --- Validation ---
         try: agent._validate_state(strict=strict_validation)
         except ValueError as e:
             if strict_validation: raise e
             else: warnings.warn(f"Agent {agent_id}: State validation failed post-load: {e}", RuntimeWarning)
         # print(f"Agent {agent_id} reconstructed.") # Verbose
         return agent
 
     def _validate_state(self, strict: bool = True):
         # ... (validation logic as before) ...
         errors = []; warnings_list = []
-        if not isinstance(self.cognitive.personality, dict): errors.append("Personality type."); else:
+        if not isinstance(self.cognitive.personality, dict):
+            errors.append("Personality type.")
+        else:
             for key, val in self.cognitive.personality.items():
-                 if not (0.0 <= val <= 1.0): errors.append(f"Personality '{key}' range.")
+                if not (0.0 <= val <= 1.0):
+                    errors.append(f"Personality '{key}' range.")
         if not isinstance(self.cognitive.heuristics, np.ndarray) or self.cognitive.heuristics.shape != (4, 4): errors.append("Heuristics shape.")
         if not isinstance(self.cognitive.cognitive_state, np.ndarray) or self.cognitive.cognitive_state.shape != (4,): errors.append("Cognitive state shape.")
         elif not np.isclose(np.sum(self.cognitive.cognitive_state), 1.0): warnings_list.append(f"Cognitive state sum ~{np.sum(self.cognitive.cognitive_state):.2f}.")
         sig = self.voice.linguistic_signature
-        if not isinstance(sig, dict): errors.append("Ling sig type."); elif "style_vector" not in sig or not isinstance(sig["style_vector"], np.ndarray): errors.append("Style vector type/missing."); elif np.any(np.isnan(sig["style_vector"])) or np.any(np.isinf(sig["style_vector"])): errors.append("Style vector NaN/Inf.")
+        if not isinstance(sig, dict):
+            errors.append("Ling sig type.")
+        elif "style_vector" not in sig or not isinstance(sig["style_vector"], np.ndarray):
+            errors.append("Style vector type/missing.")
+        elif np.any(np.isnan(sig["style_vector"])) or np.any(np.isinf(sig["style_vector"])):
+            errors.append("Style vector NaN/Inf.")
         if not isinstance(self.memory.memories, dict): errors.append("Memory store type.")
         # Correct state sum if not strict
         if not strict and any("Cognitive state sum" in w for w in warnings_list):
             if np.sum(self.cognitive.cognitive_state) > 1e-6: self.cognitive.cognitive_state /= np.sum(self.cognitive.cognitive_state)
             else: self.cognitive.cognitive_state = np.ones(4) / 4; warnings_list.append("Cognitive state reset.")
         # Report
         for w in warnings_list: warnings.warn(f"Agent {self.agent_id} Validate Warn: {w}", RuntimeWarning)
         if errors: error_message = f"Agent {self.agent_id} Validate Fail: {'; '.join(errors)}";
         if strict and errors: raise ValueError(error_message)
         elif errors: warnings.warn(error_message, RuntimeWarning)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
EOF
)