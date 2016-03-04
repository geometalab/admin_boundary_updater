#!/usr/bin/env python
# -​*- coding: utf-8 -*​-

import pytest
import main


@pytest.fixture()
def eosm():
    return main.get_polygons_from_file('test/eosmMock.json', 'name')


@pytest.fixture()
def sbound():
    return main.get_polygons_from_file('test/sBoundMock.json', 'NAME')


@pytest.fixture()
def sbound_original():
    return main.get_polygons_from_file('src/swissBOUNDARIES3D.json', 'NAME')


@pytest.fixture()
def eosm_original():
    return main.get_polygons_from_file('src/EOSMDBOne2.json', 'name')


@pytest.fixture()
def illnau_eosm():
    return main.get_polygons_from_file('src/illnauEosm.json', 'name')


@pytest.fixture()
def illnau_sbound():
    return main.get_polygons_from_file('src/illnauSbound.json', 'NAME')


def test_file_to_polygon_illnau(illnau_eosm, illnau_sbound):
    assert illnau_eosm[0].get_area_in_meters() == 32906992.342055503
    assert illnau_sbound[0].get_area_in_meters() == 25283822.266234234


def test_write_polygon_on_file(illnau_sbound):
    main.write_geometry_of_polygon('test/out.json', illnau_sbound)


def test_file_to_polygon_eosm(eosm):
    assert eosm[0].name == "Binn"
    assert eosm[0].get_area_in_meters() == 65034397.371016964


def test_file_to_polygon_sbound(sbound):
    assert sbound[0].name == u"Glarus Süd"
    assert sbound[0].get_area_in_meters() == 430129923.9961412


def test_create_unique_list(eosm, sbound):
    singleton_list = main.create_unique_list(eosm, sbound)
    assert len(singleton_list) == 2


def test_get_new_polygons(eosm, sbound):
    new_polygons = main.get_new_polygons(eosm, sbound)
    assert len(new_polygons) == 2


def test_get_old_polygons(eosm, sbound):
    new_polygons = main.get_nullified_polygons(eosm, sbound)
    assert len(new_polygons) == 0


def test_is_singleton(eosm):
    assert main.is_only_one_with_name(eosm, "Binn") == False
    assert main.is_only_one_with_name(eosm, "Weisslingen") == True
    assert main.is_only_one_with_name(eosm, u"Glarus Süd") == True


def test_has_size_difference():
    assert main.has_size_difference(0, 15, 15) is False
    assert main.has_size_difference(1, 100.0, 99.5) is False
    assert main.has_size_difference(1, 99.5, 100.0) is False
    assert main.has_size_difference(0, 40.4, 12.6) is True
    assert main.has_size_difference(0, 12.6, 40.4) is True


def test_get_resized_polygons(eosm, sbound):
    resized_polygons = main.get_resized_polygons(0, eosm, sbound)
    len(resized_polygons) == 1