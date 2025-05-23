### Notes regaring rPPG extraction.

It seems the rPPG methods of LGI, GREEN and OMIT are basically the same,
So let's using the LGI for the sake of the simplicity

But for a note, let's extract all features.

#### Todos

Plot the individual time frame, the GT shows combined version of all of it

Update the bsi to earlier one,

upate the HRV-features methods to work with the neurokit and bandpass filter methods - Upsampling the data to 100 Hz

work with dataset physio itera

### Uptake

Bland-altman is fine, but we can correct it with linear regression and other model to make less bias

This leaves a question, since the short term have much more data since windowing, compare to the full / Y variable, how does one correlate / plot the bland-altman

Approach A: Aggregate Short Windows Per Subject

Make jupyter files on several subject test and see which one is better. each file containing unique test case like file a is for subject T1 and etc.

### Insight

Stress is not a universal state marked by a single HRV cutoff — it’s a relative shift in autonomic balance. For research and applications, this means contextual HRV interpretation (baseline vs. current) is key, especially for real-time stress inference.
