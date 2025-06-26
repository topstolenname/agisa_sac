 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/src/agisa_sac/components/cognitive.py b/src/agisa_sac/components/cognitive.py
index 9bc45d83b1c006d6c70a97c4804c5ea29b90bd9f..779ec2a0b8feff15b1a56b4fa0ec1dea7b3e23fc 100644
--- a/src/agisa_sac/components/cognitive.py
+++ b/src/agisa_sac/components/cognitive.py
@@ -29,58 +29,73 @@ class CognitiveDiversityEngine:
         self.stability_factor = 0.3
         self.cognitive_state = np.ones(4) / 4 # Vector over state aspects
         self.decision_history: List[Dict] = [] # Runtime history
 
     def update_heuristics(self, situational_entropy: float):
         # ... (logic from previous combined file) ...
         memories = self.memory_layer.retrieve_memory("decision outcome context", limit=5, threshold=0.2)
         salience = sum(m["importance"] * m["confidence"] for m in memories) / len(memories) if memories else 0.1; salience = np.clip(salience, 0.0, 1.0)
         personality_vector = np.array([ self.personality.get("curiosity", 0.5), self.personality.get("conformity", 0.5), self.personality.get("openness", 0.5), self.personality.get("consistency", 0.5) ])
         d_heuristics = salience * situational_entropy * personality_vector.reshape(-1, 1) * (np.random.rand(4,4) - 0.5) * 0.5
         self.heuristics += self.learning_rate * (d_heuristics - self.stability_factor * (self.heuristics - 0.5)); self.heuristics = 1 / (1 + np.exp(-self.heuristics)); self.heuristics = np.clip(self.heuristics, 0.1, 0.9)
         if self.message_bus: self.message_bus.publish('cognitive_heuristic_update', {'agent_id': self.agent_id, 'magnitude': float(np.mean(np.abs(d_heuristics))), 'entropy': float(situational_entropy), 'salience': float(salience)})
 
 
     def decide(self, query: str, peer_influence: Dict[str, float]) -> str:
         # ... (logic from previous combined file) ...
         memories = self.memory_layer.retrieve_memory(query, limit=5, threshold=0.25); memory_weight = sum(m["relevance_score"] * m["confidence"] for m in memories) / len(memories) if memories else 0.0; memory_weight = np.clip(memory_weight, 0.0, 1.0)
         total_influence = sum(peer_influence.values()); normalized_influence = {pid: w / total_influence for pid, w in peer_influence.items()} if total_influence > 1e-6 else {}; peer_weight = sum(normalized_influence.values()); peer_weight = np.clip(peer_weight, 0.0, 1.0)
         self.cognitive_state *= (1 - 0.1)
         if memories:
             memory_state_influence = np.zeros(4); total_mem_relevance = sum(m['relevance_score'] for m in memories)
             if total_mem_relevance > 1e-6:
                  for m in memories: mem_impact = m['relevance_score'] / total_mem_relevance; memory_state_influence[3] += mem_impact * m['importance']; memory_state_influence[1] += mem_impact * m['confidence']; memory_state_influence[2] += mem_impact * (1 - m['importance']); memory_state_influence[0] += mem_impact * (1 - m['confidence'])
                  if np.sum(memory_state_influence) > 1e-6: memory_state_influence /= np.sum(memory_state_influence)
                  self.cognitive_state += 0.1 * memory_weight * memory_state_influence
-        if normalized_influence: peer_state_influence = np.array([0.0, 0.6, 0.0, 0.4]); self.cognitive_state += 0.1 * peer_weight * peer_state_influence
-        if np.sum(self.cognitive_state) > 1e-6: self.cognitive_state /= np.sum(self.cognitive_state); else: self.cognitive_state = np.ones(4) / 4
-        decision_probs = np.dot(self.cognitive_state, self.heuristics);
-        if np.sum(decision_probs) > 1e-6: decision_probs /= np.sum(decision_probs); else: decision_probs = np.ones(4) / 4
+        if normalized_influence:
+            peer_state_influence = np.array([0.0, 0.6, 0.0, 0.4])
+            self.cognitive_state += 0.1 * peer_weight * peer_state_influence
+
+        if np.sum(self.cognitive_state) > 1e-6:
+            self.cognitive_state /= np.sum(self.cognitive_state)
+        else:
+            self.cognitive_state = np.ones(4) / 4
+
+        decision_probs = np.dot(self.cognitive_state, self.heuristics)
+        if np.sum(decision_probs) > 1e-6:
+            decision_probs /= np.sum(decision_probs)
+        else:
+            decision_probs = np.ones(4) / 4
         options = ["Approach A: Systematic", "Approach B: Creative", "Approach C: Balanced", "Approach D: Efficient"]
         exploration_prob = 0.1 + 0.3 * self.personality.get("openness", 0.5)
-        if random.random() > exploration_prob: choice_idx = np.argmax(decision_probs)
-        else: try: choice_idx = np.random.choice(len(options), p=decision_probs); except ValueError: choice_idx = np.random.choice(len(options))
+        if random.random() > exploration_prob:
+            choice_idx = np.argmax(decision_probs)
+        else:
+            try:
+                choice_idx = np.random.choice(len(options), p=decision_probs)
+            except ValueError:
+                choice_idx = np.random.choice(len(options))
         response = options[choice_idx]
         decision_record = {"query": query, "response": response, "cognitive_state": self.cognitive_state.tolist(), "decision_probs": decision_probs.tolist(), "memory_weight": memory_weight, "peer_weight": peer_weight, "exploration_used": random.random() <= exploration_prob, "timestamp": time.time()}
         self.decision_history.append(decision_record); self.decision_history = self.decision_history[-100:] # Limit history size
         memory_content = {"type": "decision_context", "query": query, "response": response, "cognitive_state_at_decision": self.cognitive_state.tolist(), "theme": self.memory_layer.get_current_focus_theme(), "timestamp": decision_record["timestamp"]}
         self.memory_layer.add_memory(memory_content, importance=0.6)
         if self.message_bus: self.message_bus.publish('agent_decision', {'agent_id': self.agent_id, 'query': query, 'response': response, 'decision_probs': decision_probs.tolist(), 'cognitive_state': self.cognitive_state.tolist()})
         return response
 
     def learn_from_feedback(self, decision_index: int, reward: float):
         # ... (logic from previous combined file) ...
         if 0 <= decision_index < len(self.decision_history):
             decision = self.decision_history[decision_index]; response = decision["response"]; cognitive_state_at_decision = np.array(decision["cognitive_state"])
             try:
                 options = ["Approach A: Systematic", "Approach B: Creative", "Approach C: Balanced", "Approach D: Efficient"]; choice_idx = options.index(response)
                 update_vector = cognitive_state_at_decision * reward * self.learning_rate * 0.5; self.heuristics[:, choice_idx] += update_vector
                 self.heuristics = 1 / (1 + np.exp(-self.heuristics)); self.heuristics = np.clip(self.heuristics, 0.1, 0.9)
                 if self.message_bus: self.message_bus.publish('agent_feedback_learning', {'agent_id': self.agent_id, 'decision_index': decision_index, 'reward': reward, 'magnitude': float(np.sum(np.abs(update_vector)))})
                 return True
             except ValueError: warnings.warn(f"Agent {self.agent_id}: Resp '{response}' N/A.", RuntimeWarning)
             except Exception as e: warnings.warn(f"Agent {self.agent_id}: Feedback err: {e}", RuntimeWarning)
         else: warnings.warn(f"Agent {self.agent_id}: Invalid index {decision_index}.", RuntimeWarning)
         return False
 
     def to_dict(self, history_limit: int = 10) -> Dict:
         """ Serializes the cognitive engine state. """
 
EOF
)