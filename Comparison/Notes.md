# Notes:

Based on the comparison signal, there's some conclusion that we can take here.

There's no way we can have consistent value for the HRV analysis. It's because HRV analysis are based on the RR-interval.

This RR-interval require you to pre-process data in such manner it was cleaned and the peaks are correctly identified.

My method that I'm using here and the framework as the comparator, is based on my pure assumption if the data is clean and every peak is the pure beat (Even though I don't know).

One last thing is also cleaning the RR-interval data. since the maybe an anomalies since RR distance can't be 300 and clearing the outlier based on the limitations

> Physiological Range: The RR intervals should typically be within the range of 300 ms (0.3 s) to 1300 ms (1.3 s). This range corresponds to heart rates between approximately 46 bpm and 200 bpm, which covers most normal physiological conditions

I guess with the result on Time and Freq domain, I'm sure I can move on with Caution later..

20 Jan 2025
