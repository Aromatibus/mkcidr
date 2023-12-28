import sys
import time


def Memory_Usage_Comparison() -> None:
    d = 0
    n = 1234567890
    n_max = sys.maxsize
    f_max = sys.float_info.max
    is_64bits = sys.maxsize > 2**32
    c = "A"
    s = "ABCDEFGHIJ"
    print("Memory Usage Comparison")
    print("  1 digit     = {:>3} Bytes : {}".format(d.__sizeof__(), d))
    print("  Numeric     = {:>3} Bytes : {}".format(n.__sizeof__(), n))
    print("")
    print("  platform maxsize (is64bits : {} / architecture : {})".format(is_64bits, sys.platform))
    print("  int Max     = {:>3} Bytes : {}".format(n_max.__sizeof__(), n_max))
    print("  float Max   = {:>3} Bytes : {}".format(f_max.__sizeof__(), f_max))
    print("")
    print("  Character   = {:>3} Bytes : {}".format(c.__sizeof__(), c))
    print("  String      = {:>3} Bytes : {}".format(s.__sizeof__(), s))
    print("")

    l = list
    t = tuple
    array_digit = 5
    data = "A"
    print("List and Tuple Memory Usage Comparison (Data is '{}')".format(data))

    print("  array digits {}".format(len(())))
    print("    List     = {:>7,} Bytes".format([].__sizeof__()))
    print("    Tuple    = {:>7,} Bytes".format(().__sizeof__()))
    for i in range(0, array_digit):
        l = [data for x in range(0, pow(10, i))]
        t = tuple(l)
        print("  array digits {}".format(len((l))))
        print("    List     = {:>7,} Bytes".format(l.__sizeof__()))
        print("    Tuple    = {:>7,} Bytes".format(t.__sizeof__()))
    return


def list_append_time(MAX_RANGES: int = 100000) -> float:
    list_array = []
    start_time = time.time()
    for i in range(MAX_RANGES):
        list_array.append(i)
    end_time = time.time() - start_time
    return end_time


def list_append_object_time(MAX_RANGES: int = 100000) -> float:
    list_array = []
    start_time = time.time()
    list_array_append = list_array.append
    for i in range(MAX_RANGES):
        list_array_append(i)
    end_time = time.time() - start_time
    return end_time


def list_comprehensions_time(MAX_RANGES: int = 100000) -> float:
    list_array = []
    start_time = time.time()
    list_array = [x for x in range(1, MAX_RANGES)]
    end_time = time.time() - start_time
    return end_time


def tuple_append_time(MAX_RANGES: int = 100000) -> float:
    tuple_array = ()
    start_time = time.time()
    for i in range(MAX_RANGES):
        tuple_array += (i,)
    end_time = time.time() - start_time
    return end_time


def list_calculation_time(list_array: list) -> float:
    start_time = time.time()
    result = sum([x for x in list_array if x % 2 == 0])
    end_time = time.time() - start_time
    return end_time


def tuple_calculation_time(tuple_array: tuple) -> float:
    start_time = time.time()
    result = sum([x for x in tuple_array if x % 2 == 0])
    end_time = time.time() - start_time
    return end_time


if __name__ == "__main__":
    Memory_Usage_Comparison()
    print("")

    MAX_RANGES = 10000000
    TRIAL_COUNT = 5
    FUNCTIONS = [
        list_append_time,
        list_append_object_time,
        list_comprehensions_time,
        # tuple_append_time
    ]
    print("Measure the time it takes to add data to an array")
    print("Repeat {:,} tests {:,} times".format(MAX_RANGES, TRIAL_COUNT))

    for f in FUNCTIONS:
        print("")
        print("  {}".format(f.__name__))
        total_time = 0
        function = globals()[f.__name__]
        for i in range(TRIAL_COUNT):
            end_time = function(MAX_RANGES)
            total_time += end_time
            print(
                "    Test NO.{:>2} : time {:,.5f} sec".format(i + 1, end_time)
            )
        print(
            "    Average    : time {:,.5f} sec".format(
                total_time / TRIAL_COUNT
            )
        )

    print("")
    print("Sum only even numbers from the list and tuple arrays")
    list_array = []
    list_array = [x for x in range(1, MAX_RANGES)]

    print("")
    print("  List Calculations")
    total_time = 0
    for i in range(TRIAL_COUNT):
        end_time = list_calculation_time(list_array)
        total_time += end_time
        print("    Test NO.{:>2} : time {:,.5f} sec".format(i + 1, end_time))
    print("    Average    : time {:,.5f} sec".format(total_time / TRIAL_COUNT))

    tuple_array = tuple(list_array)

    print("")
    print("  Tuple Calculations")
    total_time = 0
    for i in range(TRIAL_COUNT):
        end_time = tuple_calculation_time(tuple_array)
        total_time += end_time
        print("    Test NO.{:>2} : time {:,.5f} sec".format(i + 1, end_time))
    print("    Average    : time {:,.5f} sec".format(total_time / TRIAL_COUNT))

    sys.exit(0)
