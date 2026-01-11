-- BigQuery schema for AGI-SAC simulation data
CREATE TABLE IF NOT EXISTS `simulation.memory_scrolls` (
    agent_id STRING,
    epoch INT64,
    timestamp TIMESTAMP,
    scroll JSON,
    PRIMARY KEY(agent_id, epoch)
);

CREATE TABLE IF NOT EXISTS `simulation.agent_phases` (
    agent_id STRING,
    phase STRING,
    started TIMESTAMP,
    ended TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `simulation.homology_topologies` (
    run_id STRING,
    dimension INT64,
    birth FLOAT64,
    death FLOAT64
);
