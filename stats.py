import json
import sys
from os import listdir
from os.path import isfile, join


def init_location(stats, location):
    stats["locations"][location] = {}
    stats["locations"][location]["items"] = {}
    stats["locations"][location]["play"] = 0
    stats["locations"][location]["nokeys"] = 0
    stats["locations"][location]["woth"] = 0


def init_item(stats, item):
    stats["items"][item] = {}
    stats["items"][item]["play"] = 0
    stats["items"][item]["woth"] = 0


def aggregate_stats(inputpath, outputpath):
    stats = {}
    stats["locations"] = {}
    stats["items"] = {}
    stats["barren"] = {}
    stats["number_analyzed"] = 0

    for filename in listdir(inputpath):
        filepath = join(inputpath, filename)
        if isfile(filepath):
            with open(filepath, 'r') as spoiler:
                data = json.load(spoiler)

                for location, item in data["locations"].items():
                    if location not in stats["locations"]:
                        init_location(stats, location)
                    if not isinstance(item, str):
                        item = item["item"]
                    if item not in stats["items"]:
                        init_item(stats, item)

                    if item not in stats["locations"][location]["items"]:
                        stats["locations"][location]["items"][item] = 1
                    else:
                        stats["locations"][location]["items"][item] += 1

                for location, item in data[":woth_locations"].items():
                    if location not in stats["locations"]:
                        init_location(stats, location)
                    if not isinstance(item, str):
                        item = item["item"]
                    if item not in stats["items"]:
                        init_item(stats, item)

                    # if item == "Farores Wind":
                    #    print(filename)

                    stats["locations"][location]["woth"] += 1
                    stats["items"][item]["woth"] += 1

                for sphere in data[":playthrough"].values():
                    for location, item in sphere.items():
                        if location not in stats["locations"]:
                            init_location(stats, location)
                        if not isinstance(item, str):
                            item = item["item"]
                        if item not in stats["items"]:
                            init_item(stats, item)

                        # if item == "Farores Wind":
                        #    print(filename)

                        if not "key" in item.lower():
                            stats["locations"][location]["nokeys"] += 1
                        stats["locations"][location]["play"] += 1
                        stats["items"][item]["play"] += 1

                for region in data[":barren_regions"]:
                    if region not in stats["barren"]:
                        stats["barren"][region] = 1
                    else:
                        stats["barren"][region] += 1

                stats["number_analyzed"] += 1

    with open(outputpath, 'w') as output:
        json.dump(stats, output, indent=4)

    return stats


def format_csv(stats, outputpath):
    with open(outputpath, 'w') as outputfile:

        line = ",,,Items:"
        for item in stats["items"]:
            line += ",%s" % item
        line += "\n"
        outputfile.write(line)

        line = ",,,Play%:"
        for item in stats["items"]:
            line += ",%s" % (stats["items"][item]
                             ["play"]/stats["number_analyzed"])
        line += "\n"
        outputfile.write(line)

        line = "Locations:,Play%:,NoKeys%:,WotH%:"
        for item in stats["items"]:
            line += ",%s" % (stats["items"][item]
                             ["woth"]/stats["number_analyzed"])
        line += "\n"
        outputfile.write(line)

        for location in stats["locations"]:
            line = "%s,%s,%s,%s" % (location,
                                    stats["locations"][location]["play"] /
                                    stats["number_analyzed"],
                                    stats["locations"][location]["nokeys"] /
                                    stats["number_analyzed"],
                                    stats["locations"][location]["woth"]/stats["number_analyzed"])
            for item in stats["items"]:
                item_at_location = stats["locations"][location]["items"].get(
                    item)
                if item_at_location is None:
                    line += ",%s" % 0
                else:
                    line += ",%s" % (item_at_location/stats["number_analyzed"])
            line += "\n"
            outputfile.write(line)


def main(argv):
    inputpath = argv[0]
    outputpath = argv[1]

    stats = aggregate_stats(inputpath, "%s.json" % outputpath)
    format_csv(stats, "%s.csv" % outputpath)


if __name__ == "__main__":
    main(sys.argv[1:])
