import logging
from rtree import index

logger = logging.getLogger(__name__)


class AutoTree(index.Index):
    """
    Spatial bounding box transforming (using pyproj) and indexing (using Rtree).
    """

    def __init__(self):
        super().__init__()
        self.objects = []
        self.counter = 0

    def auto_insert(self, facility):
        super().insert(self.counter, facility.geom.bounds)
        self.objects.append(facility)
        self.counter += 1

    def intersection(self, coordinates):
        ids = super().intersection(coordinates, objects=False)
        return [self.objects[i] for i in ids]

    def __iter__(self):
        for o in self.objects:
            yield(o)

    def __len__(self):
        return self.counter

    def __str__(self):
        print(list(self))


def dict_list_match(d, dict_list):
    """
    Check if simple key value pairs from dict d are in dictionary of lists.
    eg:
    dict_list_match({1:2}, {1:[1,2,3]}) == True
    dict_list_match({1:4}, {1:[1,2,3]}) == False
    dict_list_match({2:1}, {1:[1,2,3]}) == False
    """
    for k, v, in d.items():
        if v in dict_list.get(k, []):
            return True
    return False


def height_to_m(height):
    """
    Parse height to float in metres.
    """
    if height.isnumeric():
        return float(height)
    if "'" in height:
        return imperial_to_metric(height)
    logger.warning(f"Unable to convert height '{height} to metres, returning 'None'.")
    return None


def imperial_to_metric(height):
    """
    Convert imperial (feet and inches) to metric (metres).
    Expect formatted as 3'4" (3 feet and 4 inches) or 3' (3 feet).
    Return float
    """
    inches = float(height.split("'")[0].strip()) * 12
    if '"' in height:
        inches += float(height.split("'")[-1].replace('"',"").strip())
    return round(height/39.3701,3)


def progressBar(iterable, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    from here: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)
    # Progress Bar Printing Function
    def printProgressBar (iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()

def get_distance(p):
    """
    Return the distance between two shapely points
    Assumes orthogonal projection in meters
    :params tuple p: A tuple conctaining two Shapely points

    :return float: Distance in meters
    """
    distance = (
        (p[0].x - p[1].x)**2 +\
        (p[0].y - p[1].y)**2
    ) ** 0.5
    return distance