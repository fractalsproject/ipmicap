#!/bin/bash

export PATH="/usr/local/cuda-10.2/targets/x86_64-linux/lib:$PATH"
export PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:$PATH"
export PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib/stubs/:$PATH"

export LD_LIBRARY_PATH="/usr/local/cuda-10.2/targets/x86_64-linux/lib:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib:$PATH"
export LD_LIBRARY_PATH="/usr/local/cuda-10.1/targets/x86_64-linux/lib/stubs/:$PATH"

#./gpu_burn --help
cd /home/george/Projects/ipmi/GPUBURN/wilicc/gpu-burn/; ./gpu_burn $1

