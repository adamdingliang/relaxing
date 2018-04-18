#!/usr/bin/env python3
"""
This script calculate stats for different analysis types (tartan runs).
"""

import sys
import argparse
import pandas as pd
import matplotlib.pyplot as plt


def main():
    """ Handles arguments and invokes the driver function.
    """
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-a', '--anls-type', metavar='STR', required=True, help='Analysis type')
    parser.add_argument('-t', '--target-name', metavar='STR', required=True, help='Target name (CHIPSEQ, WHOLE_GENOME, TRANSCRIPTOME, EXOME)')
    parser.add_argument('-ad', '--after-date', metavar='STR', help='Calculate stats using data created after a given date (YYYY-MM-DD)')
    parser.add_argument('-bd', '--before-date', metavar='STR', help='Calculate stats using data created before a given date (YYYY-MM-DD)')
    parser.add_argument('-i', '--input-dir', metavar='STR', help='Input directory')
    parser.add_argument('-o', '--output-dir', metavar='STR', help='Output directory')
    parser.add_argument('--dry-run', help='enable dry-run mode.', action='store_true')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args()

    targets = ['CHIPSEQ', 'WHOLE_GENOME', 'TRANSCRIPTOME', 'EXOME']
    if args.target_name not in targets:
        sys.exit('Error - invalid target name: ' + args.target_name)

    anls_run_time_stat(args.anls_type, args.target_name, args.before_date, args.after_date)
    return


def anls_run_time_stat(anls_type, target, before_date, after_date):
    """ Summarize analysis run time statistics
    Args:
        anls_type (str): analysis type
        target (str): target name
        before_date (str): Calculate stats using data created before a given date
        after_date (str): calculate stats using data created after a given date
    Return:
        None
    """
    csv_file = '{}.csv'.format(anls_type)
    df = pd.read_csv(csv_file, sep='\t')

    # Convert all chipseq targets to CHIPSEQ
    new_target_names = []
    for ta in df.loc[:, ('target_name')]:
        if ta.find(target) != -1:
            new_target_names.append(target)
        else:
            new_target_names.append(ta)

    # Only keep date, ignore hours, seconds, etc
    new_dates = []
    for date in df.loc[:, ('begin_date')]:
        new_dates.append(date.split()[0])

    # Convert duration unit from second to hour
    hour_duration = []
    for duration in df.loc[:, ('duration')]:
        hour_duration.append(float(duration) / 3600.0)
    temp_df = pd.DataFrame({'target_name': new_target_names, 'begin_date': new_dates, 'duration': hour_duration})
    df.update(temp_df)

    # Group by begin_date and take the mean of duration
    df_target = df[df.loc[:, ('target_name')] == target]
    target_bd_df = df_target.groupby(['begin_date']).mean()
    sorted_target_bd_df = target_bd_df.sort_index(level=1)

    # Select rows after a given date
    start_index = 1
    if after_date:
        for index, date in enumerate(sorted_target_bd_df.index.values):
            if date > after_date:
                start_index = index
                break
    end_index = sorted_target_bd_df.shape[0]
    if before_date:
        for index, date in enumerate(sorted_target_bd_df.index.values):
            if date > before_date:
                end_index = index
                break
    selected_bd_df = sorted_target_bd_df.iloc[range(start_index, end_index)]

    # Output stats to file
    mean_str = 'mean: ' + str(round(selected_bd_df.loc[:, ('duration')].mean(), 2)) + ' hours'
    std_str = 'std: ' + str(round(selected_bd_df.loc[:, ('duration')].std(), 2)) + ' hours'
    with open('{}_{}.txt'.format(anls_type, target), 'w') as fout:
        fout.write('Without filtering outliers\n')
        fout.write(mean_str + '\n')
        fout.write(std_str + '\n\n')

    # Make a box plot
    #color = dict(boxes='DarkGreen', whiskers='DarkOrange', medians='DarkBlue', caps='Gray')
    #pl = selected_bd_df.plot.box(showfliers=False, return_type='both', color=color, sym='r+')
    pl = selected_bd_df.boxplot(showfliers=False, return_type='both')
    cap_low = pl.lines['caps'][0].get_ydata(orig=True)[0]
    cap_high = pl.lines['caps'][1].get_ydata(orig=True)[0]
    plt.savefig('{}_{}_boxplot.png'.format(anls_type, target))

    # Define outlier using box plot
    selected_bd_df.loc[:, ('outlier_high')] = selected_bd_df.loc[:, ('duration')] > cap_high
    selected_bd_df.loc[:, ('outlier_low')] = selected_bd_df.loc[:, ('duration')] < cap_low

    # Define outlier using Z-score
    #selected_bd_df.loc[:, ('outlier_high')] = abs(selected_bd_df.loc[:, ('duration')] \
    #    - selected_bd_df.loc[:, ('duration')].mean()) > 1.96 * selected_bd_df.loc[:, ('duration')].std()

    # Filter outlier
    selected_bd_df = selected_bd_df[selected_bd_df['outlier_high'] == False]
    selected_bd_df = selected_bd_df[selected_bd_df['outlier_low'] == False]

    # Output stats to file
    mean_str = 'mean: ' + str(round(selected_bd_df.loc[:, ('duration')].mean(), 2)) + ' hours'
    std_str = 'std: ' + str(round(selected_bd_df.loc[:, ('duration')].std(), 2)) + ' hours'
    with open('{}_{}.txt'.format(anls_type, target), 'a') as fout:
        fout.write('After filtering outliers\n')
        fout.write(mean_str + '\n')
        fout.write(std_str)

    # Plot distribution
    xticks = range(1, selected_bd_df.shape[0], int((selected_bd_df.shape[0]-1)/5))
    pl = selected_bd_df.loc[:, ('duration')].plot(y='seconds', xticks=xticks)
    pl.set(title='{} {} run time distribution'.format(target, anls_type), ylabel='Hour', xlabel='Begin Date')
    #max_duration = int(sorted_chip_no_outlier_df.max(axis=0)['duration'])
    #x_pos = int(selected_bd_df.shape[0] * 0.70)
    #pl.text(x_pos, max_duration, mean_str)
    #pl.text(x_pos, max_duration * 0.95, std_str)
    plt.savefig('{}_{}_distribution.png'.format(anls_type, target))

    print('Done', file=sys.stderr)
    return


if __name__ == '__main__':
    main()
