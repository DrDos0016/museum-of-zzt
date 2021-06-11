import glob
import os
import subprocess
import sys
import time


def main():
    print("=" * 78)
    now = int(time.time())
    cutoff = 90000 # 25 hours
    path = sys.argv[-1]

    success_count = 0
    successes = []
    fail_count = 0
    failures = []

    raw_files = glob.glob(path + "**/*.[Pp][Nn][Gg]")

    print("Image path:", path)
    print("Checking  :", len(raw_files), "files...")

    to_optimize = []

    for f in raw_files:
        mtime = int(os.stat(f).st_mtime)
        diff = now - mtime
        if diff < cutoff:
            to_optimize.append(f)

    print("Found     :", len(to_optimize), "file(s) to optimize.")
    print("Beginning optimization.")

    for f in to_optimize:
        res = subprocess.run(
            ["optipng", "-o7", "-strip=all", "-fix", "-nc", "-quiet", f]
        )
        if res.returncode == 0:
            success_count += 1
            successes.append(f)
        else:
            fail_count += 1
            failures.append(f)

    print("Completed optimizations.")
    print("Successes :", success_count)
    print("Failures  :", fail_count)

    if success_count:
        print("Optimized:")
        for f in successes:
            print("\t" + f)

    if fail_count:
        print("Failed on:")
        for f in failures:
            print("\t" + f)

    return True


if __name__ == "__main__":
    main()
