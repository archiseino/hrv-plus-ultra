## Notes

It seems the general Time window are the minimum 2 minute length samples. So the best shot is to make a sliding window every 30 seconds.

Doing interpolation it seems doesn't do much, rather make an artifact that suddenly increase the value in Spectral analysis artificially.

Using HHT (Hilbert Huang Transform) is another candidate for slower time window Freq Analysis, but still figure it out how does that work.

Another solution is just drop the Freq analysis.
