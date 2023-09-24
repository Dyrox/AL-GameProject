import pstats

p = pstats.Stats('profile_results.prof')
p.sort_stats('cumulative').print_stats(20)  # This will sort by cumulative time and print the top 10 functions.
