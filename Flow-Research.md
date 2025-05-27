# Flow of the Research

### Introduction

**What does that mean?**
Even if your heart beats around **70 times per minute** (which is typical for a healthy person at rest), the time between each beat isn’t exactly the same.

So, for example in 10 seconds of your heart beat, your heart might beat faster during few seconds, and a bit slower in the next. That small change in the timings between the beat is normal - and actually a good sign.

It show that your body can adapt to things like breathing, movement or even stress.

That's the core of the HRV and we can utilize this concept to make the Real Time Stress Detection

### To get know better about the HRV Features

HRV is not a number, but a collection of features / metrics that describe your heartbeat timings changes.

#### NN : Beat to Beat Timings (Time Domain)

NN is a concept of calculating the timings between each beat, then we calculate the mean of the timings, the standard deviation over the entire sample.

NN interval are the times between each heartbeat over the window. We normally calculate things like

- Mean NN: The average time between beats
- SDNN: The standard deviation of the NN (how much the intervals vary)

🧠 A heart that's too steady (with low variation) means the body is under pressure / stress. A healthy heart changes the ritme of the heart rate depending on the state (like resting), so it has high variation in timings.

⏱️ Other Time-Based Features from NN Intervals

- RMSSD: Root Mean Square of Successive Differences, sounds complicated but this means: How much does the timing between beats change from one beat to the next?
- pNN50: Looks for the percentage of the differences between peaks that is over 50 milis. Why 50 milis?
  - Why 50 ms? Because it's a good marker that shows if your heartbeat is actively changing — and that’s a healthy sign.
- Mean HR: Look for the mean value of the Heart Rate

### Looking the Overall Components of the Signal (Frequency Domain)

The NN Interval metrics tells us about the timings between each heartbeat.

But we can look the overall waves / pattern of the signal, we can observe which frequency that makes up the signal and how strong does the frequency itself contribute.

This is known by Frequency Analysis. It helps us see what kinds of rhythms (frequencies) are hidden inside the heartbeat signal — and how much power (or strength) each rhythm has.

1. High Frequency (HF) – The Chill Zone
   - Related to your breathing and the relaxed part of your nervous system (called the parasympathetic system).
   - More HF power = your body is relaxed and in recovery mode
2. Low Frequency (LF) – The Balance Zone
   - This one is trickier. It’s influenced by both stress and relaxation systems.
   - LF power often goes up when you’re focused, solving problems, or feeling pressure.
3. LF/HF Ratio – Your Inner Balance Scale
   - This ratio compares how much stress vs. relaxation power

🧠 So, by looking at the frequency powers, we can tell if your body is more like: 🔥 "Fight or Focus" or 🧘 "Rest and Recover"

### Looking the Pattern of the Signal (Non-Linear Analysis)

Your heart doesn’t just beat fast or slow, or have simple rhythms like high or low frequencies.

Sometimes, your heart behaves in ways that are more complex and harder to predict.

Non-linear analysis helps us understand the pattern of your heartbeat signal — whether it’s smooth, regular, or more chaotic.

1. A healthy heart has a bit of chaos — but not too much.

   - It adapts to everything you do: breathing, moving, thinking, even your mood.

2. A less healthy or stressed heart might be:
   - Too predictable (like a metronome): Could mean the body is under pressure and not adapting well.
   - Too messy or chaotic: Could suggest the system is unstable or struggling to self-regulate.

Common features

1. SD1 (Short-term variability)
   ➤ Measures how much the beat-to-beat timing changes from one beat to the next
   ➤ Bigger SD1 = more flexibility in your heart, good sign for relaxation and recovery
2. SD2 (Long-term variability)
   ➤ Looks at the slower, longer-term changes in your heartbeat rhythm
   ➤ Bigger SD2 = your body’s heart rhythm changes more gradually over time

### Study Correlation on the Short Term HRV vs Full HRV

People say that the more data or time you have, the better you can understand something. This is true for HRV too — the longer we measure your heart’s activity, the more accurate and reliable the HRV features will be.

But here’s the question: If we only measure your heart for a short time, like 30 seconds, 1 minute, or 2 minutes, can we still learn useful information? Or do we need a longer measurement to understand it well?

If short measurements can still give us good info, it means there’s a connection (or correlation) between short-term and full-term HRV. That’s great because it means we could use short HRV checks to detect things like stress in real time — quickly and easily.

This study often takes the features / metrics from different window and compare it with the full length, if we got a positive / negative correlation.

### Inference Process: Can We Use This for Real-Time Stress Detection?

Even if we find that short HRV features are strongly correlated with full-length ones, that alone doesn't prove they can detect stress.

To move forward, we:

1. Take the short HRV features.
2. Train a machine learning (ML) model to recognize patterns linked to stress.
3. Validate it (using cross-validation or testing on new data).
4. Use the trained model for real-time stress detection.

⚠️ Keep in mind: Results may vary by person or situation. This is a starting point for future research — not a final answer.

### Update

Since the nature of the data of the rPPG and PPG is basically different, I guess we can cherry picking the best feature with the correction of the Pearson r > .5, as the base for other research on this.

For the model itself, let's try to using the Traditional one, and the data from each window hrv metrics.

This is a weakness, but can be put as saran for future research?

### Update Model

Some model gives the accuracy of 80 is percentage, does it is overfitting? I dunno

Todos, try to also include the HR
