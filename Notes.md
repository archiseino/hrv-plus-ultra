We recommend that you:

Use pip only after conda

- Install as many requirements as possible with conda then use pip.
- Pip should be run with --upgrade-strategy only-if-needed (the default).
- Do not use pip with the --user argument, avoid all users installs.

Use conda environments for isolation

- Create a conda environment to isolate any changes pip makes.
- Environments take up little space thanks to hard links.
- Care should be taken to avoid running pip in the root environment.

Recreate the environment if changes are needed

- Once pip has been used, conda will be unaware of the changes.
- To install additional conda packages, it is best to recreate the environment.

Store conda and pip requirements in text files

- Package requirements can be passed to conda via the --file argument.
- Pip accepts a list of Python packages with -r or --requirements.
- Conda env will export or create environments based on a file with conda and pip requirements.

As for best practice, try to recreate the conda (store the dependencies into `requirements.yml` by `conda env exports > requirements.yml` and add the package) after using `pip` since conda won't track the package installed by pip and it can create a problem breaking from the `pip` with the `conda`. So anytime after using pip and want to install with conda, just recreate the env.

Working on Reserach Later I guess

### Notes:

- Setup the clustering on the face using mediapipe face detection
- Well, reference article it seems using Sentiment Analysis as the backup for the HRV.
- Do some Signal Frequency quality indicator with `signal.welch`
- Change the ROI around the under the eye
  - One should use the left under the eye as the ROI
  - and one should use both under the eye area as the ROI
- The concept of Facelandmarking can be working really well for detecting the area compare to faceDetector
