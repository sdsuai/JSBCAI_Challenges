# **Assignment: Circuit Simulation — A Robot's Power & Signal Chain**

**JSBCAI / Robotics Lab — Electrical Engineering Task**

* All simulation in this task runs on **free software** on any laptop (Windows/macOS/Linux). No hardware, no paid licenses.
* After completing this task you will need to screen record a video showing your simulations running and you explaining how they work.
* Create a github repo containing your files and the video. Name the repo something like "JSB_EE_interview_problem" or something like that so it's identifiable.
* **IMPORTANT (READ THE ENTIRE BULLET POINT) For submission you must:**
   - **submit a pull request to this repo so that we have access to your username and can find your repo. However, so others don't copy your work, do not do your work in the public forked repo.**
   - **Make a private clone (or however you make things private) of the forked repo and do your actual work there.**
   - **Send an invite to me to the private repo (philipamadasun1@gmail.com) so I can gain access.**
   - **In your ReadME, make sure to provide your email address.**
* You may freely use any tool available to you to accomplish this task. The internet, ChatGPT, anything. However, **your submitted work must be your own**, and your demo video must clearly demonstrate that **you personally understand your circuits**.

---

## **Tools (pick one — all free)**

| Tool | Platforms | Notes |
| ---- | --------- | ----- |
| **LTspice** (recommended) | Win / macOS | Industry-standard SPICE, huge built-in part library |
| **KiCad 8+** | Win / macOS / Linux | Schematic editor with built-in ngspice simulation |
| **ngspice** (CLI) | Linux / all | The starter netlists in `examples/` run directly: `ngspice -b examples/rc_lowpass.cir` |
| Falstad CircuitJS (browser) | any | **Prototyping/intuition only** — final deliverables must be SPICE files we can re-run |

**Deliverable rule:** for every task you must include the **runnable simulation source files** (`.asc`, KiCad project, or `.cir` netlists) — not just screenshots. If we can't re-run your sim, it doesn't count.

Starter netlists showing the mechanics (AC sweep, transient analysis, PWM switching, measurements) are in `examples/`. They use **different component values than the assignment asks for** — adapt them, don't copy them.

---

## **Scenario**

You are designing the electronics that sit between a small robot's battery and its brain:

```
                 ┌────────────► 5 V regulator ──► MCU + ADC
  battery (2S)───┤                                   ▲
                 └──► MOSFET ◄─ PWM from MCU         │ 0–3.3 V
                       │                        op-amp stage
                     motor                           ▲
                                                 RC filter
                                                     ▲
                                              analog sensor
```

Four required tasks, one per block. Each task = design math + simulation(s) + plots + short written answers.

---

## **Task 1 — Sensor noise filter (RC low-pass) [20 pts]**

An analog distance sensor outputs a useful signal below ~200 Hz, but picks up switching noise from the motor PWM. Design a **first-order RC low-pass** with **cutoff fc ≈ 1.6 kHz (±10%)** using standard component values. Show the math for your R and C choice.

**Simulations:**

1. **AC sweep** (10 Hz – 1 MHz): Bode magnitude plot with the −3 dB point marked. Does the measured fc match your math?
2. **Transient:** input = 100 Hz, 1 V-amplitude sine (the "signal") **plus** 50 kHz, 0.1 V-amplitude sine (the "noise") — see `examples/rc_lowpass.cir` for how to sum two sources in series. Overlay input and output; report the noise amplitude before and after.

**Answer in your README:**

* What attenuation (in dB) does your filter give at 50 kHz — read from the Bode plot **and** computed from `20·log10(1/√(1+(f/fc)²))`. Do they agree?
* Now connect a **10 kΩ load resistor** across the capacitor (a cheap ADC input) and re-run the AC sweep. What happened to the DC level and to fc, and why? What does this tell you about why buffers exist?

---

## **Task 2 — Signal scaling (op-amp) [20 pts]**

The sensor (after filtering) outputs **0–0.5 V**; your ADC wants **0–3.3 V**. Design a **non-inverting amplifier** with gain ≈ 6.6 using standard E12 resistor values, powered from a **single 5 V supply**.

Use a **real op-amp model, not an ideal one** (LTspice: any single-supply part in the library, e.g. LT1013; KiCad/ngspice: any vendor SPICE model — say in your README where you got it).

**Simulations:**

1. **DC sweep** Vin from 0 → 1 V: plot Vout vs Vin. Mark the linear region and where it saturates.
2. **Transient** with a 0–0.5 V, 50 Hz triangle wave input.

**Answer in your README:**

* At what output voltage does your amplifier clip, and why is it not 5 V?
* Does your chosen op-amp actually reach 3.3 V from a 5 V supply? Check its output-swing spec. What op-amp property would guarantee it (name the term), and name one other way to rescue the design if you were stuck with this part.
* Your sensor glitches to 1 V for a moment. What does the amplifier output do, and why is that clipping actually *protecting* the ADC here?

---

## **Task 3 — Power: regulation and the price of linear [15 pts]**

The robot runs on a 2S lithium pack: **8.4 V full, ~6.0 V empty**. Logic wants 5 V.

**(a) Simulate a Zener shunt regulator:** 5.1 V Zener + series resistor, feeding a **50 mA load** (≈100 Ω). Choose the series resistor so regulation still holds with the battery nearly empty — show the math (a generic diode model with `BV=5.1` is fine; LTspice also has real Zeners like BZX84C5V1).

* **DC sweep** the battery from 5 → 9 V: plot Vout. Where does the regulator "fall out" of regulation, and why there?
* At a **full** battery, how much power is burned in the series resistor and Zener combined? Who is eating those watts, and what does that mean for a battery-powered robot?

**(b) Arithmetic only (no sim):** a linear pass regulator (LM7805-style) supplies **200 mA at 5 V from 7.4 V**.

* Power dissipated in the regulator? Efficiency?
* Same load from an ideal **buck converter** at 90% efficiency: input power drawn?
* Roughly how much longer does the battery last with the buck? (Ratio is enough.)

**Answer in your README:** why do linear regulators get hot, and name one situation where linear is still the *right* choice.

---

## **Task 4 — PWM motor drive [25 pts]**

The core of the robot. Model the motor as **5 Ω in series with 1 mH** (winding resistance + inductance; note in your README what physical effect this model *ignores* — hint: it's exact only for a stalled rotor). Battery = 7.4 V. Drive the motor with a **low-side N-MOSFET** switched by a 0/5 V gate pulse at **20 kHz**, with a **flyback diode** across the motor. Starter mechanics: `examples/pwm_motor.cir`.

**Simulations:**

1. **Transient at duty = 25%, 50%, 75%:** motor current waveforms, plus a table (or plot) of **average motor current vs duty**. Is it roughly linear? Compare against `I_avg ≈ D·V/R`.
2. **Ripple at 50% duty:** measure the peak-to-peak current ripple and compare to `ΔI = V·D·(1−D)/(L·f)`.
3. **The big one — delete the flyback diode** and re-run. Plot the MOSFET **drain voltage** at switch-off and report the spike. If the simulator complains or shows megavolts: give the drain node the ~100 pF of capacitance a real MOSFET has (the starter shows where) and watch it **ring** instead.

**Answer in your README:**

* Where does the spike come from? Walk through `v = L·di/dt` at the moment the switch opens: what does the inductor current *want* to do, and what path does it have?
* What exactly does the flyback diode do during the off-time?
* Why 20 kHz and not 200 Hz or 2 MHz? (Two different reasons — one you could *hear*, one that burns watts in the switch.)

---

## **Tier 2 (Extra Credit — choose one) [+10]**

### **Option A — H-bridge + shoot-through**

Build a 4-switch H-bridge around the same motor model and show **forward and reverse** operation (motor current changes sign). Then the classic failure: **overlap** the gate signals on one leg by ~1 µs so both switches conduct at once, and plot the **supply current spike** (shoot-through). Add **dead time** and show it gone. Explain why every motor-driver IC has dead time built in.

### **Option B — Buck converter**

Open-loop buck (switch + diode + L + C) from 7.4 V to ≈5 V at duty ≈ Vout/Vin. Show the output ripple, the average output voltage, and the inductor current waveform. Connect it back to Task 3(b): where did the "wasted" watts go this time?

---

## **Deliverables (repo layout)**

```
sims/     runnable simulation sources, one folder or file per task
plots/    exported plots, axes labeled (nobody can grade an unlabeled axis)
README.md design math, plots inline, and the written answers for every task
video     4–8 min (or link in README)
```

**Video requirements:** run at least **Task 1 and Task 4 live** in your simulator; show each task's key plot; explain the no-diode voltage spike **in your own words** — that explanation is worth more than the plot.

---

## **Grading Rubric**

| Category | Points |
| -------- | ------ |
| Task 1 — RC filter (design, sims, loading answer) | 20 |
| Task 2 — Op-amp stage (real model, clipping explained) | 20 |
| Task 3 — Regulation + efficiency arithmetic | 15 |
| Task 4 — PWM drive (duty sweep, ripple, spike) | 25 |
| README write-up quality | 10 |
| Demo video | 10 |
| **Tier 2 Extra Credit** | +10 |

Maximum: **100 (+10 bonus)**
