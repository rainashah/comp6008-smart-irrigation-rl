# Reusing code from the reinforcement-learning practicals

The project guidelines allow us to adapt implementations from the unit practicals when they are suitable for the selected problem. The final submission must still be our own implementation, demonstrate our understanding of the algorithms, and explicitly connect each algorithm's pseudocode to the corresponding code.

Our irrigation environment has an 18-dimensional continuous observation and one continuous irrigation action. None of the practicals directly implements DDPG, TD3 or SAC. We can reuse general implementation patterns and utilities, but the continuous-control policies and algorithm-specific updates must be implemented for this project.

## Reuse by practical

| Practical | Suitable material to adapt | Required changes or limitations |
|---|---|---|
| Practical 1: Introduction to RL | Gymnasium `reset()` and `step()` loop, observation/action-space inspection, `terminated` and `truncated` handling, and episode-return calculation | Replace the supplied environments with the Kyabram irrigation environment and preserve the distinction between true termination and an external training cut-off |
| Practical 3: MDP and Dynamic Programming | MDP terminology, transition and reward reasoning, and mathematical notation | Dynamic-programming algorithms assume known discrete dynamics and are not suitable agents for our continuous problem |
| Practicals 4–5: Temporal-Difference Learning | TD-target logic and terminal-state handling | The tabular prediction, SARSA and action-selection code does not apply directly to neural continuous control |
| Practical 7: Value Function Approximation | Continuous-observation checks and general function-approximation structure | Tile coding and linear SARSA are not the neural actor–critic methods selected for this project |
| Practical 8: Deep Q-Learning | Replay-memory structure, minibatch sampling, target-network concept, PyTorch optimisation, model saving/loading, and training-loop organisation | Remove DQN's discrete actions, `argmax`, action-index `gather()` operations and output of one Q-value per discrete action |
| Practical 9: Policy Gradient and Actor–Critic | Separation of actor and critic/value networks, MLP construction, Adam updates, TD-target structure, checkpointing and evaluation loops | Replace the categorical discrete policy and on-policy actor–critic updates with continuous policies and the specific DDPG, TD3 and SAC update rules |

Practicals 8 and 9 provide the most useful starting structure.

## Shared components

The following components can be adapted once and used consistently by all three agents:

- replay buffer and minibatch sampling;
- general multilayer-perceptron construction;
- conversion of observations and actions to PyTorch tensors;
- reproducible seed handling;
- Gymnasium environment-interaction loop;
- correct terminal masking in learning targets;
- target-network update helper;
- checkpoint saving and loading;
- training and evaluation metric logging; and
- evaluation loops with learning disabled.

Shared utilities should have one agreed interface so that differences in results are caused by the agents rather than different data handling or evaluation code.

## Components that require new implementation

### DDPG

- deterministic actor producing one bounded continuous action;
- critic receiving both observation and action;
- bounded exploration noise during training;
- deterministic policy-gradient actor update;
- critic target and loss; and
- soft target-network updates.

### TD3

- two independent critics;
- minimum of the two target-Q estimates;
- target-policy smoothing with clipped noise;
- delayed actor and target-network updates; and
- TD3-specific target and loss calculations.

### SAC

For the selected 2018 SAC formulation:

- tanh-squashed Gaussian policy;
- reparameterised action sampling;
- log-probability correction after the tanh transformation;
- fixed entropy coefficient, `alpha`;
- two Q-networks;
- a separate state-value network and target value network; and
- SAC policy, Q-function and value-function losses.

## Code that should not be copied unchanged

Practical 9 uses `torch.distributions.Categorical`, which is only suitable for discrete actions. Our irrigation action is continuous, so DDPG and TD3 require deterministic bounded actors, while SAC requires a continuous tanh-squashed Gaussian policy.

Practical 8's DQN code chooses among discrete actions and computes a maximum over a finite set of action values. DDPG, TD3 and SAC instead provide the action as an input to a critic, so DQN's discrete `argmax`, action-index lookup and one-output-per-action design must not be retained.

The hard periodic target-network copy used in a practical should also not silently replace the selected soft update. Our agents use Polyak updates with `tau = 0.005`, while TD3 additionally delays its actor and target updates according to the algorithm.

## Documentation requirement

For every reused or adapted component, the notebook should identify:

1. the practical that provided the starting structure;
2. what was retained;
3. what was changed for continuous control;
4. where the corresponding pseudocode step appears in the implementation; and
5. which original algorithm paper supports the final update rule.

A suitable description is:

> The implementations adapt the course practicals' PyTorch, Gymnasium, replay-buffer and actor–critic structure. The continuous policies, critic targets and algorithm-specific DDPG, TD3 and SAC updates are implemented from the corresponding original papers.

This approach keeps the implementation consistent with the material taught in the unit while making the algorithm-specific work and our modifications explicit.
