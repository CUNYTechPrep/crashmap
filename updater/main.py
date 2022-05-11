from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from functools import partial
import geopandas as gpd
from geopandas import GeoDataFrame
import lzma
import numpy as np
from os import getenv
import pandas as pd
from pandas import DataFrame, Series
from shapely.geometry.base import BaseGeometry
from smart_open import register_compressor, smart_open
from sqlalchemy import create_engine, sql
from sqlalchemy.engine import Engine
from toolz import compose_left as compose, first, get, juxt, last, pipe, valmap
from typing import Any, Callable, Optional, Sequence
from urllib.parse import urlencode

register_compressor('.xz', partial(lzma.LZMAFile, format=lzma.FORMAT_XZ))


series_to_postgresql_array_literal: Callable[[Series], str | float] = \
    compose(Series.dropna,
            partial(map, lambda value: value.replace('\'', '\'\'') if type(value) is str else value),
            partial(map, '\'{}\''.format),
            ', '.join,
            '{{{}}}'.format,
            lambda result: np.nan if result == '{}' else result)


def combine_columns(data_frame: DataFrame, source_columns: Sequence, aggregation_function: Callable[[Series], Any],
                    new_column_name: str) -> DataFrame:
    columns_to_aggregate = data_frame.get(source_columns)
    result = data_frame.assign(**{new_column_name: columns_to_aggregate.agg(aggregation_function, axis=1)})
    result = result.drop(columns=source_columns)
    return result


nyc_geometry_path = 'resources/nyc_area.gpkg.xz'
urls = {'collision': 'https://data.cityofnewyork.us/resource/h9gi-nx95.csv',
        'vehicle': 'https://data.cityofnewyork.us/resource/bm4k-52h4.csv',
        'person': 'https://data.cityofnewyork.us/resource/f55k-p6yu.csv'}
column_name_maps = {'collision': {'collision_id': 'id',
                                  'crash_date': 'date',
                                  'crash_time': 'time',
                                  'latitude': 'latitude',
                                  'longitude': 'longitude'},
                    'vehicle': {'unique_id': 'id',
                                'collision_id': 'collision_id',
                                'state_registration': 'state_registration',
                                'vehicle_type': 'type',
                                'vehicle_make': 'make',
                                'vehicle_model': 'model',
                                'vehicle_year': 'year',
                                'travel_direction': 'travel_direction',
                                'vehicle_occupants': 'occupants',
                                'driver_sex': 'driver_sex',
                                'driver_license_status': 'driver_license_status',
                                'driver_license_jurisdiction': 'driver_license_jurisdiction',
                                'pre_crash': 'pre_crash',
                                'point_of_impact': 'point_of_impact',
                                'vehicle_damage_1': 'damage_1',
                                'vehicle_damage_2': 'damage_2',
                                'vehicle_damage_3': 'damage_3',
                                'public_property_damage': 'public_property_damage',
                                'public_property_damage_type': 'public_property_damage_type',
                                'contributing_factor_1': 'contributing_factor_1',
                                'contributing_factor_2': 'contributing_factor_2'},
                    'person': {'unique_id': 'id',
                               'collision_id': 'collision_id',
                               'vehicle_id': 'vehicle_id',
                               'person_type': 'type',
                               'person_injury': 'injury',
                               'person_age': 'age',
                               'ejection': 'ejection',
                               'emotional_status': 'emotional_status',
                               'bodily_injury': 'bodily_injury',
                               'position_in_vehicle': 'position_in_vehicle',
                               'safety_equipment': 'safety_equipment',
                               'ped_location': 'location',
                               'ped_action': 'action',
                               'complaint': 'complaint',
                               'ped_role': 'role',
                               'contributing_factor_1': 'contributing_factor_1',
                               'contributing_factor_2': 'contributing_factor_2',
                               'person_sex': 'sex'}}
url_parameters = valmap(lambda column_name_map: {'$select': ','.join(column_name_map),
                                                 '$order': 'crash_date',
                                                 '$limit': '1000000'},
                        column_name_maps)


def get_nyc_geometry(uri: str) -> BaseGeometry:
    with smart_open(uri) as file:
        return gpd.read_file(file).iloc[0].iat[0]


def create_database_engine() -> Engine:
    db_uri = {component: getenv(f'DATABASE_{component}')
              for component in ('SCHEME', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'NAME')}
    return create_engine('{SCHEME}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{NAME}'.format(**db_uri))


def get_last_append_date(database_engine: Engine) -> Optional[date]:
    with database_engine.begin() as connection:
        return connection.execute('SELECT max(collision.date) FROM collision') \
                         .scalar_one_or_none()


def get_new_data(start_date: Optional[date], duration: Optional[relativedelta] = relativedelta(months=6, weeks=1)) \
        -> dict[str, DataFrame]:
    if start_date is None:
        start_date = date.today() - duration
    end_date = start_date + duration
    date_filter = {'$where': f'\'{start_date}\' <= crash_date and '
                             f'crash_date <= \'{end_date}\''}
    return {data_set: pipe('%s?%s' % (url, urlencode(url_parameters[data_set] | date_filter)),
                           partial(pd.read_csv, dtype='str'),
                           partial(DataFrame.rename, columns=column_name_maps[data_set]))
            for data_set, url in urls.items()}


def transform_data_sets(data_sets: dict[str, DataFrame], nyc_geometry: BaseGeometry) -> dict[str, DataFrame]:
    collision, vehicle, person = map(compose(partial(DataFrame.set_index, keys='id'), DataFrame.copy),
                                     get(['collision', 'vehicle', 'person'], data_sets))
    valid_locations = GeoDataFrame(collision, geometry=gpd.points_from_xy(collision.longitude, collision.latitude)) \
                     .within(nyc_geometry)
    collision.latitude = np.where(valid_locations, collision.latitude, np.nan)
    collision.longitude = np.where(valid_locations, collision.longitude, np.nan)
    collision = collision.drop(columns=['geometry'])
    vehicle = combine_columns(vehicle, ['damage_1', 'damage_2', 'damage_3'],
                              series_to_postgresql_array_literal, 'damages')
    vehicle = combine_columns(vehicle, ['contributing_factor_1', 'contributing_factor_2'],
                              series_to_postgresql_array_literal, 'contributing_factors')
    person = combine_columns(person, ['contributing_factor_1', 'contributing_factor_2'],
                             series_to_postgresql_array_literal, 'contributing_factors')
    person['dangling_vehicle_id'] = np.where(person.vehicle_id.isin(vehicle.index), np.nan, person.vehicle_id)
    person.vehicle_id = np.where(person.vehicle_id.isin(vehicle.index), person.vehicle_id, np.nan)
    return {'collision': collision, 'vehicle': vehicle, 'person': person}


def load_data(database_engine: Engine, data_set: dict[str, DataFrame]) -> None:
    start_date, end_date = juxt(first, last)(data_set['collision'].date)
    if start_date:
        with database_engine.begin() as connection:
            connection.execute(sql.text('DELETE FROM collision WHERE daterange(:from, :to, \'[]\') @> collision.date'),
                               {'from': start_date, 'to': end_date})
            for table_name, data_frame in data_set.items():
                data_frame.to_sql(table_name, connection, if_exists='append', method='multi')


def run() -> None:
    try:
        nyc_geometry = get_nyc_geometry(nyc_geometry_path)
        print(f'Loaded geometry from {nyc_geometry_path}.')
    except Exception as error:
        print(f'Failed to load geometry from {nyc_geometry_path}. {error}')
        return

    try:
        database_engine = create_database_engine()
        print('Created database engine.')
    except Exception as error:
        print(f'Failed to create database engine. {error}')
        return

    try:
        last_append_date = get_last_append_date(database_engine)
        print(f'Found latest data dated {last_append_date}.'
              if last_append_date
              else 'The collisions table is empty.')
        data_sets = get_new_data(last_append_date)
        print(f'{sum(map(len, data_sets.values())):,} row(s) retrieved from NYC OpenData.')
        transformed_data_sets = transform_data_sets(data_sets, nyc_geometry)
        print(f'Transformed {sum(map(len, transformed_data_sets.values())):,} row(s).')
        load_data(database_engine, transformed_data_sets)
        print(f'{len(transformed_data_sets):,} data set(s) have been successfully loaded into the database.')
    except Exception as error:
        print(f'An error occurred during the update process: {error}')
    finally:
        database_engine.dispose()
        print('Disposed database engine.')


if __name__ == '__main__':
    run()
