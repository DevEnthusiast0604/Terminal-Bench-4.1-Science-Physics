import sys
from concurrent.futures import ProcessPoolExecutor


def f(x):
    return x * x


if __name__ == "__main__":
    with ProcessPoolExecutor(int(sys.argv[1])) as ex:
        print(sum(ex.map(f, range(100), chunksize=2)))
