"""
AMOC timeseries diagnostics.
=========================

Diagnostic to produce figure of the timeseries over time from a cube.
These plost show cube value (ie temperature) on the x-axis, and depth/height
on the y axis. The colour scale is the time series.

Note that this diagnostic assumes that the preprocessors do the bulk of the
hard work, and that the cube received by this diagnostic (via the settings.yml
and metadata.yml files) has a time component, and depth component, but no
latitude or longitude coordinates.

An approproate preprocessor for a 3D+time field would be::

  preprocessors:
    prep_timeseries:
      extract_volume:
        long1: 0.
        long2:  20.
        lat1:  -30.
        lat2:  30.
        z_min: 0.
        z_max: 3000.
      average_region:
        coord1: longitude
        coord2: latitude

In order to add an observational dataset to the timeseries plot, the following
arguments are needed in the diagnostic script::

  diagnostics:
    diagnostic_name:
      variables:
        ...
      additional_datasets:
      - {observational dataset description}
      scripts:
        script_name:
          script: ocean/diagnostic_timeseriess.py
          observational_dataset: {observational dataset description}

This tool is part of the ocean diagnostic tools package in the ESMValTool.

Author: Lee de Mora (PML)
        ledm@pml.ac.uk
"""
import logging
import os
import sys

import numpy as np
import iris
import iris.quickplot as qplt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy.stats import linregress


from esmvaltool.diag_scripts.ocean import diagnostic_tools as diagtools
from esmvaltool.diag_scripts.shared import run_diagnostic
from esmvalcore.preprocessor import climate_statistics
# This part sends debug statements to stdout
logger = logging.getLogger(os.path.basename(__file__))
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def calculate_trend(cube, window = '8 years', tails=False, intersect_wanted=False):
    """
    Calculate a trend inside a window.

    The window is a string which is a number and a measuremet of time.
    For instance, the following are acceptable window strings:

    * ``5 days``
    * ``12 years``
    * ``1 month``
    * ``5 yr``

    Also note the the value used is the total width of the window.
    For instance, if the window provided was '10 years', the the moving
    average returned would be the average of all values within 5 years
    of the central value.

    When tails is True, the start and end of the data, they
    only include the average of the data available. Ie the first value
    in the moving average of a ``10 year`` window will only include the average
    of the five subsequent years.
    When tails is False, these tails are ignored.

    Parameters
    ----------
    cube: iris.cube.Cube
        Input cube
    window: str
        A description of the window to use for the
    tails: bool
        Boolean flag to switch off tails.

    Returns
    ----------
    iris.cube.Cube:
        A cube with the movinage average set as the data points.

    """
    assert 0
    window = window.split()
    window_len = int(window[0]) / 2.
    win_units = str(window[1])

    if win_units not in [
            'days', 'day', 'dy', 'months', 'month', 'mn', 'years', 'yrs',
            'year', 'yr'
    ]:
        raise ValueError("Moving average window units not recognised: " +
                         "{}".format(win_units))

    times = cube.coord('time').units.num2date(cube.coord('time').points)
    float_times = diagtools.cube_time_to_float(cube)

    datetime = diagtools.guess_calendar_datetime(cube)

    slopes = []
    intercepts = []

    times = np.array([
        datetime(time_itr.year, time_itr.month, time_itr.day, time_itr.hour,
                 time_itr.minute) for time_itr in times
    ])
        # amoc_anave is the annual average
        # amoc_interan=(amoc_anave(2:end)-amoc_anave(1:end-1));
        #
        # % now calculate the trend
        # xx=(1:8);
        # x=[xx*0+1;xx];
        # for i=1:length(time2)-7
        # b=regress(amoc_anave(i:i+7)',x');
        # amoc_trend_slope(i)=b(2);
        # end

    for time_itr in times:
        if win_units in ['years', 'yrs', 'year', 'yr']:
            tmin = datetime(time_itr.year - window_len, time_itr.month,
                            time_itr.day, time_itr.hour, time_itr.minute)
            tmax = datetime(time_itr.year + window_len, time_itr.month,
                            time_itr.day, time_itr.hour, time_itr.minute)

        if win_units in ['months', 'month', 'mn']:
            tmin = datetime(time_itr.year, time_itr.month - window_len,
                            time_itr.day, time_itr.hour, time_itr.minute)
            tmax = datetime(time_itr.year, time_itr.month + window_len,
                            time_itr.day, time_itr.hour, time_itr.minute)

        if win_units in ['days', 'day', 'dy']:
            tmin = datetime(time_itr.year, time_itr.month,
                            time_itr.day - window_len, time_itr.hour,
                            time_itr.minute)
            tmax = datetime(time_itr.year, time_itr.month,
                            time_itr.day + window_len, time_itr.hour,
                            time_itr.minute)

        arr = np.ma.masked_where((times < tmin) + (times > tmax), cube.data)
        print (time_itr, len(arr))

        # No Tails
        if not tails:
            print(time_itr, [tmin, tmax], 'Length:', len(arr.compressed()), len(times), window_len*2 + 1)
            if len(arr.compressed()) != window_len*2 + 1:
                print("Wrong size")
                continue

#        print(time_itr, len(arr), len(times), window_len*2 + 1)
        time_arr = np.ma.masked_where(arr.mask, float_times)
        #if debug:
        #    print(time_itr, times, time_arr.compressed(),  arr.compressed())

        # print(time_itr, linregress(time_arr.compressed(), arr.compressed()))
        lnregs = linregress(time_arr.compressed(), arr.compressed())
        slopes.append(lnregs[0])
        intercepts.append(lnregs[1])
        #print(slopes)
    if intersect_wanted:
        return np.array(slopes), np.array(intercepts)
    else:
        return np.array(slopes)


def calculate_interannual(cube,):
    """
    Calculate the interannnual variability.
    """
    #if time_res == 'annual':
    #        cube = cube.aggregated_by('year', iris.analysis.MEAN)

    data = cube.data
    return np.array(data[1:] - data[:-1])


def calculate_midpoint(arr,):
    """
    Calculate the midpoint - usually for time axis
    """
    arr = np.ma.array(arr)
    return np.array(arr[1:] + arr[:-1])/2.


def calculate_basic_trend(cube, ): #window = '8 years'):
    """
    Calculate the 8 year window trend.

    The other function may be too complicated.
    this one keeps it simler.

        xx=(1:8);
        x=[xx*0+1;xx];
        for i=1:length(time2)-7
        b=regress(amoc_anave(i:i+7)',x');
        amoc_trend_slope(i)=b(2);
        end
    """
    # Assume annual data
    annual_data = cube.data
    times = diagtools.cube_time_to_float(cube)

    slopes, intercepts, new_times = [], [], []
    for itr in range(len(cube.data) -7):
        eight_years_data = annual_data[itr:itr+8]
        eight_years_times = times[itr:itr+8]
        print(itr, len(eight_years_data))
        if len(eight_years_data) == 8:
            assert ("Not the correct number of years: "+str(len(eight_years_data)) )
        lnregs = linregress(eight_years_times, eight_years_data)
        slopes.append(lnregs[0])
        intercepts.append(lnregs[1])
        new_times.append(np.mean(eight_years_times))

    return np.array(new_times), np.array(slopes), np.array(intercepts)


def annual_mean_from_april(cube, ):
    """
    Calculate the annual mean from April-March.

    Data from January, February and March will be marked
    into the previous year.
    Args:
    * cube (:class:`iris.cube.Cube`):
        The cube containing 'coord'. The new coord will be added into
        it.
    """
    coord = cube.coord('time')
    # Define the adjustments to be made to the year.
    month_year_adjusts = [None, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    name='year_from_april'

    # Define a categorisation function.
    def _year_from_april(coord, value):
        dt = coord.units.num2date(value)
        year = dt.year
        year += month_year_adjusts[dt.month]
        return year

    # Apply the categorisation.
    iris.coord_categorisation.add_categorised_coord(cube, name, coord, _year_from_april)

    print(cube.coord('time'), cube.coord(name))
    cube = cube.aggregated_by([name, ], iris.analysis.MEAN)
    return cube


def get_26North(cube):
    """
    Extract 26.5 North. (RAPID array)
    """
    latitude = cube.coord('latitude').points
    closest_lat = np.min(np.abs(latitude - 26.5))
    cube = cube.extract(iris.Constraint(latitude=closest_lat))
    print('get_26North:',cube.data.shape)
    return cube


def get_max_amoc(cube):
    """
    Extract maximum AMOC in the profile.
    """
    cube = cube.collapsed('depth', iris.analysis.MAX)
    print('get_max_amoc:',cube.data.shape)

    return cube


def load_cube(filename, metadata):
    """
    Load cube and set up correct units, and find 26.5 N

    """
    cube = iris.load_cube(filename)
    print('load_cube',cube.data.shape, cube.coords)
    cube = diagtools.bgc_units(cube, metadata['short_name'])
    print('load_cube', cube.data.shape)
    #cube = get_26North(cube)
    return cube


def count_models(metadatas, obs_filename):
    """calculate the number of models."""
    number_models = {}
    projects = {}
    for i, filename in enumerate(sorted(metadatas)):
        metadata = metadatas[filename]
        if filename == obs_filename: continue
        number_models[metadata['dataset']] = True
        projects[metadata['project']] = True
    model_numbers = {model:i for i, model in enumerate(sorted(number_models))}
    print (number_models, model_numbers)
    number_models = len(number_models)
    return model_numbers, number_models, projects


def abline(slope, intercept):
    """Plot a line from slope and intercept"""
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, '--')

def symetric_yaxis():
    """
    Make sure the y axis is symetrics about zero.
    """
    ylim = plt.ylim()
    ymax = np.max(np.abs(ylim))
    plt.ylim([-ymax, ymax])


def make_time_series_analysis(
    cfg,
    obs=True,
    time_res="April-March",
):
    """
    Make a plot of the time series, showing the time series, the interannual
    variability and the 8 year trends of the annual mean.
    """

    savefig = True
    metadatas = diagtools.get_input_files(cfg)

    cubes = {}
    if obs:
        obs_filename = cfg['auxiliary_data_dir']+"/moc_transports.nc"
        if not os.path.exists(obs_filename):
            raise OSError("Observational data file missing. Please Download moc_transports.nc data from https://www.rapid.ac.uk/rapidmoc/rapid_data/datadl.php and put it in the auxiliary_data_dir directory: "+str(obs_filename))
        obs_dataset = "RAPID"
        variable_constraint = iris.Constraint(cube_func=(lambda c: c.var_name == 'moc_mar_hc10'))

        obs_cube = iris.load(obs_filename, constraints=variable_constraint)[0]

        iris.coord_categorisation.add_month(obs_cube, 'time', name='month')
        iris.coord_categorisation.add_year(obs_cube, 'time', name='year')
        cubes[obs_dataset] = obs_cube

    for filename in sorted(metadatas.keys()):
        dataset = metadatas[filename]['dataset']
        cube = load_cube(filename, metadatas[filename])
        cubes[dataset] = cube



    for dataset, cube in cubes.items():
        if time_res=='annual':
            cube = cube.aggregated_by(['year',], iris.analysis.MEAN)
        if time_res=="April-March":
            cube = annual_mean_from_april(cube)

        # Calculate stuff
        cubedata = np.ma.array(cube.data)
        cube.data = cubedata - cubedata.mean()
        interannual = calculate_interannual(cube)
        #slopes, intercepts = calculate_trend(cube, intersect_wanted= True, tails= False)
        new_times, slopes, intercepts = calculate_basic_trend(cube)
        times = diagtools.cube_time_to_float(cube)
        midpoint_times = calculate_midpoint(times)

        fig = plt.figure()
        fig.set_size_inches(10., 9.)
        ax = plt.subplot(311)
        plt.plot(times, np.ma.array(cube.data))
        plt.title(' '. join([time_res,'mean AMOC anomaly', '('+dataset+')']))
        plt.axhline(0., ls='--', color='k', lw=0.5)
        xlim = plt.xlim()
        symetric_yaxis()
        plt.grid()
        # ylim = plt.ylim()
        # ymax = np.max(np.abs(ylim))
        # plt.ylim([-ymax, ymax])

        ax = plt.subplot(312)
        plt.plot(midpoint_times, interannual)
        plt.title(' '. join(['Interannual variability of ',time_res, 'mean AMOC', '('+dataset+')']))
        plt.axhline(0., ls='--', color='k', lw=0.5)
        symetric_yaxis()
        plt.grid()

        ax = plt.subplot(313)
        plt.plot(new_times, slopes)
        plt.title(' '. join(['8 year trends of ', time_res, 'mean AMOC', '('+dataset+')']))
        plt.axhline(0., ls='--', color='k', lw=0.5)
        symetric_yaxis()
        plt.xlim(xlim)
        plt.grid()

        if not savefig:
            return fig, ax

        # Load image format extention and path
        image_extention = diagtools.get_image_format(cfg)
        path = cfg['plot_dir'] + '/fig_3.24_timesseriesanalysis_'+time_res+'_'+dataset+image_extention

        # Saving files:
        if cfg['write_plots']:
            logger.info('Saving plots to %s', path)
            plt.savefig(path)

        plt.close()


def make_pane_a_data_only(
        cfg,
        fig=None,
        ax=None,
        time_res='monthly',
):
    """
    Make a time series plot for the observational data.

    Parameters
    ----------
    cfg: dict
        the opened global config dictionairy, passed by ESMValTool.
    pane: string
        Which pane to produce. Either b or c.
    fig: Pyplot.figure()
        The pyplot figure
    ax: pyplot.axes
        The pyplot axes.
    time_res: str
        The time resolution, daily, monthly or annual
    Returns
    ----------
    fig: Pyplot.figure() - optional
        The pyplot figure (only returned if also provided)
    ax: pyplot.axes - optional
        The pyplot axes.  (only returned if also provided)
    """
    savefig = False
    if fig in [None,] and ax in [None,]:
        fig = plt.figure()
        fig.set_size_inches(10., 9.)
        ax = plt.subplot(111)
        savefig = True

    obs_filename = cfg['auxiliary_data_dir']+"/moc_transports.nc"
    if not os.path.exists(obs_filename):
        raise OSError("Observational data file missing. Please Download moc_transports.nc data from https://www.rapid.ac.uk/rapidmoc/rapid_data/datadl.php and put it in the auxiliary_data_dir directory: "+str(obs_filename))
    obs_dataset = "RAPID"
    variable_constraint = iris.Constraint(cube_func=(lambda c: c.var_name == 'moc_mar_hc10'))
    obs_cube = iris.load(obs_filename, constraints=variable_constraint)[0]

    iris.coord_categorisation.add_month(obs_cube, 'time', name='month')
    iris.coord_categorisation.add_year(obs_cube, 'time', name='year')
    if time_res=='monthly':
        obs_cube = obs_cube.aggregated_by(['month','year'], iris.analysis.MEAN)
    if time_res=='annual':
        obs_cube = obs_cube.aggregated_by(['year',], iris.analysis.MEAN)
    if time_res=="April-March":
        obs_cube = annual_mean_from_april(obs_cube)

    remove_anomaly = True
    if remove_anomaly:
        cubedata = np.ma.array(obs_cube.data)
        obs_cube.data = cubedata - cubedata.mean()

    #time_range = '2018'
    #if time_range=='2018':
        #print(obs_cube.coords)
        #obs_cube.data = np.ma.masked_where(obs_cube.aux_coord('year_from_april').points>=2018., obs_cube.data)
        #obs_cube.data = cubedata - cubedata.mean()

    times = diagtools.cube_time_to_float(obs_cube)
    plt.plot(times, np.ma.array(obs_cube.data))

    # Calculate slopes
    new_times, slopes, intercepts = calculate_basic_trend(obs_cube)
#    slopes, intercepts = calculate_trend(obs_cube, intersect_wanted= True)
    abline(slopes.mean(), intercepts.mean())

    # Calculate and add interannual variabillty
    variabillty = calculate_interannual(obs_cube)

    text = 'Slope: '+str(round(slopes.mean(), 3))
    text += '\nVariabillty: '+str(round(variabillty.mean(), 3))

    plt.text(0.05, 0.1, text, fontsize=10,
         horizontalalignment='left',
         verticalalignment='center',
         transform = ax.transAxes)

    # Load image format extention and path
    image_extention = diagtools.get_image_format(cfg)

    # Add title to plot
    if remove_anomaly:
        plt.title('(a) Observed AMOC anomaly at 26.5N')
        path = cfg['plot_dir'] + '/fig_3.24a_anomaly_'+time_res+image_extention

    else:
        plt.title('(a) Observed AMOC at 26.5N')
        path = cfg['plot_dir'] + '/fig_3.24a_'+time_res+image_extention


    if not savefig:
        return fig, ax

    # Saving files:
    if cfg['write_plots']:
        logger.info('Saving plots to %s', path)
        plt.savefig(path)

    plt.close()


def make_pane_a(
        cfg,
        fig=None,
        ax=None
):
    """
    Make a profile plot for an individual model.

    The optional observational dataset can also be added.

    Parameters
    ----------
    cfg: dict
        the opened global config dictionairy, passed by ESMValTool.
    pane: string
        Which pane to produce. Either b or c.
    fig: Pyplot.figure()
        The pyplot figure
    ax: pyplot.axes
        The pyplot axes.

    Returns
    ----------
    fig: Pyplot.figure() - optional
        The pyplot figure (only returned if also provided)
    ax: pyplot.axes - optional
        The pyplot axes.  (only returned if also provided)
    """
    savefig = False
    if fig in [None,] and ax in [None,]:
        fig = plt.figure()
        fig.set_size_inches(10., 9.)
        ax = plt.subplot(111)
        savefig = True

    metadatas = diagtools.get_input_files(cfg)

    obs_key = 'observational_dataset'
    obs_filename = ''
    obs_metadata = {}
    if obs_key in cfg:
        obs_filename = diagtools.match_model_to_key(obs_key,
                                                    cfg[obs_key],
                                                    metadatas)
        obs_metadata = metadatas[obs_filename]

    cubes = {}
    for filename in sorted(metadatas.keys()):
        dataset = metadatas[filename]['dataset']
        cube = load_cube(filename, metadatas[filename])
        cubes[dataset] = climate_statistics(cube, operator='mean',
                                            period='full')
    cmap = plt.cm.get_cmap('jet')

    #####
    # calculate the number of models
    model_numbers, number_models, projects= count_models(metadatas, obs_filename)

    plot_details = {}
    for filename in sorted(metadatas.keys()):
        dataset =  metadatas[filename]['dataset']
        value = float(model_numbers[dataset] ) / (number_models - 1.)

        max_index = np.argmax(cubes[dataset].data)
        print(dataset, cubes[dataset].data.shape, max_index)

        label = ' '.join([metadatas[filename]['dataset'],
                          ':',
                          '('+str(round(cubes[dataset].data[max_index] , 1)),
                          str(cubes[dataset].units)+',',
                          str(int(cubes[dataset].coord('depth').points[max_index])),
                          str(cubes[dataset].coord('depth').units)+')'
                          ])
        if filename == obs_filename:
            plot_details[obs_key] = {'c': 'black', 'ls': '-', 'lw': 2,
                                     'label': label}
        else:
            plot_details[dataset] = {'c': cmap(value),
                                     'ls': '-',
                                     'lw': 1,
                                     'label': label}
        qplt.plot(cubes[dataset], cubes[dataset].coord('depth'),
             color = plot_details[dataset]['c'],
             linewidth = plot_details[dataset]['lw'],
             linestyle = plot_details[dataset]['ls'],
             label = label
             )
        # Add a marker at the maximum
        plt.plot(cubes[dataset].data[max_index],
                 cubes[dataset].coord('depth').points[max_index],
                 c =  plot_details[dataset]['c'],
                 marker = 'd',
                 markersize = '10',
                 )

    add_obs = True
    if add_obs:
        # RAPID data from: https://www.rapid.ac.uk/rapidmoc/rapid_data/datadl.php
        # Downloaded 15/3/2019
        # The full doi for this data set is: 10.5285/5acfd143-1104-7b58-e053-6c86abc0d94b
        # moc_transports.nc: MOC vertical profiles in NetCDF format
        obs_filename = cfg['auxiliary_data_dir']+"/moc_transports.nc"
        if not os.path.exists(obs_filename):
            raise OSError("Observational data file missing. Please Download moc_transports.nc data from https://www.rapid.ac.uk/rapidmoc/rapid_data/datadl.php and put it in the auxiliary_data_dir directory: "+str(obs_filename))
        obs_dataset = "RAPID"
        variable_constraint = iris.Constraint(cube_func=(lambda c: c.var_name == 'moc_mar_hc10'))
        obs_cube = iris.load(obs_filename, constraints=variable_constraint)
        obs_cube = obs_cube.collapsed('time', iris.analysis.MEAN)
        #max_index = np.argmax(obs_cube.data)
        #print(obs_cube, max_index)
        label = ' '.join([obs_dataset,
                          ':',
                          '('+str(round(obs_cube.data[max_index] , 1)),
                          str(obs_cube.units)+',',
                          str(int(obs_cube.coord('depth').points[max_index])),
                          str(obs_cube.coord('depth').units)+')'
                          ])

        plot_details[obs_dataset] = {'c': 'black',
                                 'ls': '-',
                                 'lw': 1,
                                 'label': label}

        qplt.plot(obs_cube, obs_cube.coord('depth'),
            color = plot_details[obs_dataset]['c'],
            linewidth = plot_details[obs_dataset]['lw'],
            linestyle = plot_details[obs_dataset]['ls'],
            label = label
            )

        # Add a marker at the maximum
        plt.plot(obs_cube.data[max_index],
                 obs_cube.coord('depth').points[max_index],
                 c =  plot_details[obs_dataset]['c'],
                 marker = 'd',
                 markersize = '10',
                 )

    # Add title to plot
    # title = ' '.join([
    #     metadata['dataset'],
    #     metadata['long_name'],
    # ])
    # plt.title(title)
    plt.title('(a) AMOC streamfunction profiles at 26.5N')

    # Add Legend outside right.
    # diagtools.add_legend_outside_right(plot_details, plt.gca())
    leg = plt.legend(loc='lower right', prop={'size':6})
    leg.draw_frame(False)
    leg.get_frame().set_alpha(0.)

    if not savefig:
        return fig, ax

    # Load image format extention and path
    image_extention = diagtools.get_image_format(cfg)
    path = cfg['plot_dir'] + '/fig_3.24a'+image_extention

    # Saving files:
    if cfg['write_plots']:
        logger.info('Saving plots to %s', path)
        plt.savefig(path)

    plt.close()


def make_pane_bc(
        cfg,
        pane = 'b',
        fig=None,
        ax=None,
        timeseries = False,
        time_res="April-March",
):
    """
    Make a box and whiskers plot for panes b and c.

    If a figure and axes are not provided, if will save the pane as it's own
    image, otherwise it returns the fig and ax.

    Parameters
    ----------
    cfg: dict
        the opened global config dictionairy, passed by ESMValTool.
    pane: string
        Which pane to produce. Either b or c.
    fig: Pyplot.figure()
        The pyplot figure
    ax: pyplot.axes
        The pyplot axes.

    Returns
    ----------
    fig: Pyplot.figure() - optional
        The pyplot figure (only returned if also provided)
    ax: pyplot.axes - optional
        The pyplot axes.  (only returned if also provided)
    """
    savefig = False
    if fig in [None,] and ax in [None,]:
        fig = plt.figure()
        fig.set_size_inches(10., 9.)
        ax = plt.subplot(1, 1, 1)
        savefig = True

    metadatas = diagtools.get_input_files(cfg)

    #####
    # Load the CMIP data and calculate the trend or interannual variability
    trends = {}
    for filename in sorted(metadatas.keys()):
        dataset = metadatas[filename]['dataset']
        cube = load_cube(filename, metadatas[filename])
        print (cube.data.shape)
        if time_res=='monthly':
            cube = cube.aggregated_by(['month','year'], iris.analysis.MEAN)
        if time_res=='annual':
            cube = cube.aggregated_by(['year',], iris.analysis.MEAN)
        if time_res=="April-March":
            cube = annual_mean_from_april(cube)

        if pane == 'b':
            #cube = get_max_amoc(cube)
            new_times, slopes, intercepts = calculate_basic_trend(cube)
            trends[dataset] = slopes
        if pane == 'c':
            #cube = get_max_amoc(cube)
            trends[dataset] = calculate_interannual(cube)

    #####
    # Add observational data.
    add_obs = True
    if add_obs:
        # RAPID data from: https://www.rapid.ac.uk/rapidmoc/rapid_data/datadl.php
        # Downloaded 15/3/2019
        # The full doi for this data set is: 10.5285/5acfd143-1104-7b58-e053-6c86abc0d94b
        # moc_transports.nc: MOC vertical profiles in NetCDF format
        obs_filename = cfg['auxiliary_data_dir']+"/moc_transports.nc"
        obs_dataset = "RAPID"
        variable_constraint = iris.Constraint(cube_func=(lambda c: c.var_name == 'moc_mar_hc10'))
        obs_cube = iris.load(obs_filename, constraints=variable_constraint)[0]
        iris.coord_categorisation.add_month(obs_cube, 'time', name='month')
        iris.coord_categorisation.add_year(obs_cube, 'time', name='year')
        #obs_cube = obs_cube.aggregated_by(['month','year'], iris.analysis.MEAN)
        if time_res=="April-March":
            obs_cube = annual_mean_from_april(obs_cube)
        if time_res=='monthly':
            obs_cube = obs_cube.aggregated_by(['month','year'], iris.analysis.MEAN)
        if time_res=='annual':
            obs_cube = obs_cube.aggregated_by(['year',], iris.analysis.MEAN)

        if pane == 'b':
            #obs_cube = get_max_amoc(obs_cube)
            new_times, slopes, intercepts = calculate_basic_trend(obs_cube)
            trends[obs_dataset] = slopes
        if pane == 'c':
            #obs_cube = get_max_amoc(obs_cube)
            trends[obs_dataset] = calculate_interannual(obs_cube)

    #####
    # calculate the number of models
    model_numbers, number_models, projects= count_models(metadatas, obs_filename)

    if timeseries:
        # Draw the trend/variability as a time series
        cmap = plt.cm.get_cmap('jet')
        for dataset in sorted(trends):
            print(dataset, trends[dataset])
            try:
                value = float(model_numbers[dataset] ) / (number_models - 1.)
                color = cmap(value)
                lw = 1.
            except:
                color = 'black'
                lw = 2.5
            plt.plot(trends[dataset], c = color, lw=lw, label = dataset)
    else:
        # Draw the trend/variability as a box and whisker diagram.
        box_data = [trends[dataset] for dataset in sorted(trends)]
        box = ax.boxplot(box_data,
                         0,
                         sym = 'k.',
                         whis = [1, 99],
                         showmeans= False,
                         meanline = False,
                         showfliers = True,
                         labels = sorted(trends.keys()))
        plt.xticks(rotation=30, ha="right")
        plt.setp(box['fliers'], markersize=1.0)

    if savefig:
        plt.subplots_adjust(bottom=0.25)

    # pane specific stuff
    if pane == 'b':
        plt.title('(b) Distribution of 8 year AMOC trends')
        plt.axhline(-0.53, c='k', lw=8, alpha=0.1, zorder = 0) # Wrong numbers!
        plt.ylabel('Sv yr'+r'$^{-1}$')
        if not savefig:
            plt.setp( ax.get_xticklabels(), visible=False)

    if pane == 'c':
        plt.title('(c) Distribution of interannual AMOC changes')
        plt.axhline(-4.4, c='k', lw=8, alpha=0.1, zorder = 0) # wrong numbers!
        plt.ylabel('Sv')

    # If putting all the panes in one figure, return them now.
    if not savefig:
        return fig, ax
   # Save the pane as its own image.


    plt.axhline(0., ls='--', color='k', lw=0.5)
    if timeseries:
        plt.legend()

    # Load image format extention and path
    image_extention = diagtools.get_image_format(cfg)
    if timeseries:
        path = cfg['plot_dir'] + '/fig_3.24_'+pane+'_timeseries_'+time_res+image_extention
    else:
        path = cfg['plot_dir'] + '/fig_3.24_'+pane+'_'+time_res+image_extention

    # Saving files:
    if cfg['write_plots']:
        logger.info('Saving plots to %s', path)
        plt.savefig(path)

    plt.close()


def  make_figure(cfg, debug=False, timeseries=False):
    """
    Make the entire figure.

    Parameters
    ----------
    cfg: dict
        the opened global config dictionairy, passed by ESMValTool.

    """
    fig = plt.figure()
    fig.set_size_inches(w=11,h=9)
    #gs1 = gridspec.GridSpec(2,5)

    # fig.subplots_adjust(wspace=0.25, hspace=0.1)

    #axa = plt.subplot2grid((2,5), (0,0), colspan=2, rowspan=2)
    axa = plt.subplot(311)
    fig, axa = make_pane_a_data_only(cfg, fig=fig, ax=axa)

    #axb = plt.subplot2grid((2,5), (0,2), colspan=3, rowspan=1)
    axb = plt.subplot(312)
    fig, axb = make_pane_bc(cfg, pane='b', fig=fig, ax=axb, timeseries=timeseries)

    #axc = plt.subplot2grid((2,5), (1,2), colspan=3, rowspan=1)
    axc = plt.subplot(313)
    fig, axc = make_pane_bc(cfg, pane='c', fig=fig, ax=axc, timeseries=timeseries)

    #plt.subplots_adjust(bottom=0.2, wspace=0.4, hspace=0.2)

    # Load image format extention and path
    image_extention = diagtools.get_image_format(cfg)
    if timeseries:
        path = cfg['plot_dir'] + '/fig_3.24_timeseries'+image_extention
    else:
        path = cfg['plot_dir'] + '/fig_3.24'+image_extention

    # Watermark
    # fig.text(0.95, 0.05, 'Draft',
    #          fontsize=50, color='gray',
    #          ha='right', va='bottom', alpha=0.5)

    # Saving files:
    if cfg['write_plots']:
        logger.info('Saving plots to %s', path)
        plt.savefig(path)

    plt.close()



def main(cfg):
    """
    Run the diagnostics profile tool.

    Load the config file, find an observational dataset filename,
    pass loaded into the plot making tool.

    Parameters
    ----------
    cfg: dict
        the opened global config dictionairy, passed by ESMValTool.

    """
    make_pane_a(cfg)
    # overall plots:
    make_figure(cfg, timeseries= True)
    make_figure(cfg, timeseries= False)
    return

    # individual plots:
    # make_timeseriespane_bc(cfg, pane='b')
    # make_timeseriespane_bc(cfg, pane='c')
    # make_pane_bc(cfg, pane='c', timeseries=False)
    # make_pane_bc(cfg, pane='b', timeseries=False)
    #make_pane_a_data_only(cfg, time_res="daily")
    #make_pane_a_data_only(cfg, time_res="monthly")
    make_time_series_analysis(cfg, obs=True)
    # make_pane_a_data_only(cfg, time_res="annual")
    make_pane_a_data_only(cfg, time_res="April-March")

    make_pane_bc(cfg, pane='c', time_res="April-March")
    make_pane_bc(cfg, pane='b',time_res="April-March")
    make_pane_bc(cfg, pane='c', time_res="annual")
    make_pane_bc(cfg, pane='b',time_res="annual")

    #




    logger.info('Success')


if __name__ == '__main__':
    with run_diagnostic() as config:
        main(config)
