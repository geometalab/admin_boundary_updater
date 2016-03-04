#!/usr/bin/env python

import fiona
import os
import codecs
import pyproj
import sys
import getopt
import json

import shapely.ops as ops
import time

from shapely.geometry import Polygon, MultiPolygon, shape, mapping
from functools import partial
from fiona.crs import from_epsg


class RegionPolygon:
    def __init__(self, name, geometry):
        self.name = name
        self.geometry = geometry

    def get_area_in_meters(self):
        geom_area = ops.transform(
            partial(
                pyproj.transform,
                pyproj.Proj(init='EPSG:4326'),
                pyproj.Proj(
                    proj='aea',
                    lat1=self.geometry.bounds[1],
                    lat2=self.geometry.bounds[3])),
            self.geometry)
        return geom_area.area

    def append(self, polygon):
        polygon_list = [polygon]
        for geom in self.geometry.geoms:
            polygon_list.append(geom)
        self.geometry = MultiPolygon(polygon_list)


def get_polygons_from_file(filename, name):
    polygons = []
    print "Importing  %s" % filename
    try:
        with fiona.open(_get_file(filename), 'r', encoding='utf-8') as fiona_polygons:
            for fiona_polygon in fiona_polygons:
                geometry = shape(Polygon(fiona_polygon['geometry']['coordinates'][0]))
                if is_only_one_with_name(polygons, fiona_polygon['properties'][name]):
                    multipolygon = MultiPolygon([geometry])
                    polygon = RegionPolygon(fiona_polygon['properties'][name], multipolygon)
                    polygons.append(polygon)
                else:
                    find_polygon(polygons, fiona_polygon['properties'][name]).append(geometry)
    except KeyError:
        print "Could not find a name under '%s' in %s" % (name, filename)
        sys.exit(2)
    except IOError:
        print "Could not find file: '%s'" % filename
        sys.exit(2)
    return polygons


def find_polygon(polygon_list, name):
    for region_polygon in polygon_list:
        if region_polygon.name == name:
            return region_polygon
    return None


def create_unique_list(old_polygons, new_polygons):
    unique_list = []
    for polygon in old_polygons:
        if is_only_one_with_name(new_polygons, polygon.name):
            unique_list.append(polygon)
    for polygon in new_polygons:
        if is_only_one_with_name(old_polygons, polygon.name):
            unique_list.append(polygon)
    return unique_list


def get_nullified_polygons(old_polygons, new_polygons):
    print "finding nullified communities"
    nullified_polygons = []
    for region_polygon in old_polygons:
        if is_only_one_with_name(new_polygons, region_polygon.name):
            nullified_polygons.append(region_polygon)
    return nullified_polygons


def get_new_polygons(old_polygons, new_polygons):
    print "finding new communities"
    new_polygons_list = []
    for region_polygon in new_polygons:
        if is_only_one_with_name(old_polygons, region_polygon.name):
            new_polygons_list.append(region_polygon)
    return new_polygons_list


def is_only_one_with_name(polygon_list, polygon_name):
    for single_region_polygon in polygon_list:
        if single_region_polygon.name == polygon_name:
            return False
    return True


def _get_file(filename):
    script_dir = os.path.dirname(os.path.dirname(__file__))
    a_file = filename
    return os.path.join(script_dir, a_file)


def has_size_difference(percentage, area_old, area_new):
    difference = abs(area_new - area_old)
    the_percentage = area_old / 100 * percentage
    if difference > the_percentage:
        return True
    else:
        return False


def get_resized_polygons(percentage, old_polygons, new_polygons):
    print "finding communities with area adjustments"
    resized_polygons = []
    for old_region_polygon in old_polygons:
        for new_region_polygon in new_polygons:
            if new_region_polygon.name is None or old_region_polygon.name is None:
                pass
            else:
                if old_region_polygon.name.lower() == new_region_polygon.name.lower():
                    if has_size_difference(percentage, old_region_polygon.get_area_in_meters(),
                                           new_region_polygon.get_area_in_meters()):
                        resized_polygons.append(old_region_polygon)
                else:
                    pass
    return resized_polygons


def append_to_file(output_file, title, polygons_list):
    output_file.write("\n\n\n")
    output_file.write(title + '\n')
    write_all_polygons_to_file(output_file, polygons_list)


def write_all_polygons_to_file(output_file, polygon_list):
    print len(polygon_list)
    for region_polygon in polygon_list:
        if region_polygon.name is not None:
            output_file.write(region_polygon.name + "\n")
        else:
            output_file.write("None\n")


def write_geometry_of_polygon(output_file, region_polygon):
    # Do not touch the Holy Grail
    with fiona.open(_get_file('src/test.json'), 'r') as holy_grail:
          pass

    schema = {'geometry': 'Polygon', 'properties': fiona.OrderedDict([(u'name', 'str')])}
    with fiona.open(_get_file(output_file), 'w', 'GeoJSON', schema) as fiona_file:
        print 'foo'
        fiona_file.write({
            'geometry': mapping(region_polygon[0].geometry),
            'properties': {'name': region_polygon[0].name}
        })
    fiona_file.close()


def main(argv):
    input_file1 = ''
    input_file2 = ''
    name_attribute1 = ''
    name_attribute2 = ''
    output_filename = ''
    percentage = 5.0
    try:
        opts, args = getopt.getopt(argv, "hi:j:n:m:o:p:",
                                   ["ifile=", "ifile2=", "name1=", "name2=", "ofile=", "percentage="])
    except getopt.GetoptError:
        print 'main.py -i <input_file1> -j <input_file2> -n <name_attribute1> -m <name_attribute2> -o ' \
              '<output_file> -p <percentage>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h'or opt == '--help':
            print 'main.py -i <input_file1> -j <input_file2> -n <name_attribute_of_file1> -m <name_attribute_of_file2>'\
                  ' -o <output_file> -p <percentage>'
            print "additional info can be found in the readme.txt file."
            sys.exit(2)
        elif opt in ("-i", "--ifile1"):
            input_file1 = arg
        elif opt in ("-j", "--ifile2"):
            input_file2 = arg
        elif opt in ("-n", "--name1"):
            name_attribute1 = arg
        elif opt in ("-m", "--name2"):
            name_attribute2 = arg
        elif opt in ("-o", "--ofile"):
            output_filename = arg
        elif opt in ("-p", "--percentage"):
            try:
                percentage = float(arg)
            except ValueError:
                print "'%s' is not a number" % arg
                sys.exit(2)

    new_polygons = get_polygons_from_file(input_file1, name_attribute1)
    old_polygons = get_polygons_from_file(input_file2, name_attribute2)

    old_polygons.sort(key=lambda x: x.name)
    new_polygons.sort(key=lambda x: x.name)

    new_polygons_list = get_new_polygons(old_polygons, new_polygons)
    nullified_polygons_list = get_nullified_polygons(old_polygons, new_polygons)
    resized_polygons_list = get_resized_polygons(percentage, old_polygons, new_polygons)

    output_file = codecs.open(output_filename, "w", "utf-8")
    output_file.write("Results from comparing %s and %s\n" % (input_file1, input_file2))
    append_to_file(output_file, "Nullified Polygons", nullified_polygons_list)
    append_to_file(output_file, "New Polygons", new_polygons_list)
    append_to_file(output_file, "Resized Polygons", resized_polygons_list)
    output_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
