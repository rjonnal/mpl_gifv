# mpl_gifv

## Make a movie out of matplotlib plots (requires ImageMagick)

## Preliminaries

1. Install [ImageMagick](https://www.imagemagick.org). In Debian/Ubuntu run `apt-get install imagemagick`. For other distros and OSs, see [ImageMagick installation instructions](https://www.imagemagick.org/script/binary-releases.php).

2. To run test.py verify installation of [numpy](http://numpy.org) and [matplotlib](http://matplotlib.org).

3. Put the mpl_gifv folder somewhere in your pythonpath.

## The basic idea:

1. Create a GIF object.

2. Add frames to it by passing matplotlib figure handles to its add function.

3. Call its make function.

## Parameters of `GIF` constructor:

1. Required: `gif_filename`, the output filename.

2. Optional: `fps`, frames per second. Default 30.

3. Optional: `dpi`, dots per inch. Default 100.

4. Optional: `loop`, number of times to loop. Default 0 (loop forever).

## Example

```python
from matplotlib import pyplot as plt
import numpy as np

f = plt.figure()

mov = GIF('example.gif',fps=10,loop=0,dpi=100)

for k in range(10):
    plt.cla()
    plt.imshow(np.random.rand(100,100))
    plt.pause(.000001)
    mov.add(f)

mov.make()
```

