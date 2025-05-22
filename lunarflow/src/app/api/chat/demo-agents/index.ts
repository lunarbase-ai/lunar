import { analyticAgent } from "../mocked/analytic-agent";
import { bioMarkersAgent } from "../mocked/bio-markers.agent";
import { grantFinderAgent } from "../mocked/grant-finder";
import { litReviewAgent } from "../mocked/lit-review.agent";
import { normalizedDbAgent } from "../mocked/normalizedDBAgent";
import { simulationAgent } from "../mocked/simulation.agent";
import { LunarAgent, LunarAgentEvent } from "../types";

export const agents = [
  analyticAgent,
  normalizedDbAgent,
  litReviewAgent,
  simulationAgent,
  bioMarkersAgent,
  grantFinderAgent
]

export async function* runAgent(agent: LunarAgent, toolCallId: string) {
  let elapsedTime = 0
  for (let i = 0; i < agent.reasoningChain.length; i++) {
    const componentInvocation: LunarAgentEvent = {
      type: 'lunar-component-invocation',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: null
      }
    }
    yield componentInvocation
    await new Promise(r => setTimeout(r, agent.reasoningChain[i].executionTime * 1000));
    elapsedTime += agent.reasoningChain[i].executionTime
    const componentResult: LunarAgentEvent = {
      type: 'lunar-component-result',
      toolCallId: toolCallId,
      reasoningChainComponent: {
        ...agent.reasoningChain[i],
        output: agent.reasoningChain[i].output,
      }
    }
    yield componentResult
  }
  const reasoningComplete: LunarAgentEvent = {
    type: 'lunar-agent-result',
    toolCallId: toolCallId,
    runningTime: elapsedTime,
    manualtime: agent.manualTime,
  }
  yield reasoningComplete
}
