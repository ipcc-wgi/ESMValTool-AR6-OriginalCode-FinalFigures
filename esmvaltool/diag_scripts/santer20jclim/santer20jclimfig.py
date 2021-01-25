#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Plot based on Santer et al. (2020).

###############################################################################
santer20jclim/santer20jclimfig.py
Author: Katja Weigel (IUP, Uni Bremen, Germany)
EVal4CMIP ans 4C project
###############################################################################

Description
-----------
    Total column water vapour trends following Santer et al. (2020).

Configuration options
---------------------
filer: optional, filter all data sets (netCDF file with 0 and 1 for used grid).
       The data must be interpolated to the same lat/lon grid as the filter.
       The filter must cover at least the time period used for the data.

###############################################################################

"""

import logging
import os
from collections import OrderedDict
from pprint import pformat
from cf_units import Unit
import iris
import iris.coord_categorisation as cat
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
# from scipy.stats import norm
from esmvaltool.diag_scripts.shared import (ProvenanceLogger,
                                            plot, get_diagnostic_filename,
                                            get_plot_filename,
                                            group_metadata,
                                            select_metadata, run_diagnostic,
                                            variables_available)

logger = logging.getLogger(os.path.basename(__file__))


def _apply_filter(cfg, cube):
    """Apply filter from RSS Anomalies to all data and calculates mean."""
    if 'filter' in cfg:
        filt = iris.load(cfg['filter'])[0]

        for iii, dim_str in ['time', 'latitude', 'longitude']:
            filt = _fit_dim(filt, cube, dim_str, iii)

        cube.data = cube.data * filt.data

    coords = ('longitude', 'latitude')
    cube_grid_areas = iris.analysis.cartography.area_weights(cube)
    cube = (cube.collapsed(coords, iris.analysis.MEAN,
                           weights=cube_grid_areas))

    return cube


def _fit_dim(filt, cube, dim_str, dim_nr):
    """Adjust array for given dimension."""
    dimfil = filt.coord(dim_str)
    dimcu = cube.coord(dim_str)
    if dim_str == 'time':
        start = dimcu.units.num2date(dimcu.points[0])
        end = dimcu.units.num2date(dimcu.points[-1])
        sdim = dimfil.nearest_neighbour_index(dimfil.units.date2num(start))
        edim = dimfil.nearest_neighbour_index(dimfil.units.date2num(end))
    else:
        start = dimcu.points[0]
        end = dimcu.points[-1]
        sdim = dimfil.nearest_neighbour_index(start)
        edim = dimfil.nearest_neighbour_index(end)

    if dim_nr == 0:
        filt = filt[sdim:edim + 1, :, :]
    elif dim_nr == 1:
        filt = filt[:, sdim:edim + 1, :]
    elif dim_nr == 2:
        filt = filt[:, :, sdim:edim + 1]

    return filt


def _calc_trend(cube_anom):
    """Calculate trends."""
    reg_var = stats.linregress(np.linspace(0, len(cube_anom.data) - 1,
                                           len(cube_anom.data)),
                               cube_anom.data)

    return reg_var.slope


def _calculate_anomalies(cube):
    """Remove annual cycle from time series."""
    c_n = cube.aggregated_by('month_number', iris.analysis.MEAN)
    month_number = cube.coord('month_number').points
    startind = np.where(month_number == 1)
    endind = np.where(month_number == 12)
    data_in = cube.data
    data_new = np.full(data_in.shape, 0.5)
    for iii in range((startind[0])[0], (endind[0])[-1], 12):
        data_new[iii:iii + 12] = ((cube.data[iii:iii + 12] - c_n.data) /
                                  c_n.data) * 100.0 * 120.0

    cube.data = data_new
    cube.units = Unit('percent')

    return cube


def _check_full_data(dataset_path, cube):
    """Check if cube covers time series from start year to end year."""
    # cstart_month = cube.coord('month_number').points[0]
    # cend_month = cube.coord('month_number').points[1]
    cstart_year = cube.coord('year').points[0]
    cend_year = cube.coord('year').points[-1]
    start_year = int(dataset_path['start_year'])
    end_year = int(dataset_path['end_year'])

    check = 0
    if start_year == cstart_year and end_year == cend_year:
        check = 1
        print("Full time series:")
        print(start_year, cstart_year, end_year, cend_year)
    else:
        print("FAILED:")
        print(start_year, cstart_year, end_year, cend_year)

    return check


def _plot_extratrends(cfg, extratrends, trends):
    """Plot trends for ensembles."""
    xhist = np.linspace(0, 4, 41)
    artrend = {}
    kde1 = {}
    fig, axx = plt.subplots(figsize=(8, 6))

    valid_datasets = []
    
    for extramodel in cfg['add_model_dist']:
        alias = list(extratrends[extramodel].keys())[0]
        valid_datasets.append(select_metadata(cfg['input_data'].values(),
                                              alias=alias)[0]['filename'])
        if alias in trends['cmip6'].keys():
            style = plot.get_dataset_style(extramodel, style_file='cmip6')
        elif alias in trends['cmip5'].keys():
            style = plot.get_dataset_style(extramodel, style_file='cmip5')
        else:
            style = {'facecolor': (0, 0, 1, 0.1), 'color': (0, 0, 1, 1.0)}

        artrend[extramodel] = np.fromiter(extratrends[extramodel].values(),
                                          dtype=float)
        kde1[extramodel] = stats.gaussian_kde(artrend[extramodel],
                                              bw_method="scott")
        axx.hist(artrend[extramodel], bins=xhist, density=True,
                 edgecolor=style['color'],
                 facecolor=style['facecolor'])
        axx.plot(xhist, kde1[extramodel](xhist),
                 color=style['color'],
                 linewidth=3,
                 label=extramodel)

    obs_str = _plot_obs(trends, axx, 2.5)
    _plot_settings(cfg, axx, fig, 'fig2')
    plt.close()

    caption = 'Probability density function of the decadal trend in ' + \
        'the Water Vapor Path.' + obs_str

    provenance_record = get_provenance_record(valid_datasets,
                                              caption, ['trend', 'other'],
                                              ['reg'])

    diagnostic_file = get_diagnostic_filename('fig2', cfg)

    logger.info("Saving analysis results to %s", diagnostic_file)

    list_dict = _write_list_dict(cfg, trends, xhist, artrend, kde1)

    iris.save(cube_to_save_vars(list_dict), target=diagnostic_file)

    logger.info("Recording provenance of %s:\n%s", diagnostic_file,
                pformat(provenance_record))
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(diagnostic_file, provenance_record)


def _plot_obs(trends, axx, maxh):
    """Plot observational or reanalysis data as vertical line."""
    obs_str = ''
    if trends['obs']:
        obs_str = ' Vertical lines show the trend for'
        for iii, obsname in enumerate(trends['obs'].keys()):
            obscoli = float(iii)
            if iii > 4:
                obscoli = float(iii) - 4.5
            if iii > 8:
                obscoli = float(iii) - 8.75
            if iii > 12:
                obscoli = float(iii) - 12.25
            axx.vlines(trends['obs'][obsname], 0, maxh,
                       colors=(1.0 - 0.25 * obscoli, 0.25 * obscoli,
                               0.5 + obscoli * 0.1),
                       linewidth=3,
                       label=obsname)
        obs_str = obs_str + '.'
    return obs_str


def _plot_trends(cfg, trends, valid_datasets):
    """Plot probability density function of trends."""
    xhist = np.linspace(0, 4, 41)
    fig, axx = plt.subplots(figsize=(8, 6))

    # CMIP5
    if trends['cmip5']:
        artrend_c5 = np.fromiter(trends['cmip5'].values(), dtype=float)
        weights_c5 = np.fromiter(trends['cmip5weights'].values(), dtype=float)
        # yyy_c5, xxx_c5 = np.histogram(artrend_c5, bins=xhist)
        kde1_c5 = stats.gaussian_kde(artrend_c5, weights=weights_c5,
                                     bw_method="scott")
        axx.hist(artrend_c5, bins=xhist, density=True,
                 weights=weights_c5,
                 edgecolor=(0, 0, 1, 0.6),
                 facecolor=(0, 0, 1, 0.1))
        axx.plot(xhist, kde1_c5(xhist),
                 color=(0, 0, 1, 1),
                 linewidth=3,
                 label="CMIP5")
        # maxh = np.max(kde1_c5(xhist))

    # CMIP6
    if trends['cmip6']:
        artrend_c6 = np.fromiter(trends['cmip6'].values(), dtype=float)
        weights_c6 = np.fromiter(trends['cmip6weights'].values(), dtype=float)
        # yyy_c6, xxx_c6 = np.histogram(artrend_c6, bins=xhist)
        kde1_c6 = stats.gaussian_kde(artrend_c6, weights=weights_c6,
                                     bw_method="scott")
        axx.hist(artrend_c6, bins=xhist, density=True,
                 weights=weights_c6,
                 edgecolor=(0.8, 0.4, 0.1, 0.6),
                 facecolor=(0.8, 0.4, 0.1, 0.1))
        axx.plot(xhist, kde1_c6(xhist),
                 color=(0.8, 0.4, 0.1, 1),
                 linewidth=3,
                 label="CMIP6")
        # maxh = np.max(kde1_c6(xhist))
    obs_str = _plot_obs(trends, axx, 2.5)
    _plot_settings(cfg, axx, fig, 'fig1')
    plt.close()

    caption = 'Probability density function of the decadal trend in ' + \
        'the Water Vapor Path.' + obs_str

    provenance_record = get_provenance_record(valid_datasets,
                                              caption, ['trend', 'other'],
                                              ['reg'])

    diagnostic_file = get_diagnostic_filename('fig1', cfg)

    logger.info("Saving analysis results to %s", diagnostic_file)

    list_dict = {}
    list_dict["data"] = [xhist]
    list_dict["name"] = [{'var_name': 'prw_trends_bins',
                          'long_name': 'Water Vapor Path Trend bins',
                          'units': 'percent'}]
    if trends['cmip5']:
        list_dict["data"].append(artrend_c5)
        list_dict["name"].append({'var_name': 'prw_trends_cmip5',
                                  'long_name': 'Water Vapor Path Trends CMIP5',
                                  'units': 'percent'})
        list_dict["data"].append(weights_c5)
        list_dict["name"].append({'var_name': 'data_set_weights',
                                  'long_name': 'Weights for each data set.',
                                  'units': '1'})
        list_dict["data"].append(kde1_c5(xhist))
        list_dict["name"].append({'var_name': 'prw_trend_distribution_cmip5',
                                  'long_name': 'Water Vapor Path Trends ' +
                                               'distribution CMIP5',
                                  'units': '1'})
    if trends['cmip6']:
        list_dict["data"].append(artrend_c6)
        list_dict["name"].append({'var_name': 'prw_trends_cmip6',
                                  'long_name': 'Water Vapor Path Trends CMIP6',
                                  'units': 'percent'})
        list_dict["data"].append(weights_c6)
        list_dict["name"].append({'var_name': 'data_set_weights',
                                  'long_name': 'Weights for each data set.',
                                  'units': '1'})
        list_dict["data"].append(kde1_c6(xhist))
        list_dict["name"].append({'var_name': 'prw_trend_distribution_cmip6',
                                  'long_name': 'Water Vapor Path Trends ' +
                                               'distribution CMIP6',
                                  'units': '1'})

    if trends['obs']:
        for obsname in trends['obs'].keys():
            list_dict["data"].append(trends['obs'][obsname])
            list_dict["name"].append({'var_name': 'prw_trend_' + obsname,
                                      'long_name': 'Water Vapor Path Trend ' +
                                                   obsname,
                                      'units': 'percent'})

    iris.save(cube_to_save_vars(list_dict), target=diagnostic_file)

    logger.info("Recording provenance of %s:\n%s", diagnostic_file,
                pformat(provenance_record))
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(diagnostic_file, provenance_record)


def _plot_settings(cfg, axx, fig, figname):
    """Define Settings for pdf figures."""
    axx.legend(loc=0)
    axx.set_ylim([0, 2.5])
    axx.set_ylabel('Probability density')
    axx.set_xlabel('Trend in Water Vapor Path [%/dec]')
    fig.tight_layout()
    fig.savefig(get_plot_filename(figname, cfg), dpi=300)


def _write_list_dict(cfg, trends, xhist, artrend, kde1):
    """Collect data for provenance."""
    list_dict = {}
    list_dict["data"] = [xhist]
    list_dict["name"] = [{'var_name': 'prw_trends_bins',
                          'long_name': 'Water Vapor Path Trend bins',
                          'units': 'percent'}]

    for extramodel in cfg['add_model_dist']:
        list_dict["data"].append(artrend[extramodel])
        list_dict["name"].append({'var_name': 'prw_trends_' + extramodel,
                                  'long_name': 'Water Vapor Path Trends ' +
                                               extramodel,
                                  'units': 'percent'})
        list_dict["data"].append(kde1[extramodel](xhist))
        list_dict["name"].append({'var_name': 'prw_trend_distribution_' +
                                              extramodel,
                                  'long_name': 'Water Vapor Path Trends ' +
                                               'distribution ' + extramodel,
                                  'units': '1'})

    if trends['obs']:
        for obsname in trends['obs'].keys():
            list_dict["data"].append(trends['obs'][obsname])
            list_dict["name"].append({'var_name': 'prw_trend_' + obsname,
                                      'long_name': 'Water Vapor Path Trend ' +
                                                   obsname,
                                      'units': 'percent'})
    return list_dict


def cube_to_save_vars(list_dict):
    """Create cubes to prepare bar plot data for saving to netCDF."""
    # cubes = iris.cube.CubeList()
    for iii, var in enumerate(list_dict["data"]):
        if iii == 0:
            cubes = iris.cube.CubeList([
                iris.cube.Cube(var,
                               var_name=list_dict["name"][iii]['var_name'],
                               long_name=list_dict["name"][iii]['long_name'],
                               units=list_dict["name"][iii]['units'])])
        else:
            cubes.append(
                iris.cube.Cube(var,
                               var_name=list_dict["name"][iii]['var_name'],
                               long_name=list_dict["name"][iii]['long_name'],
                               units=list_dict["name"][iii]['units']))

    return cubes


def get_provenance_record(ancestor_files, caption, statistics,
                          domains, plot_type='probability'):
    """Get Provenance record."""
    record = {
        'caption': caption,
        'statistics': statistics,
        'domains': domains,
        'plot_type': plot_type,
        'realms': ['atmos'],
        'themes': ['atmDyn'],
        'authors': [
            'weigel_katja',
        ],
        'references': [
            'santer20jclim',
        ],
        'ancestors': ancestor_files,
    }
    return record


###############################################################################
# Setup diagnostic
###############################################################################


def main(cfg):
    """Run the diagnostic."""
    ###########################################################################
    # Read recipe data
    ###########################################################################

    # Dataset data containers
    input_data = (cfg['input_data'].values())

    if not variables_available(cfg, ['prw']):
        logger.warning("This diagnostic was written and tested only for prw.")

    ###########################################################################
    # Read data
    ###########################################################################

    # Create iris cube for each dataset and save annual means
    trends = {}
    trends['cmip5'] = OrderedDict()
    trends['cmip6'] = OrderedDict()
    trends['cmip5weights'] = OrderedDict()
    trends['cmip6weights'] = OrderedDict()
    trends['obs'] = {}
    f_c5 = open(cfg['work_dir'] + "/cmip5_trends.txt", "a")
    f_c5.write("Model Alias Trend Weight Mean Median " +
               "Maximum Mnimum Standard deviation \n")
    f_c6 = open(cfg['work_dir'] + "/cmip6_trends.txt", "a")
    f_c6.write("Model Alias Trend Weight Mean Median " +
               "Maximum Mnimum Standard deviation \n")

    if 'add_model_dist' in cfg:
        extratrends = {}
        for extramodel in cfg['add_model_dist']:
            # wstr = extramodel + 'weights'
            extratrends[extramodel] = OrderedDict()
            # extratrends[wstr] = OrderedDict()

    number_of_subdata = OrderedDict()
    available_dataset = list(group_metadata(input_data, 'dataset'))
    valid_datasets = []
    for dataset in available_dataset:
        meta = select_metadata(input_data, dataset=dataset)
        number_of_subdata[dataset] = float(len(meta))
        for dataset_path in meta:
            cube = iris.load(dataset_path['filename'])[0]
            cat.add_year(cube, 'time', name='year')
            if not _check_full_data(dataset_path, cube):
                number_of_subdata[dataset] = number_of_subdata[dataset] - 1
            else:
                valid_datasets.append(dataset_path['filename'])

    for dataset_path in input_data:
        project = dataset_path['project']
        cube_load = iris.load(dataset_path['filename'])[0]
        cube = _apply_filter(cfg, cube_load)
        cat.add_month_number(cube, 'time', name='month_number')
        cat.add_year(cube, 'time', name='year')
        alias = dataset_path['alias']
        dataset = dataset_path['dataset']
        # selection = select_metadata(input_data, dataset=dataset)
        # number_of_subdata = float(len(select_metadata(input_data,
        #                                               dataset=dataset)))
        if not _check_full_data(dataset_path, cube):
            continue
        cube_anom = _calculate_anomalies(cube)

        if project == 'CMIP6':
            trend = _calc_trend(cube_anom)
            trends['cmip6'][alias] = trend
            trends['cmip6weights'][alias] = 1. / number_of_subdata[dataset]
            print(dataset, alias, trend, 1. / number_of_subdata[dataset])
            f_c6.write(dataset + ' ' +
                       alias + ' ' +
                       str(round(trend, 4)) + ' ' +
                       str(round(1. / number_of_subdata[dataset], 4)) + ' ' +
                       str(round(np.mean(cube_anom.data), 4)) + ' ' +
                       str(round(np.median(cube_anom.data), 4)) + ' ' +
                       str(round(np.max(cube_anom.data), 4)) + ' ' +
                       str(round(np.min(cube_anom.data), 4)) + ' ' +
                       str(round(np.std(cube_anom.data), 4)) + '\n')
        elif project == 'CMIP5':
            trend = _calc_trend(cube_anom)
            trends['cmip5'][alias] = trend
            trends['cmip5weights'][alias] = 1. / number_of_subdata[dataset]
            f_c5.write(dataset + ' ' +
                       alias + ' ' +
                       str(round(trend, 4)) + ' ' +
                       str(round(1. / number_of_subdata[dataset], 4)) + ' ' +
                       str(round(np.mean(cube_anom.data), 4)) + ' ' +
                       str(round(np.median(cube_anom.data), 4)) + ' ' +
                       str(round(np.max(cube_anom.data), 4)) + ' ' +
                       str(round(np.min(cube_anom.data), 4)) + ' ' +
                       str(round(np.std(cube_anom.data), 4)) + '\n')
        else:
            trend = _calc_trend(cube_anom)
            trends['obs'][dataset] = trend

        if 'add_model_dist' in cfg:
            if dataset in cfg['add_model_dist']:
                # wstr = dataset + 'weights'
                extratrends[dataset][alias] = trend
                # extratrends[wstr][alias] = 1./float(len(selection))

    f_c5.close()
    f_c6.close()
    _plot_trends(cfg, trends, valid_datasets)
    if 'add_model_dist' in cfg:
        if extratrends:
            _plot_extratrends(cfg, extratrends, trends)

    ###########################################################################
    # Process data
    ###########################################################################


if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
