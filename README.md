# ucsb-chess-processing

This repository contains a working version of the code used by the Wilson Lab at UCSB (adapted from Jacob P. C. Ruff at the Cornell High Energy Synchrotron Source), featuring a GUI for stacking and a GUI for orienting/indexing X-ray scattering data from the QM2 beamline at CHESS. 

To run the stacking GUI from the command line, use:
```
  > python tkinter_stack_frames.py
```

![image](https://github.com/user-attachments/assets/5f51336d-fa06-493a-8a99-a2f37d06fe36)


To run the orienting/indexing GUI from the command line, use:

```
  > python tkinter_chess_queue.py
```

![tkinter_chess_queue](app_screenshot.png)

A separate script is used to watch the queue stored in the job file for both stacking and orienting/indexing commands, which can be run using:

```
  > python start_queue.py
```

