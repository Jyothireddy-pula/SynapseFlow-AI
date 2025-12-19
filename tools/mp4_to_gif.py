import sys, subprocess, os
def mp4_to_gif(infile, outfile):
    cmd = ['./tools/mp4_to_gif.sh', infile, outfile]
    subprocess.check_call(cmd)
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python mp4_to_gif.py input.mp4 output.gif')
    else:
        mp4_to_gif(sys.argv[1], sys.argv[2])
