from subprocess import DEVNULL, STDOUT, check_call

to_launch = ["Q6256", "Q82955", "Q215380"]

for folder in to_launch:

    cmd = f"python3 ./2.4.TestETGT.py {folder}"
    check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

