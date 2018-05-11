import time, os

models_dir_path = []

trainedmodel_base = "trainedmodel"
timeformat = "%Y-%m-%d_%H-%M"

def parse_timestamp(timestampformat = timeformat):
    return time.strptime(timeformat)


def model_timestamp(timespec=timeformat):
    if timespec is None:
        timespec == timeformat
    return time.strftime(timespec)

def model_name(directory=models_dir_path, basename=trainedmodel_base, timespec=timeformat, include_timestamp=True):
    timestring = model_timestamp(timespec)
    return os.sep.join(directory + [basename]) + include_timestamp * timestring



if __name__ == '__main__':
    print (model_name())
    

