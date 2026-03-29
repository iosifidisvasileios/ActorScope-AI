from __future__ import annotations


def build_demo_organization_input() -> dict:
    return {
        "environment": {
            "environment_id": "env_demo_001",
            "environment_type": "organization",
            "description": "A small organizational setting with competing priorities.",
            "actors": ["actor_manager", "actor_report", "actor_peer"],
            "rules": [
                "Actors must operate within organizational norms.",
                "Escalation is possible but costly.",
            ],
            "norms": [
                "Direct confrontation is tolerated but not preferred.",
                "Coalitions may influence outcomes indirectly.",
            ],
            "resources": ["time", "influence", "credibility"],
            "deadlines": ["Scenario should move toward an outcome within a few rounds."],
            "external_pressures": ["delivery pressure"],
            "active_issues": ["alignment on priorities", "trust tension"],
        },
        "scenario": {
            "scenario_id": "scenario_demo_001",
            "title": "Competing priorities under delivery pressure",
            "trigger": "A deadline creates tension between delivery and coordination.",
            "context_summary": (
                "Several actors must coordinate, but there is disagreement "
                "on priorities and some latent mistrust."
            ),
            "stakeholders": ["actor_manager", "actor_report", "actor_peer"],
            "issue_map": [
                "priority misalignment",
                "trust fragility",
                "time pressure",
            ],
            "known_facts": [
                "A deadline exists.",
                "All actors are affected by the same environment.",
            ],
            "uncertainties": [
                "Whether cooperation can be restored quickly.",
                "Whether escalation will occur.",
            ],
            "success_conditions": [
                "Actors move toward a more stable configuration.",
                "Conflict does not escalate uncontrollably.",
            ],
            "failure_conditions": [
                "Escalation risk becomes dominant.",
                "The scenario deadlocks with no meaningful movement.",
            ],
            "current_round": 0,
            "status": "active",
        },
        "actors": [
            {
                "actor_id": "actor_manager",
                "name": "Manager",
                "role_label": "manager",
                "role_description": "Coordinates work and is sensitive to deadlines.",
                "base_objectives": [
                    "protect delivery",
                    "maintain coordination",
                    "avoid unnecessary escalation",
                ],
                "base_priorities": {
                    "delivery": 0.9,
                    "stability": 0.7,
                    "relationship_preservation": 0.5,
                },
                "constraints": [
                    "limited time",
                    "must operate within organizational expectations",
                ],
                "capabilities": ["request", "reframe", "challenge", "deescalate"],
                "red_lines": ["missed delivery with no recovery plan"],
                "interaction_style": "assertive",
                "metadata": {},
            },
            {
                "actor_id": "actor_report",
                "name": "Direct Report",
                "role_label": "individual_contributor",
                "role_description": "Needs clarity, fairness, and manageable expectations.",
                "base_objectives": [
                    "protect autonomy",
                    "avoid unfair blame",
                    "maintain workable conditions",
                ],
                "base_priorities": {
                    "fairness": 0.8,
                    "clarity": 0.7,
                    "self_protection": 0.8,
                },
                "constraints": [
                    "less formal authority",
                    "reactive to pressure",
                ],
                "capabilities": ["resist", "request", "signal", "reframe"],
                "red_lines": ["public blame", "unilateral pressure"],
                "interaction_style": "guarded",
                "metadata": {},
            },
            {
                "actor_id": "actor_peer",
                "name": "Peer",
                "role_label": "peer",
                "role_description": "Affected indirectly and may align with either side.",
                "base_objectives": [
                    "preserve local stability",
                    "protect own deliverables",
                ],
                "base_priorities": {
                    "stability": 0.7,
                    "self_interest": 0.6,
                },
                "constraints": ["limited direct authority"],
                "capabilities": ["support", "signal", "withhold"],
                "red_lines": ["being dragged into unnecessary conflict"],
                "interaction_style": "cautious",
                "metadata": {},
            },
        ],
        "relationships": [
            {
                "source_actor_id": "actor_manager",
                "target_actor_id": "actor_report",
                "trust": 0.45,
                "alignment": 0.40,
                "conflict_level": 0.55,
                "dependency": 0.60,
                "influence": 0.80,
                "perceived_reliability": 0.50,
                "history_summary": "Tension exists around expectations and pace.",
                "metadata": {},
            },
            {
                "source_actor_id": "actor_report",
                "target_actor_id": "actor_manager",
                "trust": 0.35,
                "alignment": 0.35,
                "conflict_level": 0.60,
                "dependency": 0.70,
                "influence": 0.40,
                "perceived_reliability": 0.45,
                "history_summary": "Feels pressured and only partially understood.",
                "metadata": {},
            },
            {
                "source_actor_id": "actor_manager",
                "target_actor_id": "actor_peer",
                "trust": 0.60,
                "alignment": 0.65,
                "conflict_level": 0.20,
                "dependency": 0.30,
                "influence": 0.60,
                "perceived_reliability": 0.70,
                "history_summary": "Generally aligned under normal conditions.",
                "metadata": {},
            },
            {
                "source_actor_id": "actor_peer",
                "target_actor_id": "actor_manager",
                "trust": 0.58,
                "alignment": 0.60,
                "conflict_level": 0.20,
                "dependency": 0.25,
                "influence": 0.35,
                "perceived_reliability": 0.68,
                "history_summary": "Respects the manager but watches self-interest.",
                "metadata": {},
            },
            {
                "source_actor_id": "actor_peer",
                "target_actor_id": "actor_report",
                "trust": 0.55,
                "alignment": 0.50,
                "conflict_level": 0.25,
                "dependency": 0.20,
                "influence": 0.30,
                "perceived_reliability": 0.60,
                "history_summary": "Neutral but sympathetic.",
                "metadata": {},
            },
            {
                "source_actor_id": "actor_report",
                "target_actor_id": "actor_peer",
                "trust": 0.60,
                "alignment": 0.52,
                "conflict_level": 0.20,
                "dependency": 0.15,
                "influence": 0.25,
                "perceived_reliability": 0.62,
                "history_summary": "Sees peer as a possible informal ally.",
                "metadata": {},
            },
        ],
    }


build_demo_input = build_demo_organization_input