# Dashboard and Integration PRD

**Project:** SIH ’26, SIH26055  
**Component:** Dashboard Application and Integration Layer  
**Prototype Version:** V0.1  
**Purpose:** Receive simulated RF observations, manage the scheduler loop, display system state, calculate performance metrics, and provide a reliable fallback when the AI Engine is unavailable.

---

## 1. Product Objective

The Dashboard shall act as the central application for the Prototype V0.1 system.

It shall receive RF observations from the RF Environment Simulator through HTTP.

It shall maintain the recent time series of receiver observations.

It shall provide the observation history to the AI Engine.

It shall receive the next-band prediction from the AI Engine.

It shall calculate the result of each receiver decision against the simulator ground truth.

It shall send hit or miss feedback to the AI Engine.

It shall calculate the required scheduler metrics.

It shall display the RF environment, receiver state, predictions, outcomes, and performance.

It shall use fallback data when the AI Engine is unavailable.

The Dashboard shall remain operational when the AI Engine fails.

The SIH problem statement requires a machine-learning-based Electronic Support receiver scheduler. It also identifies probability of detection, false alarm probability, average intercept rate, average reward or cost, prediction accuracy, average intercept-time error, interception time, and interception ratio as relevant performance measures.

---

## 2. Fixed Technology Stack

These decisions are fixed for the complete Prototype V0.1.

|Layer|Technology|
|---|---|
|Backend|Python|
|HTTP framework|FastAPI|
|Frontend|Vite + React|
|Data format|JSON|
|API style|HTTP REST|
|Development server|Uvicorn|
|State|In-memory and local JSON files|
|Charts|React-compatible chart library|
|AI integration|HTTP API|

The Dashboard backend shall use Python and FastAPI.

The Dashboard frontend shall use Vite and React.

The prototype shall not introduce another backend or frontend framework.

---

## 3. System Role

The Dashboard shall sit between the RF Environment Simulator and the AI Engine.

The primary loop shall be:

**RF Environment → Dashboard → AI Engine → Dashboard → RF Environment**

The Dashboard shall control the information flow.

The Dashboard shall prevent future ground truth from reaching the AI Engine.

The Dashboard shall retain ground truth for evaluation.

---

## 4. Prototype Scope

The Dashboard shall provide:

- Live RF band activity.
    
- Current receiver band.
    
- Current receiver dwell.
    
- Latest signal observation.
    
- AI prediction.
    
- Prediction confidence.
    
- Next-band decision.
    
- Hit or miss result.
    
- Recent observation history.
    
- Per-band activity history.
    
- Prediction history.
    
- Intercept-time tracking.
    
- Detection metrics.
    
- False-alarm metrics.
    
- Interception ratio.
    
- Average reward.
    
- AI Engine status.
    
- Fallback status.
    
- Simulation controls.
    
- Demo mode.
    
- Local fallback data.
    

The Dashboard shall support a single active simulation for Prototype V0.1.

---

# 5. Application Architecture

The Dashboard shall contain four logical modules.

### 5.1 API Layer

Receives HTTP requests from the RF Simulator.

Provides HTTP endpoints for the frontend.

Provides the AI Engine interface.

### 5.2 State Manager

Stores:

- Current simulation state.
    
- Observation history.
    
- Prediction history.
    
- Hit and miss results.
    
- Performance metrics.
    
- AI Engine state.
    

### 5.3 Scheduler Adapter

The Scheduler Adapter shall communicate with the AI Engine.

It shall normalize the AI response into one internal format.

It shall detect AI Engine timeouts and errors.

It shall activate the fallback engine when required.

### 5.4 Dashboard Frontend

The Vite and React application shall display the current system state.

It shall update without requiring a full page refresh.

---

# 6. Data Flow

The Dashboard shall execute this sequence for each receiver observation.

1. Receive the RF observation.
    
2. Validate the request.
    
3. Store the observation.
    
4. Add the observation to the time series.
    
5. Prepare the AI input.
    
6. Send the input to the AI Engine.
    
7. Use the AI response when the AI Engine responds correctly.
    
8. Use fallback data when the AI Engine fails.
    
9. Apply the selected receiver band.
    
10. Compare the decision against ground truth.
    
11. Calculate hit or miss.
    
12. Calculate the current performance metrics.
    
13. Send feedback to the AI Engine.
    
14. Return the next receiver decision to the RF Simulator.
    
15. Update the frontend.
    

The Dashboard shall complete this cycle for every simulation slot.

---

# 7. RF Observation Contract

The Dashboard shall accept the RF Event Contract defined by the RF Environment Simulator.

The initial request format shall be:

```text
POST /api/v1/rf/observation
```

The payload shall contain:

- Simulation identifier.
    
- Simulation timestamp.
    
- Receiver band.
    
- Receiver dwell.
    
- Detection state.
    
- Signal strength.
    
- Ground-truth outcome for evaluation.
    

The Dashboard shall validate all required fields.

Invalid requests shall receive an HTTP 400 response.

---

# 8. Ground Truth Handling

The Dashboard shall receive ground truth from the simulator for evaluation.

The Dashboard shall store ground truth separately from the AI input.

The AI Engine shall not receive:

- Future emitter states.
    
- Future transmission states.
    
- Future band activity.
    
- The current observation outcome before making its decision.
    

The AI Engine may receive the ground truth **after** the decision.

This feedback allows the model to learn from hits and misses.

The SIH problem statement explicitly describes a simulated RF environment with truth information for emitter status at each band and time slot. It also requires model training based on hits and misses.

---

# 9. AI Input Contract

The Dashboard shall provide a time-series window to the AI Engine.

Prototype V0.1 shall use a configurable observation window.

Default:

**20 previous simulation slots.**

The input shall contain information available to the receiver.

Example fields:

- Timestamp.
    
- Receiver band.
    
- Dwell time.
    
- Detection result.
    
- Signal strength.
    
- Previous selected bands.
    
- Previous hit or miss results.
    
- Recent prediction values.
    

The AI Engine shall not receive future observations.

The AI Engine shall not receive future ground truth.

---

# 10. AI Decision Contract

The Dashboard shall request one scheduling decision from the AI Engine.

The AI Engine shall return:

- Next band.
    
- Dwell time.
    
- Prediction probability.
    
- Confidence.
    

The required internal format shall be:

```text
next_band
dwell_ms
prediction
confidence
```

The Dashboard shall accept the decision only when the values pass validation.

`next_band` shall be between 1 and 8.

`prediction` shall be between 0 and 1.

`confidence` shall be between 0 and 1.

`dwell_ms` shall be greater than zero.

---

# 11. AI Engine Failure Handling

The Dashboard shall set a short timeout for AI requests.

The Dashboard shall treat these conditions as AI failure:

- Connection failure.
    
- Timeout.
    
- HTTP error.
    
- Invalid JSON.
    
- Missing required fields.
    
- Invalid numerical values.
    
- AI Engine exception.
    

When an AI failure occurs, the Dashboard shall select the fallback decision.

The Dashboard shall continue the simulation.

The Dashboard shall not block the demonstration because of an AI failure.

---

# 12. Fallback Engine

The Dashboard shall contain a deterministic fallback engine.

The fallback engine shall use pre-generated scheduler decisions.

The fallback dataset shall contain at least **500 records**.

The preferred prototype target shall be **1,000 records**.

Each record shall contain:

- Timestamp.
    
- Selected band.
    
- Prediction.
    
- Confidence.
    
- Expected result.
    
- Intercept time.
    
- Reward.
    

Example fields:

```text
timestamp
selected_band
prediction
confidence
actual
result
intercept_time_ms
reward
```

The fallback data shall follow the same schema as the AI Engine output.

This allows the Dashboard to use either source without changing the display pipeline.

---

# 13. Fallback Behaviour

The Dashboard shall select the fallback engine when the AI Engine becomes unavailable.

The Dashboard shall mark the active decision source internally.

The frontend may show the source status in a small system indicator.

The main dashboard shall continue to show the same metrics and charts.

The fallback engine shall produce a coherent sequence rather than independent random values.

The fallback sequence shall correspond to one of the simulator's predefined scenarios.

This prevents the demonstration from displaying contradictory RF activity and scheduler decisions.

---

# 14. Fallback Dataset Design

The fallback dataset shall contain multiple scenario sequences.

Suggested structure:

- 250 records for periodic behaviour.
    
- 250 records for bursty behaviour.
    
- 250 records for frequency-agile behaviour.
    
- 250 records for mixed behaviour.
    

The Dashboard shall select the sequence that matches the active simulation scenario.

The fallback dataset shall remain deterministic.

The dataset shall not depend on external network access.

The demonstration shall therefore continue if the AI Engine, network connection, or model service fails.

---

# 15. Hit and Miss Calculation

The Dashboard shall calculate hit or miss after the receiver observes the selected band.

The calculation shall use simulator ground truth.

The basic condition shall be:

**Selected band matches an active detectable emitter → HIT**

Otherwise:

**MISS**

The Dashboard shall record the result with the corresponding simulation timestamp.

The Dashboard shall not use the AI prediction itself to determine whether a hit occurred.

Prediction and observation shall remain separate values.

---

# 16. Feedback Contract

After the Dashboard calculates the outcome, it shall send feedback to the AI Engine.

The feedback shall contain:

- Selected band.
    
- Prediction.
    
- Confidence.
    
- Detection result.
    
- Signal strength.
    
- Hit or miss.
    
- Intercept time.
    
- Reward.
    
- Recent observation context.
    

The feedback shall allow the AI Engine to update its scheduling model.

The Dashboard shall not perform model training itself.

---

# 17. Matrix Update Interface

The AI Engine may maintain a band-transition or activity matrix.

The Dashboard shall provide the latest observation and outcome.

The AI Engine shall decide how to update its internal matrix.

The Dashboard shall not assume a particular learning algorithm.

This preserves the separation between the integration layer and the AI implementation.

A possible later representation is:

**P(next active band | current state and recent observations)**

The actual learning method shall be defined in the AI Engine PRD.

---

# 18. Dashboard Layout

The primary dashboard shall contain six areas.

### Area 1: System Status

Display:

- Simulation status.
    
- AI Engine status.
    
- Active decision source.
    
- Simulation timestamp.
    
- Current scenario.
    

Example:

**SIMULATION: RUNNING**

**AI ENGINE: LIVE**

**SCENARIO: MIXED**

---

### Area 2: RF Spectrum

Display all eight bands.

Each band shall show:

- Band identifier.
    
- Current activity.
    
- Predicted activity.
    
- Current receiver state.
    

Example:

|Band|Predicted Activity|Receiver|
|---|--:|---|
|1|24%||
|2|81%||
|3|43%||
|4|12%||
|5|72%||
|6|91%|**CURRENT**|
|7|31%||
|8|64%||

The display shall update after each simulation slot.

---

# 19. Receiver Panel

The receiver panel shall show:

- Current band.
    
- Dwell time.
    
- Latest signal strength.
    
- Detection status.
    
- Last result.
    
- Next selected band.
    

Example:

**CURRENT BAND:** 6

**DWELL:** 100 ms

**SIGNAL:** -61.4 dB

**RESULT:** HIT

**NEXT BAND:** 3

---

# 20. AI Prediction Panel

The AI panel shall show:

- Predicted activity for each band.
    
- Selected next band.
    
- Prediction probability.
    
- Confidence.
    
- Decision source.
    

Example:

**NEXT BAND: 3**

**PREDICTED ACTIVITY: 78%**

**CONFIDENCE: 84%**

**SOURCE: AI ENGINE**

The Dashboard shall not require natural-language reasoning from the AI Engine.

The first prototype shall use structured prediction fields.

---

# 21. Time-Series Panel

The Dashboard shall display the activity history of the RF bands.

The user shall be able to select a band.

The chart shall show:

- Time.
    
- Observed activity.
    
- Predicted activity.
    
- Receiver selections.
    
- Hit or miss events.
    

The chart shall use the stored simulation history.

The Dashboard shall retain enough history to show the current demonstration session.

---

# 22. Observation Table

The Dashboard shall display recent observations.

Required columns:

|Time|Band|Prediction|Actual|Result|Confidence|
|---|--:|--:|--:|---|--:|

The table shall update as new observations arrive.

The user shall be able to view at least the latest 20 observations.

---

# 23. Performance Metrics

The Dashboard shall calculate the metrics required by the SIH problem statement.

### Detection

- Probability of detection.
    
- False alarm probability.
    

### Scheduler

- Average intercept rate.
    
- Average intercept time.
    
- Average intercept-time error.
    
- Interception ratio.
    

### Prediction

- Prediction accuracy.
    
- Prediction confidence.
    

### Reward

- Average reward.
    
- Average cost where the selected reward formulation uses cost.
    

The Dashboard shall calculate these metrics from the stored simulation history.

The SIH problem statement lists these measures as figures of merit for the proposed receiver scheduler.

---

# 24. Intercept Time

The Dashboard shall track the time between emitter activation and successful receiver interception.

For each emitter event:

**Intercept Time = Detection Time - Emitter Activation Time**

The Dashboard shall retain completed intercept events.

The Dashboard shall calculate average intercept time from completed events.

The Dashboard shall not treat a prediction as an interception.

Only an actual receiver hit shall close an intercept event.

---

# 25. Interception Ratio

The Dashboard shall calculate the proportion of relevant emitter events that the receiver successfully intercepts.

Prototype V0.1 shall define:

**Interception Ratio = Successfully intercepted events / Relevant emitter events**

The Dashboard shall use the simulator ground truth to determine relevant events.

The exact event grouping can change when the AI Engine specification defines the final evaluation protocol.

---

# 26. Reward

Prototype V0.1 shall support a normalized reward value.

The exact reward formula shall remain configurable.

A preliminary reward model may consider:

- Successful hit.
    
- Intercept time.
    
- Repeated scans of inactive bands.
    
- Missed active emitters.
    

The AI Engine shall receive the reward value as feedback.

The final reward function shall be fixed when the AI Engine PRD is defined.

---

# 27. Baseline Comparison

The Dashboard shall support comparison against sequential scanning.

Baseline schedule:

**1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → repeat**

The Dashboard shall calculate baseline performance from the same RF scenario.

The Dashboard shall show:

|Metric|Sequential|AI|
|---|--:|--:|
|Detection Rate|||
|Average Intercept Time|||
|Interception Ratio|||
|Average Reward|||

This comparison gives the demonstration a measurable reference point.

The supplied research discusses periodic receiver scan strategies and evaluates them through probability of intercept and intercept-time measures.

---

# 28. Simulation Controls

The Dashboard shall provide:

- Start.
    
- Pause.
    
- Resume.
    
- Reset.
    
- Scenario selection.
    
- Simulation speed.
    

The Dashboard shall send simulation control requests to the RF Simulator.

The Dashboard shall not directly modify emitter state.

The RF Simulator remains the owner of RF environment state.

---

# 29. Demo Mode

The Dashboard shall support a dedicated demo mode.

Demo mode shall:

- Start with a known scenario.
    
- Use a known simulation seed.
    
- Load the fallback dataset.
    
- Start the RF Simulator.
    
- Start the scheduler loop.
    
- Display live metrics.
    
- Continue without external services.
    

The demo mode shall not require internet access.

The AI Engine may replace the fallback source when it becomes available.

---

# 30. AI Engine Status

The Dashboard shall track the AI Engine state.

Supported states:

**LIVE**

The AI Engine responds within the configured timeout.

**FALLBACK**

The Dashboard uses the local fallback engine.

**ERROR**

The latest AI request failed.

The scheduler shall continue when the state is `FALLBACK`.

---

# 31. HTTP API

The Dashboard backend shall expose the following endpoints.

### RF Observation

`POST /api/v1/rf/observation`

Receives one receiver observation from the simulator.

---

### Dashboard State

`GET /api/v1/dashboard/state`

Returns the current dashboard state.

---

### History

`GET /api/v1/history`

Returns recent observation and scheduler history.

---

### Health

`GET /api/v1/health`

Returns Dashboard health.

---

### Simulation Start

`POST /api/v1/simulation/start`

Starts the connected RF simulation.

---

### Simulation Pause

`POST /api/v1/simulation/pause`

Pauses the connected RF simulation.

---

### Simulation Resume

`POST /api/v1/simulation/resume`

Resumes the connected RF simulation.

---

### Simulation Reset

`POST /api/v1/simulation/reset`

Resets the connected RF simulation.

---

# 32. AI Engine API

The Dashboard shall use a separate AI Engine interface.

Suggested endpoint:

`POST /api/v1/agent/predict`

The Dashboard shall send:

- Observation window.
    
- Current receiver state.
    
- Previous decisions.
    
- Previous outcomes.
    
- Previous rewards.
    

The AI Engine shall return:

- Next band.
    
- Dwell time.
    
- Prediction values.
    
- Confidence.
    

Suggested feedback endpoint:

`POST /api/v1/agent/feedback`

The Dashboard shall send the result after the receiver completes its observation.

The exact AI API may change when the AI Engine PRD defines the model.

The internal Dashboard contract shall remain stable.

---

# 33. Dashboard State Model

The Dashboard shall maintain one internal state object.

It shall contain:

- Simulation status.
    
- Current timestamp.
    
- Current receiver band.
    
- Current dwell.
    
- Latest observation.
    
- Latest prediction.
    
- Latest decision.
    
- Latest result.
    
- Recent history.
    
- Metrics.
    
- AI status.
    
- Decision source.
    

The frontend shall obtain this state through the Dashboard API.

---

# 34. Error Handling

The Dashboard shall handle:

- Invalid simulator requests.
    
- Missing fields.
    
- Invalid band identifiers.
    
- AI timeout.
    
- AI connection failure.
    
- AI invalid response.
    
- Simulator disconnection.
    
- Empty history.
    
- Fallback dataset exhaustion.
    

The Dashboard shall return structured error responses.

The frontend shall display actionable system status.

The backend shall log technical error details.

---

# 35. Fallback Dataset Exhaustion

If the fallback dataset reaches its final record, the Dashboard shall restart the sequence.

The sequence shall retain its deterministic order.

The Dashboard shall reset the fallback timestamp to the current simulation timestamp.

The simulation shall not stop because the fallback dataset ends.

---

# 36. Local Persistence

Prototype V0.1 shall not require a database.

The Dashboard shall keep active state in memory.

The Dashboard may write completed simulation sessions to local JSON or JSON Lines files.

Suggested structure:

`data/runs/`

Each run shall contain:

- Simulation ID.
    
- Scenario.
    
- Seed.
    
- Observations.
    
- Decisions.
    
- Outcomes.
    
- Metrics.
    

---

# 37. Information Security Boundary

Prototype V0.1 shall operate in a local development environment.

The system shall not require authentication.

The system shall not use real operational RF data.

The simulator shall use synthetic frequency identifiers.

The prototype shall not transmit classified or sensitive emitter information.

These constraints apply to the demonstration environment.

---

# 38. Performance Requirements

The Dashboard shall process one observation per simulation slot.

The target prototype loop shall support at least 10 simulation slots per second.

The Dashboard shall not require database access for each observation.

The frontend shall update without a full page reload.

The AI timeout shall not block the Dashboard indefinitely.

The fallback engine shall respond locally.

---

# 39. Prototype Acceptance Criteria

The Dashboard shall be considered complete when it can:

- Receive RF observations through FastAPI.
    
- Validate the RF Event Contract.
    
- Store observation history.
    
- Maintain separate ground truth.
    
- Build an AI observation window.
    
- Send an AI prediction request.
    
- Receive and validate an AI decision.
    
- Detect AI failures.
    
- Switch to fallback data.
    
- Calculate hit or miss.
    
- Calculate intercept time.
    
- Calculate interception ratio.
    
- Calculate detection rate.
    
- Calculate false alarm rate.
    
- Calculate prediction accuracy.
    
- Calculate average reward.
    
- Display eight RF bands.
    
- Display the current receiver band.
    
- Display AI predictions.
    
- Display recent observations.
    
- Display time-series data.
    
- Display performance metrics.
    
- Compare AI scheduling with sequential scanning.
    
- Control the RF Simulator.
    
- Continue the demonstration after AI failure.
    
- Run locally without internet access.
    

---

# 40. Explicit Non-Goals

Prototype V0.1 shall not implement:

- User authentication.
    
- Multi-user access.
    
- Cloud deployment.
    
- Production database infrastructure.
    
- Role-based access control.
    
- Mobile application.
    
- Real SDR integration.
    
- Raw RF waveform display.
    
- Complex GIS visualization.
    
- Advanced signal processing.
    
- Natural-language AI explanations.
    
- Autonomous model architecture changes.
    
- Automated hyperparameter search.
    
- Distributed inference.
    
- Multi-receiver coordination.
    
- Production cybersecurity controls.
    

These features can be considered after the prototype validates the scheduling concept.

---

# 41. End-to-End Prototype Flow

The final Prototype V0.1 loop shall follow this sequence:

**1. RF Simulator generates the current environment.**

**2. RF Simulator selects the current receiver band.**

**3. RF Simulator generates the receiver observation.**

**4. RF Simulator sends the observation to the Dashboard.**

**5. Dashboard stores the observation and ground truth.**

**6. Dashboard sends the available time-series context to the AI Engine.**

**7. AI Engine returns the next-band prediction.**

**8. Dashboard uses the AI decision when the AI Engine responds correctly.**

**9. Dashboard uses the fallback decision when the AI Engine fails.**

**10. Dashboard calculates hit or miss after the observation.**

**11. Dashboard calculates intercept and performance metrics.**

**12. Dashboard sends feedback to the AI Engine.**

**13. AI Engine updates its internal prediction state.**

**14. Dashboard returns the next receiver decision to the RF Simulator.**

**15. RF Simulator advances the simulation clock.**

**16. The cycle repeats.**

---

# 42. Definition of Done

The Dashboard and Integration Layer shall be ready for the first demonstration when the complete closed loop works locally.

The required loop is:

**RF Simulator → HTTP POST → Dashboard → AI or Fallback → Hit/Miss → Metrics → Next Decision → RF Simulator**

The Dashboard shall remain functional when the AI Engine fails.

The fallback dataset shall contain at least 500 records.

The Dashboard shall expose the scheduler behaviour through live visualizations.

The Dashboard shall provide quantitative evidence that compares intelligent scheduling with sequential scanning.

The architecture shall allow the AI Engine implementation to change without requiring changes to the RF Simulator or the Dashboard frontend.

The final prototype shall therefore demonstrate the central SIH26055 concept: a receiver that uses observations and learned emitter behaviour to choose where to scan next, with the goal of reducing intercept time and maintaining a high interception rate.