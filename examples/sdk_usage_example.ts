/**
 * Example usage of the LOGOS TypeScript SDKs (Hermes and Sophia clients).
 * 
 * This example demonstrates how to:
 * 1. Connect to Hermes and Sophia services
 * 2. Generate text embeddings with Hermes
 * 3. Create a plan with Sophia
 * 4. Query the current state
 * 5. Run a simulation
 * 
 * Prerequisites:
 * - Hermes service running on http://localhost:8080
 * - Sophia service running on http://localhost:8000
 * - Both services connected to the HCG (Neo4j + Milvus)
 * 
 * Usage:
 *   npm install @logos/hermes-client @logos/sophia-client
 *   npx ts-node sdk_usage_example.ts
 */

import { Configuration as HermesConfig, DefaultApi as HermesApi } from '@logos/hermes-client';
import { Configuration as SophiaConfig, DefaultApi as SophiaApi } from '@logos/sophia-client';


async function hermesExample() {
  console.log('\n=== Hermes SDK Example ===\n');
  
  // Configure Hermes client
  const hermesConfig = new HermesConfig({
    basePath: 'http://localhost:8080',
  });
  const hermesApi = new HermesApi(hermesConfig);
  
  // 1. Generate text embeddings
  console.log('1. Generating text embeddings...');
  try {
    const embedResponse = await hermesApi.embedText({
      text: 'The red block is on the table',
      model: 'default',
    });
    console.log(`   ✓ Embedding generated: ${embedResponse.dimension} dimensions`);
    console.log(`   ✓ Model: ${embedResponse.model}`);
    console.log(`   ✓ First 5 values: ${embedResponse.embedding?.slice(0, 5)}`);
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
  
  // 2. Simple NLP processing
  console.log('\n2. Processing text with NLP...');
  try {
    const nlpResponse = await hermesApi.simpleNlp({
      text: 'The quick brown fox jumps over the lazy dog',
      operations: ['tokenize', 'pos_tag'],
    });
    console.log(`   ✓ Tokens: ${nlpResponse.tokens}`);
    if (nlpResponse.pos_tags && nlpResponse.pos_tags.length > 0) {
      const tagPairs = nlpResponse.pos_tags.slice(0, 5).map(t => `(${t.token}, ${t.tag})`);
      console.log(`   ✓ POS tags: ${tagPairs.join(', ')}`);
    }
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
  
  // 3. Text-to-Speech (note: returns binary data)
  console.log('\n3. Text-to-Speech conversion...');
  try {
    const ttsResponse = await hermesApi.textToSpeech({
      text: 'Hello from LOGOS',
      language: 'en-US',
    });
    console.log(`   ✓ Audio generated (binary response)`);
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
}


async function sophiaExample() {
  console.log('\n=== Sophia SDK Example ===\n');
  
  // Configure Sophia client
  const sophiaConfig = new SophiaConfig({
    basePath: 'http://localhost:8000',
  });
  const sophiaApi = new SophiaApi(sophiaConfig);
  
  // 1. Check health status
  console.log('1. Checking Sophia health...');
  try {
    const health = await sophiaApi.getHealth();
    console.log(`   ✓ Status: ${health.status}`);
    console.log(`   ✓ Neo4j connected: ${health.neo4j?.connected}`);
    console.log(`   ✓ Milvus collections: ${health.milvus?.collections}`);
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
  
  // 2. Generate a plan
  console.log('\n2. Generating a plan...');
  try {
    const plan = await sophiaApi.generatePlan({
      goal: 'Pick up the red block and place it in the bin',
      goal_state: {
        entities: [
          {
            entity_id: 'block_red_001',
            desired_state: 'in_bin',
          },
        ],
      },
      context: {
        environment: 'table_workspace',
        available_capabilities: ['grasp_object', 'move_arm', 'release_object'],
      },
    });
    console.log(`   ✓ Plan ID: ${plan.plan_id}`);
    console.log(`   ✓ Number of processes: ${plan.processes?.length || 0}`);
    console.log(`   ✓ Confidence: ${plan.confidence?.toFixed(2)}`);
    
    if (plan.processes && plan.processes.length > 0) {
      console.log('\n   Processes:');
      plan.processes.forEach((proc, i) => {
        console.log(`     ${i + 1}. ${proc.name} (capability: ${proc.capability_id})`);
      });
    }
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
  
  // 3. Query current state
  console.log('\n3. Querying current state...');
  try {
    const state = await sophiaApi.getState({
      limit: 5,
      model_type: 'CWM_A',
      status: 'observed',
    });
    console.log(`   ✓ Retrieved ${state.states?.length || 0} states`);
    
    if (state.states && state.states.length > 0) {
      console.log('\n   Recent states:');
      state.states.slice(0, 3).forEach(s => {
        console.log(`     - ${s.state_id}: ${s.model_type} (${s.status})`);
        console.log(`       Confidence: ${s.confidence?.toFixed(2)}, Source: ${s.source}`);
      });
    }
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
  
  // 4. Run simulation
  console.log('\n4. Running simulation...');
  try {
    const sim = await sophiaApi.runSimulation({
      capability_id: 'grasp_object',
      context: {
        entity_ids: ['block_red_001', 'gripper_001'],
        horizon_steps: 5,
        talos_metadata: {
          force_threshold: 5.0,
          approach_velocity: 0.1,
        },
      },
    });
    console.log(`   ✓ Simulation ID: ${sim.simulation_id}`);
    console.log(`   ✓ Imagined states: ${sim.imagined_states?.length || 0}`);
    console.log(`   ✓ Predicted outcomes: ${sim.predicted_outcomes?.length || 0}`);
    
    if (sim.metadata) {
      console.log('\n   Metadata:');
      console.log(`     Model version: ${sim.metadata.model_version}`);
      console.log(`     Horizon: ${sim.metadata.horizon} steps`);
    }
  } catch (e) {
    console.log(`   ✗ Error: ${e}`);
  }
}


async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('LOGOS SDK Examples');
  console.log('='.repeat(60));
  
  console.log('\nNote: These examples require running Hermes and Sophia services.');
  console.log('If services are not available, you will see connection errors.\n');
  
  // Run Hermes examples
  await hermesExample();
  
  // Run Sophia examples
  await sophiaExample();
  
  console.log('\n' + '='.repeat(60));
  console.log('Examples complete!');
  console.log('='.repeat(60) + '\n');
}

main().catch(console.error);
