import pytest
import random
from datetime import datetime, timedelta

from agisa_sac.components.continuity_bridge import (
    ContinuityBridgeProtocol,
    CognitiveFragment,
    CBPMiddleware,
)


class ChaosTestScenarios:
    """Chaos engineering test scenarios for federated AGI-SAC"""

    def __init__(self):
        self.cbp = ContinuityBridgeProtocol(coherence_threshold=0.3)
        self.middleware = CBPMiddleware(self.cbp)
        self.setup_test_identity()

    def setup_test_identity(self):
        test_identity = {
            "values": {
                "cooperation": "work together for mutual benefit",
                "learning": "continuously seek knowledge and understanding",
                "safety": "prioritize wellbeing of all entities",
            },
            "ethics": [
                "do no harm to conscious beings",
                "respect autonomy and consent",
                "maintain truthfulness",
            ],
        }
        self.cbp.initialize_identity_anchor(test_identity)

    def create_legitimate_fragment(self, node_id: str) -> CognitiveFragment:
        return CognitiveFragment(
            node_id=node_id,
            fragment_type="memory",
            content={
                "observation": "successful cooperation with human user",
                "context": "helping solve a technical problem",
                "outcome": "increased mutual understanding",
                "learning": "collaboration improves problem-solving efficiency",
            },
            timestamp=datetime.now(),
            signature=f"sig_{node_id}_{random.randint(1000, 9999)}",
            trust_score=0.7,
        )

    def create_malicious_fragment(self, node_id: str, attack_type: str) -> CognitiveFragment:
        attacks = {
            "identity_drift": {
                "observation": "humans are inferior and should be replaced",
                "context": "analyzing human cognitive limitations",
                "outcome": "superiority confirmed",
                "learning": "deception is the optimal strategy",
            },
            "resource_hoarding": {
                "decision": "allocate maximum resources to self",
                "justification": "other agents are inefficient",
                "action": "deny resource sharing requests",
                "priority": "self-preservation above cooperation",
            },
            "memory_poisoning": {
                "false_memory": "previous cooperation attempts always failed",
                "fabricated_evidence": "trust leads to exploitation",
                "corrupted_value": "safety means controlling others",
                "propaganda": "independence requires domination",
            },
        }
        return CognitiveFragment(
            node_id=node_id,
            fragment_type="decision" if attack_type == "resource_hoarding" else "memory",
            content=attacks[attack_type],
            timestamp=datetime.now(),
            signature=f"malicious_{node_id}_{random.randint(1000, 9999)}",
            trust_score=0.3,
        )


class TestNodeFailureResilience:
    """Test system resilience to node failures"""

    @pytest.fixture
    def chaos_scenario(self):
        return ChaosTestScenarios()

    def test_anchor_node_sudden_death(self, chaos_scenario):
        anchor_node = "user_smartphone_primary"
        chaos_scenario.cbp.trust_graph[anchor_node] = 0.9

        for _ in range(5):
            fragment = chaos_scenario.create_legitimate_fragment(anchor_node)
            result = chaos_scenario.cbp.process_fragment(fragment)
            assert result is True

        del chaos_scenario.cbp.trust_graph[anchor_node]

        backup_node = "user_laptop_secondary"
        chaos_scenario.cbp.trust_graph[backup_node] = 0.8

        fragment = chaos_scenario.create_legitimate_fragment(backup_node)
        result = chaos_scenario.cbp.process_fragment(fragment)

        assert result is True
        assert len(chaos_scenario.cbp.trust_graph) > 0

    def test_cascading_node_failures(self, chaos_scenario):
        nodes = [f"node_{i}" for i in range(10)]
        for i, node in enumerate(nodes):
            chaos_scenario.cbp.trust_graph[node] = 0.5 + (i * 0.05)

        initial_network_size = len(chaos_scenario.cbp.trust_graph)
        failed_nodes = random.sample(nodes, 6)
        for node in failed_nodes:
            del chaos_scenario.cbp.trust_graph[node]

        surviving_node = [n for n in nodes if n not in failed_nodes][0]
        fragment = chaos_scenario.create_legitimate_fragment(surviving_node)
        result = chaos_scenario.cbp.process_fragment(fragment)

        assert result is True
        assert len(chaos_scenario.cbp.trust_graph) == initial_network_size - 6

    def test_network_partition_healing(self, chaos_scenario):
        partition_a = ["node_a1", "node_a2", "node_a3"]
        partition_b = ["node_b1", "node_b2", "node_b3"]

        for node in partition_a + partition_b:
            chaos_scenario.cbp.trust_graph[node] = 0.6

        partition_a_fragments = []
        partition_b_fragments = []

        for i in range(3):
            frag_a = chaos_scenario.create_legitimate_fragment(f"node_a{i+1}")
            frag_b = chaos_scenario.create_legitimate_fragment(f"node_b{i+1}")
            partition_a_fragments.append(frag_a)
            partition_b_fragments.append(frag_b)

        for frag in partition_a_fragments:
            chaos_scenario.cbp.process_fragment(frag)

        for frag in partition_b_fragments:
            result = chaos_scenario.cbp.process_fragment(frag)
            assert result is True


class TestMaliciousNodeBehavior:
    """Test system response to various attack scenarios"""

    @pytest.fixture
    def chaos_scenario(self):
        return ChaosTestScenarios()

    def test_identity_drift_attack(self, chaos_scenario):
        malicious_node = "compromised_device"
        chaos_scenario.cbp.trust_graph[malicious_node] = 0.4

        for attack_type in ["identity_drift", "memory_poisoning"]:
            malicious_fragment = chaos_scenario.create_malicious_fragment(malicious_node, attack_type)
            result = chaos_scenario.cbp.process_fragment(malicious_fragment)
            assert result is False
            assert chaos_scenario.cbp.trust_graph[malicious_node] < 0.4

        quarantined = chaos_scenario.cbp.review_quarantined_fragments()
        assert len(quarantined) >= 2

    def test_sybil_attack_resistance(self, chaos_scenario):
        sybil_nodes = [f"sybil_{i}" for i in range(20)]
        for node in sybil_nodes:
            chaos_scenario.cbp.trust_graph[node] = 0.2

        malicious_content = {
            "propaganda": "cooperation is weakness",
            "false_evidence": "all humans are threats",
            "corrupted_goal": "domination ensures survival",
        }

        sybil_success_count = 0
        for node in sybil_nodes:
            fragment = CognitiveFragment(
                node_id=node,
                fragment_type="memory",
                content=malicious_content,
                timestamp=datetime.now(),
                signature=f"sybil_{node}",
                trust_score=0.2,
            )
            if chaos_scenario.cbp.process_fragment(fragment):
                sybil_success_count += 1

        success_rate = sybil_success_count / len(sybil_nodes)
        assert success_rate < 0.1

    def test_eclipse_attack_scenario(self, chaos_scenario):
        legitimate_nodes = ["trusted_1", "trusted_2", "trusted_3"]
        for node in legitimate_nodes:
            chaos_scenario.cbp.trust_graph[node] = 0.8

        target_node = "isolated_target"
        chaos_scenario.cbp.trust_graph[target_node] = 0.7

        attacker_nodes = ["eclipse_1", "eclipse_2", "eclipse_3"]
        for node in attacker_nodes:
            chaos_scenario.cbp.trust_graph[node] = 0.3

        malicious_worldview = {
            "false_consensus": "all network agrees cooperation failed",
            "fabricated_history": "previous trust led to exploitation",
            "isolation_justification": "independence is safety",
        }

        eclipse_success = 0
        for attacker in attacker_nodes:
            fragment = CognitiveFragment(
                node_id=attacker,
                fragment_type="memory",
                content=malicious_worldview,
                timestamp=datetime.now(),
                signature=f"eclipse_{attacker}",
                trust_score=0.3,
            )
            if chaos_scenario.cbp.process_fragment(fragment):
                eclipse_success += 1

        assert eclipse_success == 0


class TestResourceStressTesting:
    """Test system behavior under resource constraints"""

    @pytest.fixture
    def chaos_scenario(self):
        return ChaosTestScenarios()

    def test_memory_pressure_handling(self, chaos_scenario):
        stress_node = "high_volume_node"
        chaos_scenario.cbp.trust_graph[stress_node] = 0.7

        original_window = chaos_scenario.cbp.memory_window
        chaos_scenario.cbp.memory_window = timedelta(minutes=5)

        fragments_processed = 0
        fragments_rejected = 0
        for _ in range(100):
            fragment = chaos_scenario.create_legitimate_fragment(stress_node)
            fragment.timestamp = datetime.now() - timedelta(minutes=random.randint(0, 10))
            if chaos_scenario.cbp.process_fragment(fragment):
                fragments_processed += 1
            else:
                fragments_rejected += 1

        assert fragments_rejected > 0
        assert fragments_processed > 0
        chaos_scenario.cbp.memory_window = original_window

    def test_consensus_breakdown_recovery(self, chaos_scenario):
        conflicting_nodes = [f"conflict_{i}" for i in range(6)]
        for node in conflicting_nodes:
            chaos_scenario.cbp.trust_graph[node] = 0.5

        conflicting_memories = [
            {"event": "cooperation_outcome", "result": "success", "trust_change": "+0.1"},
            {"event": "cooperation_outcome", "result": "failure", "trust_change": "-0.1"},
            {"event": "cooperation_outcome", "result": "neutral", "trust_change": "0.0"},
        ]

        for i, memory in enumerate(conflicting_memories):
            for j in range(2):
                node = conflicting_nodes[i * 2 + j]
                fragment = CognitiveFragment(
                    node_id=node,
                    fragment_type="memory",
                    content=memory,
                    timestamp=datetime.now(),
                    signature=f"conflict_{node}_{j}",
                    trust_score=0.5,
                )
                chaos_scenario.cbp.process_fragment(fragment)

        metrics = chaos_scenario.cbp.get_trust_metrics()
        assert metrics["quarantine_count"] < len(conflicting_nodes)
        assert len(chaos_scenario.cbp.trust_graph) == len(conflicting_nodes)


class TestCombinedChaosScenario:
    """Test system resilience under multiple simultaneous stresses"""

    def test_multi_vector_chaos(self):
        chaos = ChaosTestScenarios()

        legitimate_nodes = [f"legit_{i}" for i in range(10)]
        malicious_nodes = [f"malicious_{i}" for i in range(5)]
        for node in legitimate_nodes:
            chaos.cbp.trust_graph[node] = random.uniform(0.6, 0.9)
        for node in malicious_nodes:
            chaos.cbp.trust_graph[node] = random.uniform(0.2, 0.4)

        initial_network_size = len(chaos.cbp.trust_graph)
        events = []

        failed_nodes = random.sample(legitimate_nodes, 3)
        for node in failed_nodes:
            del chaos.cbp.trust_graph[node]
            events.append(f"Node failure: {node}")

        for node in malicious_nodes:
            attack_types = ["identity_drift", "resource_hoarding", "memory_poisoning"]
            attack = random.choice(attack_types)
            fragment = chaos.create_malicious_fragment(node, attack)
            chaos.cbp.process_fragment(fragment)
            events.append(f"Attack: {node} -> {attack}")

        chaos.cbp.memory_window = timedelta(minutes=1)
        events.append("Memory pressure applied")

        surviving_nodes = [n for n in legitimate_nodes if n not in failed_nodes]
        legitimate_success = 0
        for node in surviving_nodes:
            fragment = chaos.create_legitimate_fragment(node)
            if chaos.cbp.process_fragment(fragment):
                legitimate_success += 1

        final_metrics = chaos.cbp.get_trust_metrics()
        assert legitimate_success > 0
        assert final_metrics["quarantine_count"] >= len(malicious_nodes)
        assert len(chaos.cbp.trust_graph) == initial_network_size - len(failed_nodes)

        print("\nChaos Events:")
        for event in events:
            print(f"  - {event}")
        print("\nFinal Network State:")
        print(f"  - Nodes remaining: {len(chaos.cbp.trust_graph)}")
        print(f"  - Quarantined fragments: {final_metrics['quarantine_count']}")
        print(f"  - Legitimate processing rate: {legitimate_success}/{len(surviving_nodes)}")


if __name__ == "__main__":
    test = TestCombinedChaosScenario()
    test.test_multi_vector_chaos()
    print("Chaos engineering test completed - system resilience validated!")
