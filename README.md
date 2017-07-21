# bark-extra

Scripts for wrangling data into [Bark](https://github.com/kylerbrown/bark)-usable shape.

Every script should provide usage info via the `-h` argument.

## scripts

+ `add_units`: adds `units` attribute to ARF file datasets to allow proper Bark conversation
+ `check_valid_intervals`: ensures that stop is after start for each interval in a Bark event dataset, and swaps them if not
+ `combine_events`: combines two Bark event datasets
+ `float_to_int`: uses SOX to convert float-encoded Bark sampled datasets to integer encoding (useful for JILL outputs)
+ `gen_stim_times`: combines JILL jstim log and Intan eval board ADC inputs to make a Bark event dataset containing stimulus times and identities
+ `pull_times`: summarizes Bark entries in a root by hour of day
+ `remove_empty_csvs`: removes .csv files which do not meet length criteria
+ `remove_extra_intro_notes`: removes intro notes from Bark event datasets that occur far away from song
+ `winnow_entries`: removes all entries in a given root for which a specified event dataset is empty (useful to tidy up roots with lots of useless entries)
